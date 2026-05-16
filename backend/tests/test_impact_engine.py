"""Tests for impact analysis engine."""

from typing import List, Set
from unittest.mock import MagicMock, patch

import networkx as nx
import pytest

from app.core.code_parser import FunctionInfo, ClassInfo, ImportInfo, ParseResult
from app.core.impact_engine import (
    ImpactEngine,
    ImpactResult,
    impact_engine,
)


class TestImpactEngineInitialization:
    """Test impact engine initialization."""
    
    def test_engine_initialization(self):
        """Test that engine initializes correctly."""
        engine = ImpactEngine()
        
        assert isinstance(engine._graph, nx.DiGraph)
        assert isinstance(engine._file_graph, nx.DiGraph)
        assert engine._graph.number_of_nodes() == 0
        assert engine._file_graph.number_of_nodes() == 0
    
    def test_singleton_instance(self):
        """Test that singleton instance exists."""
        assert impact_engine is not None
        assert isinstance(impact_engine, ImpactEngine)


class TestDependencyGraphBuilding:
    """Test dependency graph building."""
    
    def test_build_graph_with_single_file(self):
        """Test building graph with a single file."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/main.py",
                language="python",
                functions=[
                    FunctionInfo(
                        name="main",
                        qualified_name="src/main.py::main",
                        file_path="src/main.py",
                        line_start=1,
                        line_end=5,
                        signature="def main()",
                    ),
                ],
                classes=[],
                imports=[],
            ),
        ]
        
        graph = engine.build_dependency_graph(parse_results)
        
        assert graph.number_of_nodes() == 2  # file + function
        assert graph.number_of_edges() == 1  # file -> function
        assert graph.has_node("src/main.py")
        assert graph.has_node("src/main.py::main")
    
    def test_build_graph_with_imports(self):
        """Test building graph with imports."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/main.py",
                language="python",
                functions=[],
                imports=[
                    ImportInfo(module="utils", file_path="src/main.py", line=1),
                ],
            ),
            ParseResult(
                file_path="src/utils.py",
                language="python",
                functions=[
                    FunctionInfo(
                        name="helper",
                        qualified_name="src/utils.py::helper",
                        file_path="src/utils.py",
                        line_start=1,
                        line_end=3,
                        signature="def helper()",
                    ),
                ],
                imports=[],
            ),
        ]
        
        graph = engine.build_dependency_graph(parse_results)
        
        # Should have import edge from main.py to utils.py
        assert graph.has_edge("src/main.py", "src/utils.py")
        edge_data = graph.get_edge_data("src/main.py", "src/utils.py")
        assert edge_data["edge_type"] == "imports"
    
    def test_build_graph_with_classes(self):
        """Test building graph with class definitions."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/models.py",
                language="python",
                functions=[],
                classes=[
                    ClassInfo(
                        name="Payment",
                        qualified_name="src/models.py::Payment",
                        file_path="src/models.py",
                        line_start=1,
                        line_end=20,
                        methods=["__init__", "save"],
                    ),
                ],
                imports=[],
            ),
        ]
        
        graph = engine.build_dependency_graph(parse_results)
        
        assert graph.has_node("src/models.py::Payment")
        assert graph.has_edge("src/models.py", "src/models.py::Payment")
    
    def test_build_graph_with_inheritance(self):
        """Test building graph with class inheritance."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/payment.py",
                language="python",
                functions=[],
                classes=[
                    ClassInfo(
                        name="PaymentGateway",
                        qualified_name="src/payment.py::PaymentGateway",
                        file_path="src/payment.py",
                        line_start=1,
                        line_end=10,
                        methods=["charge"],
                        inherits_from=[],
                    ),
                    ClassInfo(
                        name="StripeGateway",
                        qualified_name="src/payment.py::StripeGateway",
                        file_path="src/payment.py",
                        line_start=11,
                        line_end=20,
                        methods=["charge"],
                        inherits_from=["PaymentGateway"],
                    ),
                ],
                imports=[],
            ),
        ]
        
        graph = engine.build_dependency_graph(parse_results)
        
        # Should have inheritance edge
        assert graph.has_edge(
            "src/payment.py::StripeGateway",
            "src/payment.py::PaymentGateway",
        )
    
    def test_build_graph_empty_results(self):
        """Test building graph with empty parse results."""
        engine = ImpactEngine()
        
        graph = engine.build_dependency_graph([])
        
        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0


class TestImpactAnalysis:
    """Test impact analysis."""
    
    def test_analyze_single_file_change(self):
        """Test analyzing impact of changing a single file."""
        engine = ImpactEngine()
        
        # Build graph
        parse_results = [
            ParseResult(
                file_path="src/main.py",
                language="python",
                functions=[
                    FunctionInfo(
                        name="main",
                        qualified_name="src/main.py::main",
                        file_path="src/main.py",
                        line_start=1,
                        line_end=5,
                        signature="def main()",
                    ),
                ],
                imports=[],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        # Analyze impact
        result = engine.analyze_impact(["src/main.py"])
        
        assert isinstance(result, ImpactResult)
        assert result.primary_files == {"src/main.py"}
        assert "src/main.py::main" in result.affected_functions
    
    def test_analyze_with_dependencies(self):
        """Test analyzing impact with file dependencies."""
        engine = ImpactEngine()
        
        # Build graph: main.py imports utils.py
        parse_results = [
            ParseResult(
                file_path="src/main.py",
                language="python",
                functions=[],
                imports=[ImportInfo(module="utils", file_path="src/main.py", line=1)],
            ),
            ParseResult(
                file_path="src/utils.py",
                language="python",
                functions=[
                    FunctionInfo(
                        name="helper",
                        qualified_name="src/utils.py::helper",
                        file_path="src/utils.py",
                        line_start=1,
                        line_end=3,
                        signature="def helper()",
                    ),
                ],
                imports=[],
            ),
            ParseResult(
                file_path="src/app.py",
                language="python",
                functions=[],
                imports=[ImportInfo(module="main", file_path="src/app.py", line=1)],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        # Analyze impact of changing utils.py
        result = engine.analyze_impact(["src/utils.py"])
        
        assert "src/utils.py" in result.primary_files
        # main.py depends on utils.py
        assert "src/main.py" in result.secondary_files
        # app.py depends on main.py which depends on utils.py
        assert "src/app.py" in result.tertiary_files
    
    def test_analyze_with_test_detection(self):
        """Test detecting affected tests."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/main.py",
                language="python",
                functions=[
                    FunctionInfo(
                        name="process",
                        qualified_name="src/main.py::process",
                        file_path="src/main.py",
                        line_start=1,
                        line_end=10,
                        signature="def process()",
                    ),
                ],
                imports=[],
            ),
            ParseResult(
                file_path="tests/test_main.py",
                language="python",
                functions=[
                    FunctionInfo(
                        name="test_process",
                        qualified_name="tests/test_main.py::test_process",
                        file_path="tests/test_main.py",
                        line_start=1,
                        line_end=5,
                        signature="def test_process()",
                    ),
                ],
                imports=[ImportInfo(module="main", file_path="tests/test_main.py", line=1)],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        result = engine.analyze_impact(["src/main.py"])
        
        # Test file should be detected as affected
        assert "tests/test_main.py" in result.tests_affected


class TestImpactMetrics:
    """Test impact metrics calculation."""
    
    def test_calculate_metrics_small_impact(self):
        """Test calculating metrics for small impact."""
        engine = ImpactEngine()
        
        impact = ImpactResult(
            primary_files={"file1.py"},
            secondary_files=set(),
            tertiary_files=set(),
            affected_functions=set(),
            affected_classes=set(),
            entry_points=set(),
            tests_affected=set(),
        )
        
        metrics = engine.calculate_impact_metrics(impact, total_files=100)
        
        assert metrics["files_affected"] == 1
        assert metrics["files_direct"] == 1
        assert metrics["files_indirect"] == 0
        assert metrics["percentage_of_codebase"] == 1.0
        assert metrics["category"] == "small"
    
    def test_calculate_metrics_medium_impact(self):
        """Test calculating metrics for medium impact."""
        engine = ImpactEngine()
        
        impact = ImpactResult(
            primary_files={"file1.py"},
            secondary_files={"file2.py", "file3.py", "file4.py", "file5.py"},
            tertiary_files={"file6.py", "file7.py", "file8.py"},
            affected_functions={"f1", "f2", "f3"},
            affected_classes={"c1"},
            entry_points={"file1.py"},
            tests_affected={"test1.py"},
        )
        
        metrics = engine.calculate_impact_metrics(impact, total_files=100)
        
        assert metrics["files_affected"] == 9
        assert metrics["files_direct"] == 1
        assert metrics["files_indirect"] == 8
        assert metrics["functions_affected"] == 3
        assert metrics["classes_affected"] == 1
        assert metrics["tests_affected"] == 1
        assert metrics["percentage_of_codebase"] == 9.0
        assert metrics["category"] == "medium"
    
    def test_calculate_metrics_large_impact(self):
        """Test calculating metrics for large impact."""
        engine = ImpactEngine()
        
        impact = ImpactResult(
            primary_files={"file1.py"},
            secondary_files={f"file{i}.py" for i in range(2, 15)},
            tertiary_files=set(),
            affected_functions=set(),
            affected_classes=set(),
            entry_points=set(),
            tests_affected=set(),
        )
        
        metrics = engine.calculate_impact_metrics(impact, total_files=100)
        
        assert metrics["files_affected"] == 14
        assert metrics["percentage_of_codebase"] == 14.0
        assert metrics["category"] == "large"


class TestEntryPointIdentification:
    """Test entry point identification."""
    
    def test_identify_main_entry_point(self):
        """Test identifying main.py as entry point."""
        engine = ImpactEngine()
        
        impact = ImpactResult(
            primary_files={"src/main.py"},
            secondary_files=set(),
            tertiary_files=set(),
        )
        
        # Simulate graph
        engine._file_graph.add_node("src/main.py")
        
        entry_points = engine._identify_entry_points(impact)
        
        assert "src/main.py" in entry_points
    
    def test_identify_no_incoming_imports(self):
        """Test identifying files with no incoming imports."""
        engine = ImpactEngine()
        
        impact = ImpactResult(
            primary_files={"src/entry.py"},
            secondary_files={"src/utils.py"},
            tertiary_files=set(),
        )
        
        # Simulate graph: entry.py has no predecessors
        engine._file_graph.add_node("src/entry.py")
        engine._file_graph.add_node("src/utils.py")
        engine._file_graph.add_edge("src/entry.py", "src/utils.py")
        
        entry_points = engine._identify_entry_points(impact)
        
        assert "src/entry.py" in entry_points
    
    def test_identify_index_js_entry_point(self):
        """Test identifying index.js as entry point."""
        engine = ImpactEngine()
        
        impact = ImpactResult(
            primary_files={"src/index.js"},
            secondary_files=set(),
            tertiary_files=set(),
        )
        
        entry_points = engine._identify_entry_points(impact)
        
        assert "src/index.js" in entry_points


class TestGraphDataSerialization:
    """Test graph data serialization."""
    
    def test_get_graph_data(self):
        """Test getting graph data for serialization."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/main.py",
                language="python",
                functions=[
                    FunctionInfo(
                        name="main",
                        qualified_name="src/main.py::main",
                        file_path="src/main.py",
                        line_start=1,
                        line_end=5,
                        signature="def main()",
                    ),
                ],
                imports=[],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        data = engine.get_graph_data()
        
        assert "nodes" in data
        assert "edges" in data
        assert "stats" in data
        assert data["stats"]["total_nodes"] == 2
        assert data["stats"]["total_edges"] == 1
        assert data["stats"]["files_count"] == 1
        assert data["stats"]["functions_count"] == 1
        
        # Check node data
        file_node = next(n for n in data["nodes"] if n["id"] == "src/main.py")
        assert file_node["type"] == "file"
        assert file_node["name"] == "main.py"


class TestPathFinding:
    """Test path finding in graph."""
    
    def test_find_shortest_path_exists(self):
        """Test finding shortest path between nodes."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/a.py",
                language="python",
                functions=[],
                imports=[ImportInfo(module="b", file_path="src/a.py", line=1)],
            ),
            ParseResult(
                file_path="src/b.py",
                language="python",
                functions=[],
                imports=[ImportInfo(module="c", file_path="src/b.py", line=1)],
            ),
            ParseResult(
                file_path="src/c.py",
                language="python",
                functions=[],
                imports=[],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        path = engine.find_shortest_path("src/a.py", "src/c.py")
        
        assert path is not None
        assert len(path) == 3
        assert path[0] == "src/a.py"
        assert path[-1] == "src/c.py"
    
    def test_find_shortest_path_not_exists(self):
        """Test finding path when no path exists."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/a.py",
                language="python",
                functions=[],
                imports=[],
            ),
            ParseResult(
                file_path="src/b.py",
                language="python",
                functions=[],
                imports=[],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        path = engine.find_shortest_path("src/a.py", "src/b.py")
        
        assert path is None


class TestCircularDependencies:
    """Test circular dependency detection."""
    
    def test_find_circular_dependencies(self):
        """Test finding circular dependencies."""
        engine = ImpactEngine()
        
        # Create circular dependency: a -> b -> c -> a
        parse_results = [
            ParseResult(
                file_path="src/a.py",
                language="python",
                functions=[],
                imports=[ImportInfo(module="b", file_path="src/a.py", line=1)],
            ),
            ParseResult(
                file_path="src/b.py",
                language="python",
                functions=[],
                imports=[ImportInfo(module="c", file_path="src/b.py", line=1)],
            ),
            ParseResult(
                file_path="src/c.py",
                language="python",
                functions=[],
                imports=[ImportInfo(module="a", file_path="src/c.py", line=1)],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        cycles = engine.find_circular_dependencies()
        
        assert len(cycles) > 0
        # Each cycle should include all three files
        cycle = cycles[0]
        assert "src/a.py" in cycle
        assert "src/b.py" in cycle
        assert "src/c.py" in cycle
    
    def test_no_circular_dependencies(self):
        """Test with no circular dependencies."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/a.py",
                language="python",
                functions=[],
                imports=[ImportInfo(module="b", file_path="src/a.py", line=1)],
            ),
            ParseResult(
                file_path="src/b.py",
                language="python",
                functions=[],
                imports=[],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        cycles = engine.find_circular_dependencies()
        
        assert len(cycles) == 0


class TestFileDependencies:
    """Test file dependency queries."""
    
    def test_get_file_dependencies(self):
        """Test getting dependencies for a file."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/main.py",
                language="python",
                functions=[],
                imports=[ImportInfo(module="utils", file_path="src/main.py", line=1)],
            ),
            ParseResult(
                file_path="src/utils.py",
                language="python",
                functions=[],
                imports=[],
            ),
            ParseResult(
                file_path="src/app.py",
                language="python",
                functions=[],
                imports=[ImportInfo(module="main", file_path="src/app.py", line=1)],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        deps = engine.get_file_dependencies("src/main.py")
        
        assert "src/utils.py" in deps["imports"]
        assert "src/app.py" in deps["imported_by"]
    
    def test_get_file_dependencies_not_in_graph(self):
        """Test getting dependencies for file not in graph."""
        engine = ImpactEngine()
        
        deps = engine.get_file_dependencies("nonexistent.py")
        
        assert deps["imports"] == []
        assert deps["imported_by"] == []


class TestTestFileDetection:
    """Test test file detection."""
    
    @pytest.mark.parametrize("file_path,is_test", [
        ("tests/test_main.py", True),
        ("src/main_test.py", True),
        ("src/main.spec.js", True),
        ("src/main.test.ts", True),
        ("__tests__/main.test.js", True),
        ("test/test_main.py", True),
        ("src/main.py", False),
        ("lib/utils.py", False),
    ])
    def test_is_test_file(self, file_path, is_test):
        """Test test file detection patterns."""
        engine = ImpactEngine()
        
        result = engine._is_test_file(file_path)
        
        assert result == is_test


class TestImportResolution:
    """Test import resolution."""
    
    def test_resolve_import_simple(self):
        """Test resolving simple import."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/utils.py",
                language="python",
                functions=[],
                imports=[],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        imp = ImportInfo(module="utils", file_path="src/main.py", line=1)
        result = engine._resolve_import(imp, parse_results)
        
        assert result == "src/utils.py"
    
    def test_resolve_import_with_module_path(self):
        """Test resolving module path import."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/models/payment.py",
                language="python",
                functions=[],
                imports=[],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        imp = ImportInfo(module="models.payment", file_path="src/main.py", line=1)
        result = engine._resolve_import(imp, parse_results)
        
        assert result == "src/models/payment.py"
    
    def test_resolve_import_not_found(self):
        """Test resolving import that doesn't exist."""
        engine = ImpactEngine()
        
        imp = ImportInfo(module="nonexistent", file_path="src/main.py", line=1)
        result = engine._resolve_import(imp, [])
        
        assert result is None


class TestFunctionAndClassResolution:
    """Test function and class resolution."""
    
    def test_resolve_function_call(self):
        """Test resolving function call."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/utils.py",
                language="python",
                functions=[
                    FunctionInfo(
                        name="helper",
                        qualified_name="src/utils.py::helper",
                        file_path="src/utils.py",
                        line_start=1,
                        line_end=3,
                        signature="def helper()",
                    ),
                ],
                imports=[],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        result = engine._resolve_function_call("helper", parse_results)
        
        assert result == "src/utils.py::helper"
    
    def test_resolve_class(self):
        """Test resolving class reference."""
        engine = ImpactEngine()
        
        parse_results = [
            ParseResult(
                file_path="src/models.py",
                language="python",
                functions=[],
                classes=[
                    ClassInfo(
                        name="Payment",
                        qualified_name="src/models.py::Payment",
                        file_path="src/models.py",
                        line_start=1,
                        line_end=20,
                        methods=[],
                    ),
                ],
                imports=[],
            ),
        ]
        engine.build_dependency_graph(parse_results)
        
        result = engine._resolve_class("Payment", parse_results)
        
        assert result == "src/models.py::Payment"
