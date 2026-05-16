"""Impact analysis engine using NetworkX."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx

from app.core.code_parser import ImportInfo, ParseResult

logger = logging.getLogger(__name__)


@dataclass
class ImpactResult:
    """Result of impact analysis."""
    primary_files: Set[str] = field(default_factory=set)
    secondary_files: Set[str] = field(default_factory=set)
    tertiary_files: Set[str] = field(default_factory=set)
    affected_functions: Set[str] = field(default_factory=set)
    affected_classes: Set[str] = field(default_factory=set)
    entry_points: Set[str] = field(default_factory=set)
    tests_affected: Set[str] = field(default_factory=set)


class ImpactEngine:
    """Impact analysis engine using NetworkX graphs."""
    
    def __init__(self):
        """Initialize impact engine."""
        self._graph = nx.DiGraph()
        self._file_graph = nx.DiGraph()
    
    def build_dependency_graph(self, parse_results: List[ParseResult]) -> nx.DiGraph:
        """Build dependency graph from parse results.
        
        Args:
            parse_results: List of file parse results
            
        Returns:
            NetworkX directed graph
        """
        self._graph = nx.DiGraph()
        self._file_graph = nx.DiGraph()
        
        # First pass: add all nodes
        for result in parse_results:
            # Add file node
            self._graph.add_node(
                result.file_path,
                node_type="file",
                language=result.language,
            )
            self._file_graph.add_node(result.file_path)
            
            # Add function nodes
            for func in result.functions:
                node_id = f"{result.file_path}::{func.name}"
                self._graph.add_node(
                    node_id,
                    node_type="function",
                    file_path=result.file_path,
                    line_start=func.line_start,
                    line_end=func.line_end,
                    signature=func.signature,
                )
                # Connect file to function
                self._graph.add_edge(result.file_path, node_id, edge_type="contains")
            
            # Add class nodes
            for cls in result.classes:
                node_id = f"{result.file_path}::{cls.name}"
                self._graph.add_node(
                    node_id,
                    node_type="class",
                    file_path=result.file_path,
                    line_start=cls.line_start,
                    line_end=cls.line_end,
                    methods=cls.methods,
                )
                self._graph.add_edge(result.file_path, node_id, edge_type="contains")
        
        # Second pass: add edges
        for result in parse_results:
            # Add import edges
            for imp in result.imports:
                target_file = self._resolve_import(imp, parse_results)
                if target_file:
                    self._graph.add_edge(
                        result.file_path,
                        target_file,
                        edge_type="imports",
                        import_names=imp.names,
                    )
                    self._file_graph.add_edge(result.file_path, target_file)
            
            # Add function call edges
            for func in result.functions:
                func_node = f"{result.file_path}::{func.name}"
                for called_func in func.calls:
                    target = self._resolve_function_call(called_func, parse_results)
                    if target:
                        self._graph.add_edge(func_node, target, edge_type="calls")
            
            # Add inheritance edges
            for cls in result.classes:
                class_node = f"{result.file_path}::{cls.name}"
                for parent in cls.inherits_from:
                    parent_node = self._resolve_class(parent, parse_results)
                    if parent_node:
                        self._graph.add_edge(class_node, parent_node, edge_type="inherits")
        
        logger.info(
            f"Built dependency graph: {self._graph.number_of_nodes()} nodes, "
            f"{self._graph.number_of_edges()} edges"
        )
        
        return self._graph
    
    def _resolve_import(
        self,
        imp: ImportInfo,
        parse_results: List[ParseResult],
    ) -> Optional[str]:
        """Resolve an import to a file path."""
        module_parts = imp.module.split(".")
        
        for result in parse_results:
            path = Path(result.file_path)
            
            # Try to match module path
            for i in range(len(module_parts)):
                potential_path = "/".join(module_parts[i:])
                if potential_path in result.file_path.replace("\\", "/"):
                    return result.file_path
                
                # Try with extensions
                for ext in [".py", ".js", ".ts", ".java", ".go"]:
                    if potential_path + ext in result.file_path.replace("\\", "/"):
                        return result.file_path
        
        return None
    
    def _resolve_function_call(
        self,
        func_name: str,
        parse_results: List[ParseResult],
    ) -> Optional[str]:
        """Resolve a function call to a node ID."""
        for result in parse_results:
            for func in result.functions:
                if func.name == func_name:
                    return f"{result.file_path}::{func.name}"
        return None
    
    def _resolve_class(
        self,
        class_name: str,
        parse_results: List[ParseResult],
    ) -> Optional[str]:
        """Resolve a class reference to a node ID."""
        for result in parse_results:
            for cls in result.classes:
                if cls.name == class_name:
                    return f"{result.file_path}::{cls.name}"
        return None
    
    def analyze_impact(
        self,
        changed_files: List[str],
        entry_points: Optional[List[str]] = None,
    ) -> ImpactResult:
        """Analyze impact of changes to files.
        
        Args:
            changed_files: List of files being changed
            entry_points: Optional list of entry point files
            
        Returns:
            ImpactResult with affected components
        """
        result = ImpactResult()
        
        # Primary impact: directly changed files
        result.primary_files = set(changed_files)
        
        # Get all functions/classes in changed files
        for file_path in changed_files:
            for node, attrs in self._graph.nodes(data=True):
                if attrs.get("file_path") == file_path:
                    node_type = attrs.get("node_type")
                    if node_type == "function":
                        result.affected_functions.add(node)
                    elif node_type == "class":
                        result.affected_classes.add(node)
            
            # Check if this is a test file
            if self._is_test_file(file_path):
                result.tests_affected.add(file_path)
        
        # Secondary impact: files that depend on changed files
        for file_path in changed_files:
            # Find files that import this file
            if file_path in self._file_graph:
                dependents = nx.ancestors(self._file_graph, file_path)
                result.secondary_files.update(dependents)
        
        # Remove primary from secondary
        result.secondary_files -= result.primary_files
        
        # Tertiary impact: transitive dependencies
        for secondary in list(result.secondary_files):
            if secondary in self._file_graph:
                dependents = nx.ancestors(self._file_graph, secondary)
                result.tertiary_files.update(dependents)
        
        # Remove primary and secondary from tertiary
        result.tertiary_files -= result.primary_files
        result.tertiary_files -= result.secondary_files
        
        # Identify entry points
        if entry_points:
            result.entry_points = set(entry_points) & (
                result.primary_files | result.secondary_files | result.tertiary_files
            )
        else:
            # Guess entry points: files not imported by others (except main/entry files)
            result.entry_points = self._identify_entry_points(result)
        
        # Find affected tests
        result.tests_affected = self._find_affected_tests(result)
        
        return result
    
    def _is_test_file(self, file_path: str) -> bool:
        """Check if a file is a test file."""
        test_patterns = [
            "test_",
            "_test.",
            "_spec.",
            ".test.",
            "/tests/",
            "/test/",
            "__tests__/",
        ]
        return any(pattern in file_path for pattern in test_patterns)
    
    def _identify_entry_points(self, impact: ImpactResult) -> Set[str]:
        """Identify entry point files from affected files."""
        entry_points = set()
        all_affected = impact.primary_files | impact.secondary_files | impact.tertiary_files
        
        for file_path in all_affected:
            # Check common entry point patterns
            path = Path(file_path)
            name = path.name.lower()
            
            if name in ["main.py", "main.js", "main.ts", "main.go", "main.java", 
                       "index.js", "index.ts", "app.py", "server.py", "server.js"]:
                entry_points.add(file_path)
                continue
            
            # Check if file has no incoming imports (might be entry point)
            if file_path in self._file_graph:
                predecessors = list(self._file_graph.predecessors(file_path))
                if not predecessors:
                    entry_points.add(file_path)
        
        return entry_points
    
    def _find_affected_tests(self, impact: ImpactResult) -> Set[str]:
        """Find tests that cover affected functionality."""
        tests = set()
        
        # Find all test files
        for node, attrs in self._graph.nodes(data=True):
            node_type = attrs.get("node_type")
            if node_type == "file" and self._is_test_file(node):
                # Check if this test file imports any affected files
                if node in self._file_graph:
                    imports = nx.descendants(self._file_graph, node)
                    
                    affected = (
                        impact.primary_files | 
                        impact.secondary_files | 
                        impact.tertiary_files
                    )
                    
                    if imports & affected:
                        tests.add(node)
        
        return tests
    
    def calculate_impact_metrics(
        self,
        impact: ImpactResult,
        total_files: int,
    ) -> Dict[str, any]:
        """Calculate impact metrics.
        
        Args:
            impact: Impact result
            total_files: Total number of files in repository
            
        Returns:
            Dictionary of metrics
        """
        total_affected = (
            len(impact.primary_files) +
            len(impact.secondary_files) +
            len(impact.tertiary_files)
        )
        
        percentage = (total_affected / total_files * 100) if total_files > 0 else 0
        
        # Determine category
        if percentage < 1:
            category = "small"
        elif percentage < 10:
            category = "medium"
        else:
            category = "large"
        
        return {
            "files_affected": total_affected,
            "files_direct": len(impact.primary_files),
            "files_indirect": len(impact.secondary_files) + len(impact.tertiary_files),
            "functions_affected": len(impact.affected_functions),
            "classes_affected": len(impact.affected_classes),
            "tests_affected": len(impact.tests_affected),
            "percentage_of_codebase": round(percentage, 2),
            "category": category,
        }
    
    def get_graph_data(self) -> Dict:
        """Get graph data for serialization.
        
        Returns:
            Dictionary with nodes and edges
        """
        nodes = []
        for node_id, attrs in self._graph.nodes(data=True):
            node_data = {
                "id": node_id,
                "type": attrs.get("node_type", "unknown"),
                **{k: v for k, v in attrs.items() if k != "node_type"},
            }
            
            # Extract name from node_id for display
            if "::" in node_id:
                node_data["name"] = node_id.split("::")[-1]
                node_data["path"] = node_id.split("::")[0]
            else:
                node_data["name"] = Path(node_id).name
                node_data["path"] = node_id
            
            nodes.append(node_data)
        
        edges = []
        for source, target, attrs in self._graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "type": attrs.get("edge_type", "unknown"),
                **{k: v for k, v in attrs.items() if k != "edge_type"},
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_nodes": self._graph.number_of_nodes(),
                "total_edges": self._graph.number_of_edges(),
                "files_count": len([n for n, attrs in self._graph.nodes(data=True) 
                                   if attrs.get("node_type") == "file"]),
                "functions_count": len([n for n, attrs in self._graph.nodes(data=True) 
                                       if attrs.get("node_type") == "function"]),
            },
        }
    
    def find_shortest_path(
        self,
        source: str,
        target: str,
    ) -> Optional[List[str]]:
        """Find shortest path between two nodes.
        
        Args:
            source: Source node ID
            target: Target node ID
            
        Returns:
            List of node IDs in path, or None if no path exists
        """
        try:
            return nx.shortest_path(self._graph, source, target)
        except nx.NetworkXNoPath:
            return None
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the codebase.
        
        Returns:
            List of cycles (each cycle is a list of node IDs)
        """
        try:
            cycles = list(nx.simple_cycles(self._file_graph))
            return cycles
        except Exception as e:
            logger.error(f"Error finding circular dependencies: {e}")
            return []
    
    def get_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """Get dependencies for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with "imports" and "imported_by" lists
        """
        imports = []
        imported_by = []
        
        if file_path in self._file_graph:
            imports = list(self._file_graph.successors(file_path))
            imported_by = list(self._file_graph.predecessors(file_path))
        
        return {
            "imports": imports,
            "imported_by": imported_by,
        }


# Singleton instance
impact_engine = ImpactEngine()
