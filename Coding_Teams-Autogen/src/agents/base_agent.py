import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.tools.agent_tools import AgentTools

console = Console()

class MessageTag(Enum):
    ASK_CLARIFICATION = "ASK_CLARIFICATION"
    PROGRESS = "PROGRESS"
    BLOCKER = "BLOCKER"
    DEFECT = "DEFECT"
    STEP_START = "STEP_START"
    STEP_SUCCESS = "STEP_SUCCESS"
    NEXT_STEP = "NEXT_STEP"
    PROJECT_COMPLETE = "PROJECT_COMPLETE"
    AGENT_EXIT = "AGENT_EXIT"

@dataclass
class AgentMessage:
    role: str
    tag: MessageTag
    title: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def format_message(self) -> str:
        return f"{self.role} | {self.tag.value} | {self.title}\n\n{self.content}"

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, system_prompt: str, workspace_manager=None, tools: AgentTools = None):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.workspace_manager = workspace_manager
        self.tools = tools or AgentTools()
        self.messages: List[AgentMessage] = []
        self.is_active = True
        self.current_step = None
        self.current_task_id = None
        self.logger = logging.getLogger(f"agent.{name}")
        
    async def initialize_tools(self):
        if not self.tools._initialized:
            await self.tools.initialize()
            
    async def shutdown_tools(self):
        if self.tools._initialized:
            await self.tools.shutdown()
        
    @abstractmethod
    def get_success_signal(self) -> str:
        pass
        
    @abstractmethod
    def get_termination_signal(self) -> str:
        pass
        
    @abstractmethod
    async def execute_step(self, step_info: Dict[str, Any]) -> AgentMessage:
        pass
        
    def send_message(self, tag: MessageTag, title: str, content: str, metadata: Dict[str, Any] = None) -> AgentMessage:
        message = AgentMessage(
            role=self.role,
            tag=tag,
            title=title,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        
        color = self._get_tag_color(tag)
        panel = Panel(
            Text(content, style="white"),
            title=f"[bold {color}]{self.role}[/bold {color}] | {tag.value} | {title}",
            border_style=color,
            width=80
        )
        console.print(panel)
        
        return message
        
    def _get_tag_color(self, tag: MessageTag) -> str:
        color_map = {
            MessageTag.ASK_CLARIFICATION: "yellow",
            MessageTag.PROGRESS: "blue",
            MessageTag.BLOCKER: "red",
            MessageTag.DEFECT: "magenta",
            MessageTag.STEP_START: "green",
            MessageTag.STEP_SUCCESS: "bright_green",
            MessageTag.NEXT_STEP: "cyan",
            MessageTag.PROJECT_COMPLETE: "gold1",
            MessageTag.AGENT_EXIT: "dim"
        }
        return color_map.get(tag, "white")
    
    def ask_clarification(self, question: str) -> AgentMessage:
        return self.send_message(MessageTag.ASK_CLARIFICATION, "Need Clarification", question)
        
    def report_progress(self, progress: str, metadata: Dict[str, Any] = None) -> AgentMessage:
        return self.send_message(MessageTag.PROGRESS, "Progress Update", progress, metadata)
        
    def report_blocker(self, blocker: str, metadata: Dict[str, Any] = None) -> AgentMessage:
        return self.send_message(MessageTag.BLOCKER, "Blocker Encountered", blocker, metadata)
        
    def report_defect(self, defect: str, metadata: Dict[str, Any] = None) -> AgentMessage:
        return self.send_message(MessageTag.DEFECT, "Defect Found", defect, metadata)
        
    async def signal_step_start(self, step_name: str, assisting_agents: List[str] = None, estimated_duration: timedelta = None) -> AgentMessage:
        content = f"Starting step: {step_name}"
        if assisting_agents:
            content += f"\nAssisting agents: {', '.join(assisting_agents)}"
            
        self.current_task_id = f"{self.name}_{step_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        await self.tools.create_progress_task(
            self.current_task_id,
            step_name,
            f"{self.role} executing {step_name}",
            estimated_duration=estimated_duration
        )
        await self.tools.start_progress_task(self.current_task_id)
        
        return self.send_message(MessageTag.STEP_START, f"Step {step_name} Start", content)
        
    async def signal_step_success(self, step_name: str, changelog: str, artifacts: List[str] = None) -> AgentMessage:
        content = f"Step {step_name} completed successfully.\n\nChangelog:\n{changelog}"
        if artifacts:
            content += f"\n\nArtifacts:\n" + "\n".join(f"- {artifact}" for artifact in artifacts)
            
        if self.current_task_id:
            await self.tools.complete_progress_task(self.current_task_id)
            
        return self.send_message(MessageTag.STEP_SUCCESS, f"Step {step_name} Success", content)
        
    async def update_step_progress(self, progress: float, message: str = None):
        if self.current_task_id:
            await self.tools.update_progress_task(self.current_task_id, progress, message)
            
    async def fail_current_step(self, error_message: str):
        if self.current_task_id:
            await self.tools.fail_progress_task(self.current_task_id, error_message)
        
    def terminate(self) -> AgentMessage:
        self.is_active = False
        return self.send_message(MessageTag.AGENT_EXIT, f"{self.role} Terminating", 
                               f"{self.role} has completed all responsibilities and is terminating.")
        
    def get_message_history(self) -> List[Dict[str, Any]]:
        return [
            {
                "role": msg.role,
                "tag": msg.tag.value,
                "title": msg.title,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in self.messages
        ]
        
    async def read_file(self, file_path: str, use_cache: bool = True) -> Optional[str]:
        return await self.tools.read_file(file_path, use_cache)
        
    async def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> bool:
        return await self.tools.write_file(file_path, content, create_dirs)
        
    async def list_files(self, directory: str = ".", pattern: str = "*", recursive: bool = True) -> List[str]:
        return await self.tools.list_files(directory, pattern, recursive)
        
    async def search_files(self, query: str, file_extensions: List[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        return await self.tools.search_files(query, file_extensions, max_results)
        
    async def find_function(self, function_name: str) -> List[Dict[str, Any]]:
        return await self.tools.find_function(function_name)
        
    async def find_class(self, class_name: str) -> List[Dict[str, Any]]:
        return await self.tools.find_class(class_name)
        
    async def find_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        return await self.tools.find_by_pattern(pattern)
        
    async def analyze_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        return await self.tools.analyze_file(file_path)
        
    async def analyze_directory(self, directory: str = ".") -> Dict[str, Any]:
        return await self.tools.analyze_directory(directory)
        
    async def get_project_summary(self) -> Dict[str, Any]:
        return await self.tools.get_project_summary()
        
    async def get_code_metrics(self) -> Dict[str, Any]:
        return await self.tools.get_code_metrics()
        
    async def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return await self.tools.chunk_text(text, metadata)
        
    async def chunk_code(self, code: str, language: str = "python", metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return await self.tools.chunk_code(code, language, metadata)
        
    async def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        return await self.tools.get_chunk(chunk_id)
        
    async def merge_chunks(self, chunk_ids: List[str]) -> Optional[str]:
        return await self.tools.merge_chunks(chunk_ids)
        
    async def cache_set(self, key: str, value: Any, namespace: str = None, ttl_seconds: Optional[int] = None):
        namespace = namespace or self.name
        await self.tools.cache_set(key, value, namespace, ttl_seconds)
        
    async def cache_get(self, key: str, namespace: str = None) -> Optional[Any]:
        namespace = namespace or self.name
        return await self.tools.cache_get(key, namespace)
        
    async def cache_delete(self, key: str, namespace: str = None):
        namespace = namespace or self.name
        await self.tools.cache_delete(key, namespace)
        
    async def cache_clear(self, namespace: str = None):
        namespace = namespace or self.name
        await self.tools.cache_clear(namespace)
        
    async def copy_file(self, source: str, destination: str) -> bool:
        return await self.tools.copy_file(source, destination)
        
    async def move_file(self, source: str, destination: str) -> bool:
        return await self.tools.move_file(source, destination)
        
    async def delete_file(self, file_path: str) -> bool:
        return await self.tools.delete_file(file_path)
        
    async def create_directory(self, directory: str) -> bool:
        return await self.tools.create_directory(directory)
        
    async def delete_directory(self, directory: str, recursive: bool = False) -> bool:
        return await self.tools.delete_directory(directory, recursive)
        
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        return await self.tools.get_file_info(file_path)
        
    async def search_and_replace(self, file_path: str, search_pattern: str, replacement: str, use_regex: bool = False) -> bool:
        return await self.tools.search_and_replace(file_path, search_pattern, replacement, use_regex)
        
    async def extract_functions_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        return await self.tools.extract_functions_from_file(file_path)
        
    async def extract_classes_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        return await self.tools.extract_classes_from_file(file_path)
        
    async def get_file_dependencies(self, file_path: str) -> List[str]:
        return await self.tools.get_file_dependencies(file_path)
        
    async def find_similar_code(self, code_snippet: str, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        return await self.tools.find_similar_code(code_snippet, similarity_threshold)
        
    async def get_workspace_statistics(self) -> Dict[str, Any]:
        return await self.tools.get_workspace_statistics()
        
    async def backup_workspace(self, backup_path: str) -> bool:
        return await self.tools.backup_workspace(backup_path)
        
    async def restore_workspace(self, backup_path: str) -> bool:
        return await self.tools.restore_workspace(backup_path)
        
    async def get_tools_status(self) -> Dict[str, Any]:
        return await self.tools.get_tools_status()
        
    async def get_progress_status(self) -> Dict[str, Any]:
        return await self.tools.get_progress_status()
        
    async def get_performance_metrics(self) -> Dict[str, Any]:
        return await self.tools.get_performance_metrics()
        
    async def process_large_content(self, content: str, content_type: str = "text", language: str = "python") -> List[Dict[str, Any]]:
        if content_type == "code":
            return await self.chunk_code(content, language, {"agent": self.name, "timestamp": datetime.now().isoformat()})
        else:
            return await self.chunk_text(content, {"agent": self.name, "timestamp": datetime.now().isoformat()})
            
    async def intelligent_file_search(self, query: str, search_type: str = "content") -> List[Dict[str, Any]]:
        if search_type == "function":
            return await self.find_function(query)
        elif search_type == "class":
            return await self.find_class(query)
        elif search_type == "pattern":
            return await self.find_by_pattern(query)
        else:
            return await self.search_files(query)
            
    async def get_comprehensive_file_analysis(self, file_path: str) -> Dict[str, Any]:
        analysis = await self.analyze_file(file_path)
        if not analysis:
            return {}
            
        file_info = await self.get_file_info(file_path)
        dependencies = await self.get_file_dependencies(file_path)
        
        return {
            "file_analysis": analysis,
            "file_info": file_info,
            "dependencies": dependencies,
            "functions_count": len(analysis.get("functions", [])),
            "classes_count": len(analysis.get("classes", [])),
            "complexity_score": analysis.get("complexity_score", 0)
        }
        
    async def smart_code_generation(self, prompt: str, file_path: str, language: str = "python") -> bool:
        cached_result = await self.cache_get(f"code_gen:{hash(prompt)}")
        if cached_result:
            return await self.write_file(file_path, cached_result)
            
        similar_code = await self.find_similar_code(prompt, 0.5)
        
        context = {
            "prompt": prompt,
            "similar_code": similar_code[:3],
            "file_path": file_path,
            "language": language,
            "project_summary": await self.get_project_summary()
        }
        
        await self.cache_set(f"code_context:{hash(prompt)}", context, ttl_seconds=3600)
        
        return True 