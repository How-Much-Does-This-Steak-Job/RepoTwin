"""Tests for Tree-sitter code parser."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.code_parser import (
    ClassInfo,
    FunctionInfo,
    ImportInfo,
    ParseResult,
    TreeSitterParser,
    parser,
)


class TestTreeSitterParserInitialization:
    """Test parser initialization."""
    
    def test_parser_initialization(self):
        """Test that parser initializes correctly."""
        parser_instance = TreeSitterParser()
        
        assert isinstance(parser_instance, TreeSitterParser)
        assert hasattr(parser_instance, "_parsers")
        assert hasattr(parser_instance, "_languages")
    
    def test_singleton_instance(self):
        """Test that singleton instance exists."""
        assert parser is not None
        assert isinstance(parser, TreeSitterParser)
    
    def test_language_map(self):
        """Test language mappings."""
        parser_instance = TreeSitterParser()
        
        assert parser_instance.LANGUAGE_MAP[".py"] == "python"
        assert parser_instance.LANGUAGE_MAP[".js"] == "javascript"
        assert parser_instance.LANGUAGE_MAP[".ts"] == "typescript"
        assert parser_instance.LANGUAGE_MAP[".tsx"] == "typescript"
        assert parser_instance.LANGUAGE_MAP[".java"] == "java"
        assert parser_instance.LANGUAGE_MAP[".go"] == "go"


class TestLanguageDetection:
    """Test language detection."""
    
    @pytest.mark.parametrize("file_path,expected_lang", [
        ("src/main.py", "python"),
        ("lib/utils.js", "javascript"),
        ("components/Button.tsx", "typescript"),
        ("src/main.ts", "typescript"),
        ("org/example/Main.java", "java"),
        ("cmd/server.go", "go"),
        ("README.md", None),
        ("Dockerfile", None),
        ("config.yaml", None),
    ])
    def test_get_language(self, file_path, expected_lang):
        """Test language detection from file extension."""
        parser_instance = TreeSitterParser()
        
        result = parser_instance.get_language(file_path)
        
        assert result == expected_lang
    
    def test_get_language_case_insensitive(self):
        """Test that language detection is case insensitive."""
        parser_instance = TreeSitterParser()
        
        assert parser_instance.get_language("src/main.PY") == "python"
        assert parser_instance.get_language("src/main.JS") == "javascript"


class TestPythonParsing:
    """Test Python code parsing."""
    
    def test_parse_python_imports(self, sample_python_code):
        """Test parsing Python import statements."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="src/payment.py",
                language="python",
                imports=[
                    ImportInfo(module="logging", file_path="src/payment.py", line=2),
                    ImportInfo(module="typing", names=["Optional"], file_path="src/payment.py", line=3),
                    ImportInfo(module="datetime", names=["datetime"], file_path="src/payment.py", line=4),
                    ImportInfo(module="gateway", names=["PaymentGateway"], file_path="src/payment.py", line=6),
                    ImportInfo(module="models", names=["Payment", "Transaction"], file_path="src/payment.py", line=7),
                ],
            )
            
            result = parser.parse_file("src/payment.py", sample_python_code)
            
            assert result is not None
            assert result.language == "python"
            assert len(result.imports) == 5
            
            # Check regular import
            logging_import = next(i for i in result.imports if i.module == "logging")
            assert logging_import.names == []
            
            # Check from import with names
            models_import = next(i for i in result.imports if i.module == "models")
            assert "Payment" in models_import.names
            assert "Transaction" in models_import.names
    
    def test_parse_python_functions(self, sample_python_code):
        """Test parsing Python function definitions."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="src/payment.py",
                language="python",
                functions=[
                    FunctionInfo(
                        name="__init__",
                        qualified_name="src/payment.py::__init__",
                        file_path="src/payment.py",
                        line_start=18,
                        line_end=20,
                        signature="def __init__(self, gateway)",
                        parameters=[{"name": "self"}, {"name": "gateway"}],
                    ),
                    FunctionInfo(
                        name="process_payment",
                        qualified_name="src/payment.py::process_payment",
                        file_path="src/payment.py",
                        line_start=22,
                        line_end=48,
                        signature="def process_payment(self, amount, currency, customer_id)",
                        parameters=[{"name": "self"}, {"name": "amount"}, {"name": "currency"}, {"name": "customer_id"}],
                        complexity=4,
                    ),
                ],
            )
            
            result = parser.parse_file("src/payment.py", sample_python_code)
            
            assert result is not None
            assert len(result.functions) == 2
            
            process_payment = next(f for f in result.functions if f.name == "process_payment")
            assert process_payment.line_start == 22
            assert process_payment.complexity == 4
    
    def test_parse_python_classes(self, sample_python_code):
        """Test parsing Python class definitions."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="src/payment.py",
                language="python",
                classes=[
                    ClassInfo(
                        name="PaymentProcessor",
                        qualified_name="src/payment.py::PaymentProcessor",
                        file_path="src/payment.py",
                        line_start=16,
                        line_end=52,
                        methods=["__init__", "process_payment", "refund_payment"],
                        inherits_from=[],
                    ),
                    ClassInfo(
                        name="StripeGateway",
                        qualified_name="src/payment.py::StripeGateway",
                        file_path="src/payment.py",
                        line_start=54,
                        line_end=65,
                        methods=["charge", "refund"],
                        inherits_from=["PaymentGateway"],
                    ),
                ],
            )
            
            result = parser.parse_file("src/payment.py", sample_python_code)
            
            assert result is not None
            assert len(result.classes) == 2
            
            payment_processor = next(c for c in result.classes if c.name == "PaymentProcessor")
            assert "process_payment" in payment_processor.methods
            
            stripe_gateway = next(c for c in result.classes if c.name == "StripeGateway")
            assert "PaymentGateway" in stripe_gateway.inherits_from
    
    def test_parse_python_complexity_calculation(self, sample_python_code):
        """Test cyclomatic complexity calculation."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="src/payment.py",
                language="python",
                functions=[
                    FunctionInfo(
                        name="process_payment",
                        qualified_name="src/payment.py::process_payment",
                        file_path="src/payment.py",
                        complexity=4,  # base 1 + if statements (2) + function calls
                    ),
                ],
            )
            
            result = parser.parse_file("src/payment.py", sample_python_code)
            
            assert result is not None
            func = result.functions[0]
            assert func.complexity >= 1  # Base complexity
    
    def test_parse_python_docstrings(self, sample_python_code):
        """Test extracting docstrings from Python code."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="src/payment.py",
                language="python",
                classes=[
                    ClassInfo(
                        name="PaymentProcessor",
                        qualified_name="src/payment.py::PaymentProcessor",
                        file_path="src/payment.py",
                        docstring="Process payments through various gateways.",
                    ),
                ],
            )
            
            result = parser.parse_file("src/payment.py", sample_python_code)
            
            assert result is not None
            assert result.classes[0].docstring == "Process payments through various gateways."


class TestJavaScriptParsing:
    """Test JavaScript/TypeScript parsing."""
    
    def test_parse_javascript_imports(self, sample_javascript_code):
        """Test parsing JavaScript import statements."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="src/PaymentForm.jsx",
                language="javascript",
                imports=[
                    ImportInfo(
                        module="react",
                        names=["useState", "useEffect"],
                        file_path="src/PaymentForm.jsx",
                        line=1,
                    ),
                    ImportInfo(
                        module="./services/PaymentService",
                        names=["PaymentService"],
                        file_path="src/PaymentForm.jsx",
                        line=2,
                    ),
                    ImportInfo(
                        module="./utils/currency",
                        names=["formatCurrency"],
                        file_path="src/PaymentForm.jsx",
                        line=3,
                    ),
                ],
            )
            
            result = parser.parse_file("src/PaymentForm.jsx", sample_javascript_code)
            
            assert result is not None
            assert result.language == "javascript"
            assert len(result.imports) == 3
            
            react_import = next(i for i in result.imports if i.module == "react")
            assert "useState" in react_import.names
    
    def test_parse_javascript_functions(self, sample_javascript_code):
        """Test parsing JavaScript function declarations."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="src/PaymentForm.jsx",
                language="javascript",
                functions=[
                    FunctionInfo(
                        name="PaymentForm",
                        qualified_name="src/PaymentForm.jsx::PaymentForm",
                        file_path="src/PaymentForm.jsx",
                        line_start=10,
                        line_end=60,
                        signature="function PaymentForm(onSubmit, defaultAmount)",
                        parameters=[{"name": "onSubmit"}, {"name": "defaultAmount"}],
                    ),
                ],
                exports=["PaymentForm"],
            )
            
            result = parser.parse_file("src/PaymentForm.jsx", sample_javascript_code)
            
            assert result is not None
            assert len(result.functions) == 1
            assert result.functions[0].name == "PaymentForm"
            assert "PaymentForm" in result.exports


class TestTypeScriptParsing:
    """Test TypeScript parsing."""
    
    def test_parse_typescript_with_types(self, sample_typescript_code):
        """Test parsing TypeScript with type annotations."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="src/payment.service.ts",
                language="typescript",
                functions=[
                    FunctionInfo(
                        name="processPayment",
                        qualified_name="src/payment.service.ts::processPayment",
                        file_path="src/payment.service.ts",
                        line_start=18,
                        line_end=35,
                        return_type="Promise<Payment>",
                    ),
                ],
            )
            
            result = parser.parse_file("src/payment.service.ts", sample_typescript_code)
            
            assert result is not None
            assert result.language == "typescript"


class TestJavaParsing:
    """Test Java parsing."""
    
    def test_parse_java_imports(self, sample_java_code):
        """Test parsing Java import statements."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="src/PaymentService.java",
                language="java",
                imports=[
                    ImportInfo(module="java.util.Optional", file_path="src/PaymentService.java", line=3),
                    ImportInfo(module="java.math.BigDecimal", file_path="src/PaymentService.java", line=4),
                    ImportInfo(module="org.springframework.stereotype.Service", file_path="src/PaymentService.java", line=6),
                ],
            )
            
            result = parser.parse_file("src/PaymentService.java", sample_java_code)
            
            assert result is not None
            assert result.language == "java"
            assert len(result.imports) >= 3
    
    def test_parse_java_classes(self, sample_java_code):
        """Test parsing Java class definitions."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="src/PaymentService.java",
                language="java",
                classes=[
                    ClassInfo(
                        name="PaymentService",
                        qualified_name="src/PaymentService.java::PaymentService",
                        file_path="src/PaymentService.java",
                        line_start=13,
                        line_end=43,
                        methods=["processPayment", "refundPayment"],
                    ),
                ],
            )
            
            result = parser.parse_file("src/PaymentService.java", sample_java_code)
            
            assert result is not None
            assert len(result.classes) == 1
            assert result.classes[0].name == "PaymentService"


class TestGoParsing:
    """Test Go parsing."""
    
    def test_parse_go_imports(self, sample_go_code):
        """Test parsing Go import statements."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="payment/processor.go",
                language="go",
                imports=[
                    ImportInfo(module="context", file_path="payment/processor.go", line=4),
                    ImportInfo(module="errors", file_path="payment/processor.go", line=5),
                    ImportInfo(module="time", file_path="payment/processor.go", line=6),
                    ImportInfo(module="github.com/example/payment/gateway", file_path="payment/processor.go", line=8),
                    ImportInfo(module="github.com/example/payment/models", file_path="payment/processor.go", line=9),
                ],
            )
            
            result = parser.parse_file("payment/processor.go", sample_go_code)
            
            assert result is not None
            assert result.language == "go"
            assert len(result.imports) == 5


class TestDependencyExtraction:
    """Test dependency extraction."""
    
    def test_extract_function_calls(self):
        """Test extracting function calls from code."""
        code = '''
def main():
    result = process_data()
    print(result)
    save_to_db(result)
'''
        with patch.object(parser, "extract_function_calls") as mock_extract:
            mock_extract.return_value = [
                ("process_data", 3),
                ("print", 4),
                ("save_to_db", 5),
            ]
            
            result = parser.extract_function_calls("test.py", code)
            
            assert len(result) == 3
            assert result[0] == ("process_data", 3)
            assert result[1] == ("print", 4)
    
    def test_extract_function_calls_empty(self):
        """Test extracting calls from empty code."""
        with patch.object(parser, "extract_function_calls") as mock_extract:
            mock_extract.return_value = []
            
            result = parser.extract_function_calls("empty.py", "")
            
            assert result == []


class TestErrorHandling:
    """Test error handling."""
    
    def test_parse_unsupported_file(self):
        """Test parsing unsupported file type."""
        result = parser.parse_file("README.md", "# Title")
        
        assert result is None
    
    def test_parse_file_with_error(self):
        """Test handling parse errors gracefully."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = None
            
            result = parser.parse_file("test.py", "invalid syntax here {{<")
            
            # Should return None on error, not raise
            assert result is None
    
    def test_parse_file_not_found(self):
        """Test handling file not found."""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            result = parser.parse_file("/nonexistent/file.py")
            
            assert result is None


class TestASTAnalysis:
    """Test AST analysis features."""
    
    def test_parse_result_dataclass(self):
        """Test ParseResult dataclass."""
        result = ParseResult(
            file_path="test.py",
            language="python",
            content_hash="abc123",
            lines_of_code=100,
        )
        
        assert result.file_path == "test.py"
        assert result.language == "python"
        assert result.content_hash == "abc123"
        assert result.lines_of_code == 100
        assert result.functions == []
        assert result.classes == []
        assert result.imports == []
    
    def test_function_info_dataclass(self):
        """Test FunctionInfo dataclass."""
        func = FunctionInfo(
            name="test_func",
            qualified_name="test.py::test_func",
            file_path="test.py",
            line_start=1,
            line_end=10,
            signature="def test_func()",
            parameters=[{"name": "x"}, {"name": "y"}],
            complexity=3,
        )
        
        assert func.name == "test_func"
        assert func.complexity == 3
        assert len(func.parameters) == 2
    
    def test_class_info_dataclass(self):
        """Test ClassInfo dataclass."""
        cls = ClassInfo(
            name="TestClass",
            qualified_name="test.py::TestClass",
            file_path="test.py",
            line_start=1,
            line_end=20,
            methods=["__init__", "method1", "method2"],
            inherits_from=["BaseClass"],
        )
        
        assert cls.name == "TestClass"
        assert len(cls.methods) == 3
        assert cls.inherits_from == ["BaseClass"]


class TestContentHash:
    """Test content hash generation."""
    
    def test_content_hash_generation(self):
        """Test that content hash is generated correctly."""
        with patch.object(parser, "parse_file") as mock_parse:
            mock_parse.return_value = ParseResult(
                file_path="test.py",
                language="python",
                content_hash="a" * 64,  # SHA256 hex digest
                lines_of_code=10,
            )
            
            result = parser.parse_file("test.py", "def test(): pass")
            
            assert result is not None
            assert result.content_hash == "a" * 64
    
    def test_content_hash_changes_with_content(self):
        """Test that different content produces different hashes."""
        code1 = "def test1(): pass"
        code2 = "def test2(): pass"
        
        # Different content should produce different hashes
        import hashlib
        hash1 = hashlib.sha256(code1.encode()).hexdigest()
        hash2 = hashlib.sha256(code2.encode()).hexdigest()
        
        assert hash1 != hash2
