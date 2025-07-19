import ast
import re
import os
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
import logging
from collections import defaultdict
import hashlib

@dataclass
class CodeElement:
    name: str
    type: str
    file_path: str
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    parent_class: Optional[str] = None
    complexity: int = 0
    dependencies: List[str] = field(default_factory=list)
    code_snippet: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "docstring": self.docstring,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "decorators": self.decorators,
            "parent_class": self.parent_class,
            "complexity": self.complexity,
            "dependencies": self.dependencies,
            "code_snippet": self.code_snippet
        }

@dataclass
class FileAnalysis:
    file_path: str
    language: str
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    functions: List[CodeElement] = field(default_factory=list)
    classes: List[CodeElement] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    complexity_score: int = 0
    last_modified: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "language": self.language,
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
            "imports": self.imports,
            "complexity_score": self.complexity_score,
            "last_modified": self.last_modified
        }

class CodeAnalyzer:
    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = Path(workspace_path)
        self.logger = logging.getLogger("code_analyzer")
        self.file_analyses: Dict[str, FileAnalysis] = {}
        self.code_index: Dict[str, List[CodeElement]] = defaultdict(list)
        
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }
        
    def get_file_language(self, file_path: Path) -> Optional[str]:
        return self.supported_extensions.get(file_path.suffix.lower())
        
    async def analyze_file(self, file_path: Path) -> Optional[FileAnalysis]:
        if not file_path.exists():
            return None
            
        language = self.get_file_language(file_path)
        if not language:
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            analysis = FileAnalysis(
                file_path=str(file_path),
                language=language,
                total_lines=len(content.splitlines()),
                code_lines=0,
                comment_lines=0,
                blank_lines=0,
                last_modified=str(file_path.stat().st_mtime)
            )
            
            if language == 'python':
                await self._analyze_python_file(file_path, content, analysis)
            elif language in ['javascript', 'typescript']:
                await self._analyze_js_file(file_path, content, analysis)
            else:
                await self._analyze_generic_file(file_path, content, analysis)
                
            self.file_analyses[str(file_path)] = analysis
            self._update_code_index(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            return None
            
    async def _analyze_python_file(self, file_path: Path, content: str, analysis: FileAnalysis):
        lines = content.splitlines()
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                analysis.blank_lines += 1
            elif stripped.startswith('#'):
                analysis.comment_lines += 1
            else:
                analysis.code_lines += 1
                
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        analysis.imports.append(f"{module}.{alias.name}")
                        
            class_visitor = PythonClassVisitor(file_path, content)
            class_visitor.visit(tree)
            analysis.classes = class_visitor.classes
            
            function_visitor = PythonFunctionVisitor(file_path, content)
            function_visitor.visit(tree)
            analysis.functions = function_visitor.functions
            
            analysis.complexity_score = sum(f.complexity for f in analysis.functions) + \
                                      sum(c.complexity for c in analysis.classes)
                                      
        except SyntaxError as e:
            self.logger.warning(f"Syntax error in {file_path}: {e}")
            
    async def _analyze_js_file(self, file_path: Path, content: str, analysis: FileAnalysis):
        lines = content.splitlines()
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                analysis.blank_lines += 1
            elif stripped.startswith('//') or stripped.startswith('/*'):
                analysis.comment_lines += 1
            else:
                analysis.code_lines += 1
                
        import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
        require_pattern = r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        
        imports = re.findall(import_pattern, content) + re.findall(require_pattern, content)
        analysis.imports = imports
        
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*\{'
        arrow_function_pattern = r'(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{'
        
        functions = re.findall(function_pattern, content) + re.findall(arrow_function_pattern, content)
        
        for func_name in functions:
            element = CodeElement(
                name=func_name,
                type="function",
                file_path=str(file_path),
                line_start=0,
                line_end=0
            )
            analysis.functions.append(element)
            
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{'
        classes = re.findall(class_pattern, content)
        
        for class_name in classes:
            element = CodeElement(
                name=class_name,
                type="class",
                file_path=str(file_path),
                line_start=0,
                line_end=0
            )
            analysis.classes.append(element)
            
    async def _analyze_generic_file(self, file_path: Path, content: str, analysis: FileAnalysis):
        lines = content.splitlines()
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                analysis.blank_lines += 1
            elif any(stripped.startswith(comment) for comment in ['//', '#', '/*', '*']):
                analysis.comment_lines += 1
            else:
                analysis.code_lines += 1
                
    def _update_code_index(self, analysis: FileAnalysis):
        for element in analysis.functions + analysis.classes:
            self.code_index[element.name].append(element)
            
    async def analyze_directory(self, directory_path: Path = None) -> Dict[str, FileAnalysis]:
        if directory_path is None:
            directory_path = self.workspace_path
            
        if not directory_path.exists():
            return {}
            
        analyses = {}
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and self.get_file_language(file_path):
                analysis = await self.analyze_file(file_path)
                if analysis:
                    analyses[str(file_path)] = analysis
                    
        return analyses
        
    def find_function(self, function_name: str) -> List[CodeElement]:
        return [elem for elem in self.code_index.get(function_name, []) if elem.type == "function"]
        
    def find_class(self, class_name: str) -> List[CodeElement]:
        return [elem for elem in self.code_index.get(class_name, []) if elem.type == "class"]
        
    def find_by_pattern(self, pattern: str) -> List[CodeElement]:
        regex = re.compile(pattern, re.IGNORECASE)
        results = []
        
        for elements in self.code_index.values():
            for element in elements:
                if regex.search(element.name) or regex.search(element.code_snippet):
                    results.append(element)
                    
        return results
        
    def find_dependencies(self, element_name: str) -> List[CodeElement]:
        dependencies = []
        
        for elements in self.code_index.values():
            for element in elements:
                if element_name in element.dependencies:
                    dependencies.append(element)
                    
        return dependencies
        
    def get_file_summary(self, file_path: str) -> Optional[Dict[str, Any]]:
        analysis = self.file_analyses.get(file_path)
        if not analysis:
            return None
            
        return {
            "file_path": file_path,
            "language": analysis.language,
            "total_lines": analysis.total_lines,
            "functions_count": len(analysis.functions),
            "classes_count": len(analysis.classes),
            "imports_count": len(analysis.imports),
            "complexity_score": analysis.complexity_score,
            "code_coverage": (analysis.code_lines / analysis.total_lines) * 100 if analysis.total_lines > 0 else 0
        }
        
    def get_project_summary(self) -> Dict[str, Any]:
        if not self.file_analyses:
            return {}
            
        total_files = len(self.file_analyses)
        total_lines = sum(a.total_lines for a in self.file_analyses.values())
        total_functions = sum(len(a.functions) for a in self.file_analyses.values())
        total_classes = sum(len(a.classes) for a in self.file_analyses.values())
        total_complexity = sum(a.complexity_score for a in self.file_analyses.values())
        
        languages = defaultdict(int)
        for analysis in self.file_analyses.values():
            languages[analysis.language] += 1
            
        return {
            "total_files": total_files,
            "total_lines": total_lines,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_complexity": total_complexity,
            "languages": dict(languages),
            "average_complexity_per_file": total_complexity / total_files if total_files > 0 else 0
        }
        
    def search_code_snippets(self, query: str, file_extensions: List[str] = None) -> List[Dict[str, Any]]:
        results = []
        
        for file_path, analysis in self.file_analyses.items():
            if file_extensions and not any(file_path.endswith(ext) for ext in file_extensions):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                lines = content.splitlines()
                
                for i, line in enumerate(lines, 1):
                    if query.lower() in line.lower():
                        context_start = max(0, i - 3)
                        context_end = min(len(lines), i + 3)
                        context = lines[context_start:context_end]
                        
                        results.append({
                            "file_path": file_path,
                            "line_number": i,
                            "line_content": line.strip(),
                            "context": context,
                            "language": analysis.language
                        })
                        
            except Exception as e:
                self.logger.error(f"Error searching in {file_path}: {e}")
                
        return results
        
    async def save_analysis_report(self, output_path: str):
        report = {
            "timestamp": str(datetime.now()),
            "project_summary": self.get_project_summary(),
            "file_analyses": {path: analysis.to_dict() for path, analysis in self.file_analyses.items()},
            "code_index_summary": {
                name: len(elements) for name, elements in self.code_index.items()
            }
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"Analysis report saved to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving analysis report: {e}")
            return False
            
    def get_code_metrics(self) -> Dict[str, Any]:
        if not self.file_analyses:
            return {}
            
        all_functions = []
        all_classes = []
        
        for analysis in self.file_analyses.values():
            all_functions.extend(analysis.functions)
            all_classes.extend(analysis.classes)
            
        function_complexities = [f.complexity for f in all_functions if f.complexity > 0]
        class_complexities = [c.complexity for c in all_classes if c.complexity > 0]
        
        return {
            "total_functions": len(all_functions),
            "total_classes": len(all_classes),
            "average_function_complexity": sum(function_complexities) / len(function_complexities) if function_complexities else 0,
            "average_class_complexity": sum(class_complexities) / len(class_complexities) if class_complexities else 0,
            "max_function_complexity": max(function_complexities) if function_complexities else 0,
            "max_class_complexity": max(class_complexities) if class_complexities else 0,
            "functions_with_docstrings": len([f for f in all_functions if f.docstring]),
            "classes_with_docstrings": len([c for c in all_classes if c.docstring])
        }

class PythonClassVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path, content: str):
        self.file_path = file_path
        self.content = content
        self.lines = content.splitlines()
        self.classes = []
        
    def visit_ClassDef(self, node):
        docstring = ast.get_docstring(node)
        
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(f"{decorator.attr}")
                
        code_snippet = '\n'.join(self.lines[node.lineno-1:node.end_lineno])
        
        class_element = CodeElement(
            name=node.name,
            type="class",
            file_path=str(self.file_path),
            line_start=node.lineno,
            line_end=node.end_lineno,
            docstring=docstring,
            decorators=decorators,
            complexity=self._calculate_complexity(node),
            code_snippet=code_snippet
        )
        
        self.classes.append(class_element)
        self.generic_visit(node)
        
    def _calculate_complexity(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                complexity += 1
        return complexity

class PythonFunctionVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path, content: str):
        self.file_path = file_path
        self.content = content
        self.lines = content.splitlines()
        self.functions = []
        self.current_class = None
        
    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node):
        docstring = ast.get_docstring(node)
        
        parameters = []
        for arg in node.args.args:
            parameters.append(arg.arg)
            
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(f"{decorator.attr}")
                
        return_type = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_type = node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return_type = str(node.returns.value)
                
        code_snippet = '\n'.join(self.lines[node.lineno-1:node.end_lineno])
        
        function_element = CodeElement(
            name=node.name,
            type="function",
            file_path=str(self.file_path),
            line_start=node.lineno,
            line_end=node.end_lineno,
            docstring=docstring,
            parameters=parameters,
            return_type=return_type,
            decorators=decorators,
            parent_class=self.current_class,
            complexity=self._calculate_complexity(node),
            code_snippet=code_snippet
        )
        
        self.functions.append(function_element)
        self.generic_visit(node)
        
    def _calculate_complexity(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                complexity += 1
        return complexity

from datetime import datetime 