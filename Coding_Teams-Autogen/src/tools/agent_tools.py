import asyncio
import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime, timedelta

from .chunking_manager import ChunkingManager
from .cache_manager import CacheManager
from .progress_tracker import ProgressTracker
from .code_analyzer import CodeAnalyzer

class AgentTools:
    def __init__(self, workspace_path: str = "./workspace", cache_dir: str = "./cache"):
        self.workspace_path = Path(workspace_path)
        self.cache_dir = Path(cache_dir)
        self.logger = logging.getLogger("agent_tools")
        
        self.chunking_manager = ChunkingManager()
        self.cache_manager = CacheManager(str(self.cache_dir))
        self.progress_tracker = ProgressTracker()
        self.code_analyzer = CodeAnalyzer(str(self.workspace_path))
        
        self._initialized = False
        
    async def initialize(self):
        if self._initialized:
            return
            
        await self.cache_manager.start()
        await self.progress_tracker.start_ui()
        self._initialized = True
        self.logger.info("Agent tools initialized")
        
    async def shutdown(self):
        if not self._initialized:
            return
            
        await self.cache_manager.stop()
        await self.progress_tracker.stop_ui()
        self._initialized = False
        self.logger.info("Agent tools shut down")
        
    async def read_file(self, file_path: str, use_cache: bool = True) -> Optional[str]:
        full_path = self.workspace_path / file_path
        
        if use_cache:
            cached_content = await self.cache_manager.get(f"file:{file_path}")
            if cached_content:
                return cached_content
                
        try:
            if not full_path.exists():
                return None
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if use_cache:
                await self.cache_manager.set(f"file:{file_path}", content, ttl_seconds=300)
                
            return content
            
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
            
    async def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> bool:
        full_path = self.workspace_path / file_path
        
        try:
            if create_dirs:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            await self.cache_manager.set(f"file:{file_path}", content, ttl_seconds=300)
            
            self.logger.info(f"File written: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            return False
            
    async def list_files(self, directory: str = ".", pattern: str = "*", recursive: bool = True) -> List[str]:
        dir_path = self.workspace_path / directory
        
        if not dir_path.exists():
            return []
            
        try:
            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))
                
            return [str(f.relative_to(self.workspace_path)) for f in files if f.is_file()]
            
        except Exception as e:
            self.logger.error(f"Error listing files in {directory}: {e}")
            return []
            
    async def search_files(self, query: str, file_extensions: List[str] = None, 
                          max_results: int = 50) -> List[Dict[str, Any]]:
        return self.code_analyzer.search_code_snippets(query, file_extensions)[:max_results]
        
    async def find_function(self, function_name: str) -> List[Dict[str, Any]]:
        elements = self.code_analyzer.find_function(function_name)
        return [elem.to_dict() for elem in elements]
        
    async def find_class(self, class_name: str) -> List[Dict[str, Any]]:
        elements = self.code_analyzer.find_class(class_name)
        return [elem.to_dict() for elem in elements]
        
    async def find_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        elements = self.code_analyzer.find_by_pattern(pattern)
        return [elem.to_dict() for elem in elements]
        
    async def analyze_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        full_path = self.workspace_path / file_path
        analysis = await self.code_analyzer.analyze_file(full_path)
        return analysis.to_dict() if analysis else None
        
    async def analyze_directory(self, directory: str = ".") -> Dict[str, Any]:
        dir_path = self.workspace_path / directory
        analyses = await self.code_analyzer.analyze_directory(dir_path)
        return {path: analysis.to_dict() for path, analysis in analyses.items()}
        
    async def get_project_summary(self) -> Dict[str, Any]:
        return self.code_analyzer.get_project_summary()
        
    async def get_code_metrics(self) -> Dict[str, Any]:
        return self.code_analyzer.get_code_metrics()
        
    async def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        chunks = self.chunking_manager.chunk_text(text, metadata)
        return [chunk.to_dict() for chunk in chunks]
        
    async def chunk_code(self, code: str, language: str = "python", 
                        metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        chunks = self.chunking_manager.chunk_code(code, language, metadata)
        return [chunk.to_dict() for chunk in chunks]
        
    async def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        chunk = self.chunking_manager.get_chunk(chunk_id)
        return chunk.to_dict() if chunk else None
        
    async def merge_chunks(self, chunk_ids: List[str]) -> Optional[str]:
        return self.chunking_manager.merge_chunks(chunk_ids)
        
    async def cache_set(self, key: str, value: Any, namespace: str = "default", 
                       ttl_seconds: Optional[int] = None):
        await self.cache_manager.set(key, value, namespace, ttl_seconds)
        
    async def cache_get(self, key: str, namespace: str = "default") -> Optional[Any]:
        return await self.cache_manager.get(key, namespace)
        
    async def cache_delete(self, key: str, namespace: str = "default"):
        await self.cache_manager.delete(key, namespace)
        
    async def cache_clear(self, namespace: str = None):
        await self.cache_manager.clear(namespace)
        
    async def create_progress_task(self, task_id: str, name: str, description: str = "",
                                  total_work: float = 100.0, 
                                  estimated_duration: Optional[timedelta] = None) -> Dict[str, Any]:
        task = self.progress_tracker.create_task(task_id, name, description, total_work, estimated_duration)
        return task.to_dict()
        
    async def start_progress_task(self, task_id: str) -> bool:
        return self.progress_tracker.start_task(task_id)
        
    async def update_progress_task(self, task_id: str, progress: float, message: str = None) -> bool:
        return self.progress_tracker.update_task(task_id, progress, message)
        
    async def complete_progress_task(self, task_id: str) -> bool:
        return self.progress_tracker.complete_task(task_id)
        
    async def fail_progress_task(self, task_id: str, error_message: str = None) -> bool:
        return self.progress_tracker.fail_task(task_id, error_message)
        
    async def get_progress_status(self) -> Dict[str, Any]:
        return self.progress_tracker.get_overall_progress()
        
    async def get_performance_metrics(self) -> Dict[str, Any]:
        return self.progress_tracker.get_performance_metrics()
        
    async def copy_file(self, source: str, destination: str) -> bool:
        try:
            source_path = self.workspace_path / source
            dest_path = self.workspace_path / destination
            
            if not source_path.exists():
                return False
                
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(source_path, 'rb') as src, open(dest_path, 'wb') as dst:
                dst.write(src.read())
                
            self.logger.info(f"File copied from {source} to {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error copying file from {source} to {destination}: {e}")
            return False
            
    async def move_file(self, source: str, destination: str) -> bool:
        try:
            source_path = self.workspace_path / source
            dest_path = self.workspace_path / destination
            
            if not source_path.exists():
                return False
                
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.rename(dest_path)
            
            self.logger.info(f"File moved from {source} to {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error moving file from {source} to {destination}: {e}")
            return False
            
    async def delete_file(self, file_path: str) -> bool:
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                return False
                
            full_path.unlink()
            
            await self.cache_manager.delete(f"file:{file_path}")
            
            self.logger.info(f"File deleted: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            return False
            
    async def create_directory(self, directory: str) -> bool:
        try:
            dir_path = self.workspace_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Directory created: {directory}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating directory {directory}: {e}")
            return False
            
    async def delete_directory(self, directory: str, recursive: bool = False) -> bool:
        try:
            dir_path = self.workspace_path / directory
            
            if not dir_path.exists():
                return False
                
            if recursive:
                import shutil
                shutil.rmtree(dir_path)
            else:
                dir_path.rmdir()
                
            self.logger.info(f"Directory deleted: {directory}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting directory {directory}: {e}")
            return False
            
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                return None
                
            stat = full_path.stat()
            
            return {
                "file_path": file_path,
                "size_bytes": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_directory": full_path.is_dir(),
                "is_file": full_path.is_file(),
                "extension": full_path.suffix,
                "name": full_path.name
            }
            
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {e}")
            return None
            
    async def search_and_replace(self, file_path: str, search_pattern: str, 
                                replacement: str, use_regex: bool = False) -> bool:
        try:
            content = await self.read_file(file_path, use_cache=False)
            if content is None:
                return False
                
            if use_regex:
                new_content = re.sub(search_pattern, replacement, content)
            else:
                new_content = content.replace(search_pattern, replacement)
                
            if new_content != content:
                await self.write_file(file_path, new_content)
                self.logger.info(f"Search and replace completed in {file_path}")
                return True
            else:
                self.logger.info(f"No changes made in {file_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in search and replace for {file_path}: {e}")
            return False
            
    async def extract_functions_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        analysis = await self.analyze_file(file_path)
        if analysis:
            return analysis.get("functions", [])
        return []
        
    async def extract_classes_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        analysis = await self.analyze_file(file_path)
        if analysis:
            return analysis.get("classes", [])
        return []
        
    async def get_file_dependencies(self, file_path: str) -> List[str]:
        analysis = await self.analyze_file(file_path)
        if analysis:
            return analysis.get("imports", [])
        return []
        
    async def find_similar_code(self, code_snippet: str, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        results = []
        
        analyses = await self.analyze_directory()
        
        for file_path, analysis in analyses.items():
            for func in analysis.get("functions", []):
                if func.get("code_snippet"):
                    similarity = self._calculate_similarity(code_snippet, func["code_snippet"])
                    if similarity >= similarity_threshold:
                        results.append({
                            "file_path": file_path,
                            "function_name": func["name"],
                            "similarity": similarity,
                            "code_snippet": func["code_snippet"]
                        })
                        
        return sorted(results, key=lambda x: x["similarity"], reverse=True)
        
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()
        
    async def get_workspace_statistics(self) -> Dict[str, Any]:
        files = await self.list_files(recursive=True)
        
        stats = {
            "total_files": len(files),
            "file_types": {},
            "total_size_bytes": 0,
            "languages": {}
        }
        
        for file_path in files:
            full_path = self.workspace_path / file_path
            
            if full_path.exists():
                stats["total_size_bytes"] += full_path.stat().st_size
                
                extension = full_path.suffix.lower()
                stats["file_types"][extension] = stats["file_types"].get(extension, 0) + 1
                
                language = self.code_analyzer.get_file_language(full_path)
                if language:
                    stats["languages"][language] = stats["languages"].get(language, 0) + 1
                    
        project_summary = await self.get_project_summary()
        stats.update(project_summary)
        
        return stats
        
    async def backup_workspace(self, backup_path: str) -> bool:
        try:
            import shutil
            
            backup_full_path = Path(backup_path)
            backup_full_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.make_archive(str(backup_full_path), 'zip', self.workspace_path)
            
            self.logger.info(f"Workspace backed up to {backup_path}.zip")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up workspace: {e}")
            return False
            
    async def restore_workspace(self, backup_path: str) -> bool:
        try:
            import shutil
            
            backup_full_path = Path(f"{backup_path}.zip")
            
            if not backup_full_path.exists():
                return False
                
            shutil.unpack_archive(str(backup_full_path), self.workspace_path)
            
            self.logger.info(f"Workspace restored from {backup_path}.zip")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring workspace: {e}")
            return False
            
    async def get_tools_status(self) -> Dict[str, Any]:
        cache_stats = await self.cache_manager.get_cache_stats()
        progress_stats = self.progress_tracker.get_overall_progress()
        chunking_stats = self.chunking_manager.get_stats()
        
        return {
            "initialized": self._initialized,
            "workspace_path": str(self.workspace_path),
            "cache_stats": cache_stats,
            "progress_stats": progress_stats,
            "chunking_stats": chunking_stats,
            "code_analyzer_files": len(self.code_analyzer.file_analyses)
        } 