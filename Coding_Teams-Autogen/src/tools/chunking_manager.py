import hashlib
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import asyncio
import aiofiles
from datetime import datetime, timedelta

@dataclass
class Chunk:
    id: str
    content: str
    metadata: Dict[str, Any]
    size: int
    hash: str
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "size": self.size,
            "hash": self.hash,
            "created_at": self.created_at.isoformat()
        }

class ChunkingManager:
    def __init__(self, max_chunk_size: int = 4000, overlap_size: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.chunks: Dict[str, Chunk] = {}
        
    def create_chunk_id(self, content: str, metadata: Dict[str, Any] = None) -> str:
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"chunk_{timestamp}_{content_hash}"
        
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        if len(text) <= self.max_chunk_size:
            chunk_id = self.create_chunk_id(text, metadata)
            chunk = Chunk(
                id=chunk_id,
                content=text,
                metadata=metadata or {},
                size=len(text),
                hash=hashlib.md5(text.encode()).hexdigest(),
                created_at=datetime.now()
            )
            self.chunks[chunk_id] = chunk
            return [chunk]
        
        chunks = []
        start = 0
        chunk_num = 0
        
        while start < len(text):
            end = min(start + self.max_chunk_size, len(text))
            
            if end < len(text):
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk_content = text[start:end]
            chunk_metadata = (metadata or {}).copy()
            chunk_metadata.update({
                "chunk_number": chunk_num,
                "start_position": start,
                "end_position": end,
                "total_length": len(text)
            })
            
            chunk_id = self.create_chunk_id(chunk_content, chunk_metadata)
            chunk = Chunk(
                id=chunk_id,
                content=chunk_content,
                metadata=chunk_metadata,
                size=len(chunk_content),
                hash=hashlib.md5(chunk_content.encode()).hexdigest(),
                created_at=datetime.now()
            )
            
            chunks.append(chunk)
            self.chunks[chunk_id] = chunk
            
            start = end - self.overlap_size if end < len(text) else end
            chunk_num += 1
            
        return chunks
        
    def chunk_code(self, code: str, language: str = "python", metadata: Dict[str, Any] = None) -> List[Chunk]:
        if language.lower() == "python":
            return self._chunk_python_code(code, metadata)
        elif language.lower() in ["javascript", "typescript"]:
            return self._chunk_js_code(code, metadata)
        else:
            return self.chunk_text(code, metadata)
            
    def _chunk_python_code(self, code: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        lines = code.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        in_class = False
        in_function = False
        indent_level = 0
        
        for i, line in enumerate(lines):
            line_size = len(line) + 1
            
            if current_size + line_size > self.max_chunk_size and current_chunk:
                if not (in_class or in_function):
                    chunk_content = '\n'.join(current_chunk)
                    chunk_metadata = (metadata or {}).copy()
                    chunk_metadata.update({
                        "type": "code",
                        "language": "python",
                        "start_line": i - len(current_chunk) + 1,
                        "end_line": i,
                        "lines_count": len(current_chunk)
                    })
                    
                    chunk_id = self.create_chunk_id(chunk_content, chunk_metadata)
                    chunk = Chunk(
                        id=chunk_id,
                        content=chunk_content,
                        metadata=chunk_metadata,
                        size=len(chunk_content),
                        hash=hashlib.md5(chunk_content.encode()).hexdigest(),
                        created_at=datetime.now()
                    )
                    chunks.append(chunk)
                    self.chunks[chunk_id] = chunk
                    
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
            
            stripped = line.strip()
            if stripped.startswith('class '):
                in_class = True
                indent_level = len(line) - len(line.lstrip())
            elif stripped.startswith('def '):
                in_function = True
                indent_level = len(line) - len(line.lstrip())
            elif stripped and not line.startswith(' ' * (indent_level + 1)) and not line.startswith('\t'):
                in_class = False
                in_function = False
                indent_level = 0
        
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunk_metadata = (metadata or {}).copy()
            chunk_metadata.update({
                "type": "code",
                "language": "python",
                "start_line": len(lines) - len(current_chunk) + 1,
                "end_line": len(lines),
                "lines_count": len(current_chunk)
            })
            
            chunk_id = self.create_chunk_id(chunk_content, chunk_metadata)
            chunk = Chunk(
                id=chunk_id,
                content=chunk_content,
                metadata=chunk_metadata,
                size=len(chunk_content),
                hash=hashlib.md5(chunk_content.encode()).hexdigest(),
                created_at=datetime.now()
            )
            chunks.append(chunk)
            self.chunks[chunk_id] = chunk
            
        return chunks
        
    def _chunk_js_code(self, code: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        lines = code.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        brace_count = 0
        
        for i, line in enumerate(lines):
            line_size = len(line) + 1
            
            if current_size + line_size > self.max_chunk_size and current_chunk:
                if brace_count == 0:
                    chunk_content = '\n'.join(current_chunk)
                    chunk_metadata = (metadata or {}).copy()
                    chunk_metadata.update({
                        "type": "code",
                        "language": "javascript",
                        "start_line": i - len(current_chunk) + 1,
                        "end_line": i,
                        "lines_count": len(current_chunk)
                    })
                    
                    chunk_id = self.create_chunk_id(chunk_content, chunk_metadata)
                    chunk = Chunk(
                        id=chunk_id,
                        content=chunk_content,
                        metadata=chunk_metadata,
                        size=len(chunk_content),
                        hash=hashlib.md5(chunk_content.encode()).hexdigest(),
                        created_at=datetime.now()
                    )
                    chunks.append(chunk)
                    self.chunks[chunk_id] = chunk
                    
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
            
            brace_count += line.count('{') - line.count('}')
        
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunk_metadata = (metadata or {}).copy()
            chunk_metadata.update({
                "type": "code",
                "language": "javascript",
                "start_line": len(lines) - len(current_chunk) + 1,
                "end_line": len(lines),
                "lines_count": len(current_chunk)
            })
            
            chunk_id = self.create_chunk_id(chunk_content, chunk_metadata)
            chunk = Chunk(
                id=chunk_id,
                content=chunk_content,
                metadata=chunk_metadata,
                size=len(chunk_content),
                hash=hashlib.md5(chunk_content.encode()).hexdigest(),
                created_at=datetime.now()
            )
            chunks.append(chunk)
            self.chunks[chunk_id] = chunk
            
        return chunks
        
    def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        return self.chunks.get(chunk_id)
        
    def get_chunks_by_metadata(self, metadata_filter: Dict[str, Any]) -> List[Chunk]:
        matching_chunks = []
        for chunk in self.chunks.values():
            if all(chunk.metadata.get(key) == value for key, value in metadata_filter.items()):
                matching_chunks.append(chunk)
        return matching_chunks
        
    def merge_chunks(self, chunk_ids: List[str]) -> Optional[str]:
        chunks = [self.chunks.get(chunk_id) for chunk_id in chunk_ids]
        chunks = [chunk for chunk in chunks if chunk is not None]
        
        if not chunks:
            return None
            
        chunks.sort(key=lambda x: x.metadata.get("start_position", 0))
        return '\n'.join(chunk.content for chunk in chunks)
        
    async def save_chunks(self, file_path: str) -> bool:
        try:
            chunks_data = {
                chunk_id: chunk.to_dict() 
                for chunk_id, chunk in self.chunks.items()
            }
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(chunks_data, indent=2))
            return True
        except Exception:
            return False
            
    async def load_chunks(self, file_path: str) -> bool:
        try:
            async with aiofiles.open(file_path, 'r') as f:
                chunks_data = json.loads(await f.read())
                
            for chunk_id, chunk_data in chunks_data.items():
                chunk = Chunk(
                    id=chunk_data["id"],
                    content=chunk_data["content"],
                    metadata=chunk_data["metadata"],
                    size=chunk_data["size"],
                    hash=chunk_data["hash"],
                    created_at=datetime.fromisoformat(chunk_data["created_at"])
                )
                self.chunks[chunk_id] = chunk
            return True
        except Exception:
            return False
            
    def cleanup_old_chunks(self, max_age_hours: int = 24):
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_chunks = [
            chunk_id for chunk_id, chunk in self.chunks.items()
            if chunk.created_at < cutoff_time
        ]
        
        for chunk_id in expired_chunks:
            del self.chunks[chunk_id]
            
        return len(expired_chunks)
        
    def get_stats(self) -> Dict[str, Any]:
        if not self.chunks:
            return {
                "total_chunks": 0,
                "total_size": 0,
                "average_size": 0,
                "languages": {}
            }
            
        total_size = sum(chunk.size for chunk in self.chunks.values())
        languages = {}
        
        for chunk in self.chunks.values():
            lang = chunk.metadata.get("language", "unknown")
            languages[lang] = languages.get(lang, 0) + 1
            
        return {
            "total_chunks": len(self.chunks),
            "total_size": total_size,
            "average_size": total_size / len(self.chunks),
            "languages": languages
        } 