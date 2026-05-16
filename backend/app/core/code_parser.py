"""Code parsing module using Tree-sitter."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    """Function information."""
    name: str
    line_start: int
    line_end: int
    signature: str
    calls: List[str] = field(default_factory=list)
    complexity: int = 1


@dataclass
class ClassInfo:
    """Class information."""
    name: str
    line_start: int
    line_end: int
    methods: List[str] = field(default_factory=list)
    inherits_from: List[str] = field(default_factory=list)


@dataclass
class ImportInfo:
    """Import information."""
    module: str
    names: List[str] = field(default_factory=list)
    is_relative: bool = False


@dataclass
class ParseResult:
    """Parse result for a file."""
    file_path: str
    language: str
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    total_lines: int = 0


class CodeParser:
    """Code parser using Tree-sitter."""
    
    def __init__(self):
        """Initialize code parser."""
        self._parsers: Dict[str, any] = {}
        self._supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.kt': 'kotlin',
            '.kts': 'kotlin',
            '.xml': 'xml',
            '.gradle': 'gradle',
            '.go': 'go',
            '.rs': 'rust',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
        }
    
    def _get_language(self, file_path: str) -> Optional[str]:
        """Get language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self._supported_languages.get(ext)
    
    def _get_parser(self, language: str):
        """Get or create Tree-sitter parser for language."""
        if language not in self._parsers:
            try:
                from tree_sitter import Language, Parser
                
                # Try to import language-specific parsers
                if language == 'python':
                    import tree_sitter_python as tspython
                    lang = Language(tspython.language())
                elif language == 'javascript':
                    import tree_sitter_javascript as tsjavascript
                    lang = Language(tsjavascript.language())
                elif language == 'typescript':
                    import tree_sitter_typescript as tstypescript
                    lang = Language(tstypescript.language_typescript())
                elif language == 'java':
                    import tree_sitter_java as tsjava
                    lang = Language(tsjava.language())
                elif language == 'go':
                    import tree_sitter_go as tsgo
                    lang = Language(tsgo.language())
                else:
                    logger.warning(f"Language {language} not supported by Tree-sitter")
                    return None
                
                parser = Parser(lang)
                self._parsers[language] = parser
                
            except ImportError as e:
                logger.warning(f"Tree-sitter language package not available: {e}")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize parser for {language}: {e}")
                return None
        
        return self._parsers.get(language)
    
    def parse_file(self, file_path: str, content: Optional[str] = None) -> ParseResult:
        """Parse a single file.
        
        Args:
            file_path: Path to the file
            content: Optional file content (if None, reads from disk)
            
        Returns:
            ParseResult with extracted information
        """
        language = self._get_language(file_path)
        
        if not language:
            return ParseResult(file_path=file_path, language="unknown")
        
        # Read file content if not provided
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")
                return ParseResult(file_path=file_path, language=language)
        
        # Get parser
        parser = self._get_parser(language)
        
        if not parser:
            # Fallback: basic parsing without Tree-sitter
            return self._parse_fallback(file_path, language, content)
        
        try:
            # Parse with Tree-sitter
            tree = parser.parse(bytes(content, 'utf8'))
            root_node = tree.root_node
            
            result = ParseResult(
                file_path=file_path,
                language=language,
                total_lines=len(content.splitlines()),
            )
            
            # Extract based on language
            if language == 'python':
                self._parse_python(root_node, content, result)
            elif language in ['javascript', 'typescript']:
                self._parse_javascript(root_node, content, result)
            elif language == 'java':
                self._parse_java(root_node, content, result)
            elif language == 'go':
                self._parse_go(root_node, content, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return self._parse_fallback(file_path, language, content)
    
    def _parse_fallback(self, file_path: str, language: str, content: str) -> ParseResult:
        """Fallback parsing using regex for basic info."""
        import re
        
        result = ParseResult(
            file_path=file_path,
            language=language,
            total_lines=len(content.splitlines()),
        )
        
        # Extract imports (basic regex)
        if language == 'python':
            import_pattern = r'^(?:from\s+(\S+)\s+import|import\s+(\S+))'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                module = match.group(1) or match.group(2)
                if module:
                    result.imports.append(ImportInfo(module=module))
        elif language in ['kotlin', 'java']:
            import_pattern = r'^\s*import\s+([\w.*]+)'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                result.imports.append(ImportInfo(module=match.group(1)))
        elif language in ['javascript', 'typescript']:
            import_pattern = r'^\s*import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]|^\s*import\s+[\'"]([^\'"]+)[\'"]'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                module = match.group(1) or match.group(2)
                if module:
                    result.imports.append(ImportInfo(module=module))
        
        # Extract function definitions (basic)
        func_patterns = [
            r'^\s*(?:def|function|func)\s+(\w+)',
            r'^\s*(?:public|private|protected|internal|override|suspend|static|\s)*\s*fun\s+(\w+)',
            r'^\s*(?:public|private|protected|static|final|abstract|synchronized|\s)*[\w<>\[\], ?]+\s+(\w+)\s*\([^;{}]*\)\s*\{',
        ]
        seen_functions = set()
        for func_pattern in func_patterns:
            for match in re.finditer(func_pattern, content, re.MULTILINE):
                name = match.group(1)
                if name in seen_functions or name in {'if', 'for', 'while', 'switch', 'catch'}:
                    continue
                seen_functions.add(name)
                line_num = content[:match.start()].count('\n') + 1
                result.functions.append(FunctionInfo(
                    name=name,
                    line_start=line_num,
                    line_end=line_num + 10,
                    signature=match.group(0).strip(),
                ))

        class_pattern = r'^\s*(?:data\s+|sealed\s+|enum\s+)?(?:class|interface|object)\s+(\w+)'
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            line_num = content[:match.start()].count('\n') + 1
            result.classes.append(ClassInfo(
                name=match.group(1),
                line_start=line_num,
                line_end=line_num + 30,
            ))
        
        return result
    
    def _parse_python(self, root_node, content: str, result: ParseResult):
        """Parse Python AST."""
        import re
        
        def walk_tree(node, depth=0):
            # Function definitions
            if node.type == 'function_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    
                    # Get signature
                    params_node = node.child_by_field_name('parameters')
                    signature = f"def {name}("
                    if params_node:
                        params = content[params_node.start_byte:params_node.end_byte]
                        signature += params[1:-1]  # Remove parens
                    signature += ")"
                    
                    result.functions.append(FunctionInfo(
                        name=name,
                        line_start=node.start_point[0] + 1,
                        line_end=node.end_point[0] + 1,
                        signature=signature,
                    ))
            
            # Class definitions
            elif node.type == 'class_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    
                    # Get inheritance
                    bases_node = node.child_by_field_name('superclasses')
                    inherits = []
                    if bases_node:
                        bases_text = content[bases_node.start_byte:bases_node.end_byte]
                        inherits = [b.strip() for b in re.findall(r'(\w+)', bases_text)]
                    
                    result.classes.append(ClassInfo(
                        name=name,
                        line_start=node.start_point[0] + 1,
                        line_end=node.end_point[0] + 1,
                        inherits_from=inherits,
                    ))
            
            # Import statements
            elif node.type in ['import_statement', 'import_from_statement']:
                text = content[node.start_byte:node.end_byte]
                
                # from X import Y
                if node.type == 'import_from_statement':
                    module_node = node.child_by_field_name('module_name')
                    if module_node:
                        module = content[module_node.start_byte:module_node.end_byte]
                        result.imports.append(ImportInfo(module=module))
                else:
                    # import X
                    names = re.findall(r'import\s+([\w,\s]+)', text)
                    if names:
                        for name in names[0].split(','):
                            result.imports.append(ImportInfo(module=name.strip()))
            
            # Recurse
            for child in node.children:
                walk_tree(child, depth + 1)
        
        walk_tree(root_node)
    
    def _parse_javascript(self, root_node, content: str, result: ParseResult):
        """Parse JavaScript/TypeScript AST."""
        def walk_tree(node):
            # Function declarations
            if node.type in ['function_declaration', 'function', 'arrow_function']:
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    result.functions.append(FunctionInfo(
                        name=name,
                        line_start=node.start_point[0] + 1,
                        line_end=node.end_point[0] + 1,
                        signature=f"function {name}()",
                    ))
            
            # Class declarations
            elif node.type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    result.classes.append(ClassInfo(
                        name=name,
                        line_start=node.start_point[0] + 1,
                        line_end=node.end_point[0] + 1,
                    ))
            
            # Import statements
            elif node.type == 'import_statement':
                text = content[node.start_byte:node.end_byte]
                result.imports.append(ImportInfo(module=text))
            
            # Recurse
            for child in node.children:
                walk_tree(child)
        
        walk_tree(root_node)
    
    def _parse_java(self, root_node, content: str, result: ParseResult):
        """Parse Java AST."""
        def walk_tree(node):
            if node.type == 'method_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    result.functions.append(FunctionInfo(
                        name=name,
                        line_start=node.start_point[0] + 1,
                        line_end=node.end_point[0] + 1,
                        signature=f"void {name}()",
                    ))
            
            elif node.type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    result.classes.append(ClassInfo(
                        name=name,
                        line_start=node.start_point[0] + 1,
                        line_end=node.end_point[0] + 1,
                    ))
            
            for child in node.children:
                walk_tree(child)
        
        walk_tree(root_node)
    
    def _parse_go(self, root_node, content: str, result: ParseResult):
        """Parse Go AST."""
        def walk_tree(node):
            if node.type == 'function_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = content[name_node.start_byte:name_node.end_byte]
                    result.functions.append(FunctionInfo(
                        name=name,
                        line_start=node.start_point[0] + 1,
                        line_end=node.end_point[0] + 1,
                        signature=f"func {name}()",
                    ))
            
            for child in node.children:
                walk_tree(child)
        
        walk_tree(root_node)
    
    def parse_directory(self, directory: str, extensions: Optional[Set[str]] = None) -> List[ParseResult]:
        """Parse all files in a directory.
        
        Args:
            directory: Directory path
            extensions: Optional set of file extensions to parse
            
        Returns:
            List of ParseResults
        """
        if extensions is None:
            extensions = set(self._supported_languages.keys())
        
        results = []
        directory_path = Path(directory)
        
        for ext in extensions:
            for file_path in directory_path.rglob(f"*{ext}"):
                if '.git' in str(file_path):
                    continue
                if 'node_modules' in str(file_path):
                    continue
                if '__pycache__' in str(file_path):
                    continue
                
                result = self.parse_file(str(file_path))
                results.append(result)
        
        logger.info(f"Parsed {len(results)} files from {directory}")
        return results


# Singleton instance
code_parser = CodeParser()
