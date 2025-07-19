import os
import json
import shutil
import aiofiles
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

class WorkspaceManager:
    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = Path(workspace_path)
        self.logger = logging.getLogger("workspace_manager")
        self.created_files = []
        self.created_directories = []
        
    async def initialize_workspace(self) -> None:
        """Initialize a minimal workspace directory structure"""
        try:
            # Create main workspace directory only
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Minimal workspace initialized at {self.workspace_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize workspace: {str(e)}")
            raise
            
    async def create_file(self, file_path: str, content: str, overwrite: bool = False) -> bool:
        """Create a file in the workspace"""
        try:
            full_path = self.workspace_path / file_path
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists and overwrite is False
            if full_path.exists() and not overwrite:
                self.logger.warning(f"File {file_path} already exists, skipping")
                return False
                
            # Write file content
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(content)
                
            self.created_files.append(str(full_path))
            self.logger.info(f"Created file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create file {file_path}: {str(e)}")
            return False
            
    async def read_file(self, file_path: str) -> Optional[str]:
        """Read a file from the workspace"""
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                self.logger.warning(f"File {file_path} does not exist")
                return None
                
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {str(e)}")
            return None
            
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from the workspace"""
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                self.logger.warning(f"File {file_path} does not exist")
                return False
                
            full_path.unlink()
            
            # Remove from created_files list if present
            if str(full_path) in self.created_files:
                self.created_files.remove(str(full_path))
                
            self.logger.info(f"Deleted file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False
            
    async def create_directory(self, directory_path: str) -> bool:
        """Create a directory in the workspace"""
        try:
            full_path = self.workspace_path / directory_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            self.created_directories.append(str(full_path))
            self.logger.info(f"Created directory: {directory_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create directory {directory_path}: {str(e)}")
            return False
            
    async def delete_directory(self, directory_path: str, recursive: bool = False) -> bool:
        """Delete a directory from the workspace"""
        try:
            full_path = self.workspace_path / directory_path
            
            if not full_path.exists():
                self.logger.warning(f"Directory {directory_path} does not exist")
                return False
                
            if recursive:
                shutil.rmtree(full_path)
            else:
                full_path.rmdir()
                
            # Remove from created_directories list if present
            if str(full_path) in self.created_directories:
                self.created_directories.remove(str(full_path))
                
            self.logger.info(f"Deleted directory: {directory_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete directory {directory_path}: {str(e)}")
            return False
            
    async def list_files(self, directory_path: str = "", pattern: str = "*") -> List[str]:
        """List files in a directory"""
        try:
            if directory_path:
                full_path = self.workspace_path / directory_path
            else:
                full_path = self.workspace_path
                
            if not full_path.exists():
                return []
                
            files = list(full_path.glob(pattern))
            relative_files = [str(f.relative_to(self.workspace_path)) for f in files if f.is_file()]
            
            return relative_files
            
        except Exception as e:
            self.logger.error(f"Failed to list files in {directory_path}: {str(e)}")
            return []
            
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file"""
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                return None
                
            stat = full_path.stat()
            
            return {
                "path": file_path,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "is_file": full_path.is_file(),
                "is_directory": full_path.is_dir()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {str(e)}")
            return None
            
    async def copy_file(self, source_path: str, destination_path: str) -> bool:
        """Copy a file within the workspace"""
        try:
            source_full = self.workspace_path / source_path
            dest_full = self.workspace_path / destination_path
            
            if not source_full.exists():
                self.logger.error(f"Source file {source_path} does not exist")
                return False
                
            # Create destination directory if it doesn't exist
            dest_full.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_full, dest_full)
            
            self.created_files.append(str(dest_full))
            self.logger.info(f"Copied file from {source_path} to {destination_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to copy file from {source_path} to {destination_path}: {str(e)}")
            return False
            
    async def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move a file within the workspace"""
        try:
            source_full = self.workspace_path / source_path
            dest_full = self.workspace_path / destination_path
            
            if not source_full.exists():
                self.logger.error(f"Source file {source_path} does not exist")
                return False
                
            # Create destination directory if it doesn't exist
            dest_full.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(source_full, dest_full)
            
            # Update created_files list
            if str(source_full) in self.created_files:
                self.created_files.remove(str(source_full))
            self.created_files.append(str(dest_full))
            
            self.logger.info(f"Moved file from {source_path} to {destination_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to move file from {source_path} to {destination_path}: {str(e)}")
            return False
            
    def get_workspace_stats(self) -> Dict[str, Any]:
        """Get workspace statistics"""
        return {
            "workspace_path": str(self.workspace_path),
            "files_created": len(self.created_files),
            "directories_created": len(self.created_directories),
            "total_items": len(self.created_files) + len(self.created_directories)
        }
        
    async def cleanup_workspace(self) -> bool:
        """Clean up the entire workspace"""
        try:
            if self.workspace_path.exists():
                shutil.rmtree(self.workspace_path)
                
            self.created_files.clear()
            self.created_directories.clear()
            
            self.logger.info(f"Workspace cleaned up: {self.workspace_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup workspace: {str(e)}")
            return False 