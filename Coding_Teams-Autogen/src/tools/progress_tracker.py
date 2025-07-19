import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
import statistics

console = Console()

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskProgress:
    task_id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    total_work: float = 100.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_duration: Optional[timedelta] = None
    actual_duration: Optional[timedelta] = None
    parent_task_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_completion_percentage(self) -> float:
        return (self.progress / self.total_work) * 100 if self.total_work > 0 else 0
        
    def get_elapsed_time(self) -> Optional[timedelta]:
        if self.start_time:
            end_time = self.end_time or datetime.now()
            return end_time - self.start_time
        return None
        
    def get_estimated_remaining_time(self) -> Optional[timedelta]:
        if not self.start_time or self.progress <= 0:
            return self.estimated_duration
            
        elapsed = self.get_elapsed_time()
        if not elapsed:
            return None
            
        completion_rate = self.progress / elapsed.total_seconds()
        remaining_work = self.total_work - self.progress
        
        if completion_rate > 0:
            estimated_remaining_seconds = remaining_work / completion_rate
            return timedelta(seconds=estimated_remaining_seconds)
            
        return None
        
    def update_progress(self, progress: float, message: str = None):
        self.progress = min(progress, self.total_work)
        if message:
            self.metadata["last_message"] = message
            self.metadata["last_update"] = datetime.now().isoformat()
            
        if self.progress >= self.total_work and self.status == TaskStatus.RUNNING:
            self.complete()
            
    def start(self):
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.now()
        
    def complete(self):
        self.status = TaskStatus.COMPLETED
        self.end_time = datetime.now()
        self.progress = self.total_work
        if self.start_time:
            self.actual_duration = self.end_time - self.start_time
            
    def fail(self, error_message: str = None):
        self.status = TaskStatus.FAILED
        self.end_time = datetime.now()
        if error_message:
            self.metadata["error"] = error_message
            
    def cancel(self):
        self.status = TaskStatus.CANCELLED
        self.end_time = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "progress": self.progress,
            "total_work": self.total_work,
            "completion_percentage": self.get_completion_percentage(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "estimated_duration": self.estimated_duration.total_seconds() if self.estimated_duration else None,
            "actual_duration": self.actual_duration.total_seconds() if self.actual_duration else None,
            "elapsed_time": self.get_elapsed_time().total_seconds() if self.get_elapsed_time() else None,
            "estimated_remaining_time": self.get_estimated_remaining_time().total_seconds() if self.get_estimated_remaining_time() else None,
            "parent_task_id": self.parent_task_id,
            "subtasks": self.subtasks,
            "metadata": self.metadata
        }

class ProgressTracker:
    def __init__(self, enable_ui: bool = True, update_interval: float = 0.5):
        self.tasks: Dict[str, TaskProgress] = {}
        self.enable_ui = enable_ui
        self.update_interval = update_interval
        self.logger = logging.getLogger("progress_tracker")
        
        self.callbacks: Dict[str, List[Callable]] = {
            "task_started": [],
            "task_updated": [],
            "task_completed": [],
            "task_failed": []
        }
        
        self._running = False
        self._ui_task = None
        self._live = None
        
        self.historical_data: List[Dict[str, Any]] = []
        
    def add_callback(self, event: str, callback: Callable):
        if event in self.callbacks:
            self.callbacks[event].append(callback)
            
    def remove_callback(self, event: str, callback: Callable):
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)
            
    def _trigger_callbacks(self, event: str, task: TaskProgress):
        for callback in self.callbacks.get(event, []):
            try:
                callback(task)
            except Exception as e:
                self.logger.error(f"Error in callback for {event}: {e}")
                
    def create_task(self, task_id: str, name: str, description: str = "", 
                   total_work: float = 100.0, estimated_duration: Optional[timedelta] = None,
                   parent_task_id: Optional[str] = None) -> TaskProgress:
        task = TaskProgress(
            task_id=task_id,
            name=name,
            description=description,
            total_work=total_work,
            estimated_duration=estimated_duration,
            parent_task_id=parent_task_id
        )
        
        self.tasks[task_id] = task
        
        if parent_task_id and parent_task_id in self.tasks:
            self.tasks[parent_task_id].subtasks.append(task_id)
            
        self.logger.info(f"Created task: {task_id} - {name}")
        return task
        
    def start_task(self, task_id: str) -> bool:
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        task.start()
        self._trigger_callbacks("task_started", task)
        self.logger.info(f"Started task: {task_id}")
        return True
        
    def update_task(self, task_id: str, progress: float, message: str = None) -> bool:
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        old_progress = task.progress
        task.update_progress(progress, message)
        
        if task.status == TaskStatus.COMPLETED and old_progress < task.total_work:
            self._trigger_callbacks("task_completed", task)
            self.logger.info(f"Completed task: {task_id}")
        else:
            self._trigger_callbacks("task_updated", task)
            
        return True
        
    def complete_task(self, task_id: str) -> bool:
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        task.complete()
        self._trigger_callbacks("task_completed", task)
        self.logger.info(f"Completed task: {task_id}")
        return True
        
    def fail_task(self, task_id: str, error_message: str = None) -> bool:
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        task.fail(error_message)
        self._trigger_callbacks("task_failed", task)
        self.logger.error(f"Failed task: {task_id} - {error_message}")
        return True
        
    def cancel_task(self, task_id: str) -> bool:
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        task.cancel()
        self.logger.info(f"Cancelled task: {task_id}")
        return True
        
    def get_task(self, task_id: str) -> Optional[TaskProgress]:
        return self.tasks.get(task_id)
        
    def get_all_tasks(self) -> List[TaskProgress]:
        return list(self.tasks.values())
        
    def get_active_tasks(self) -> List[TaskProgress]:
        return [task for task in self.tasks.values() if task.status == TaskStatus.RUNNING]
        
    def get_completed_tasks(self) -> List[TaskProgress]:
        return [task for task in self.tasks.values() if task.status == TaskStatus.COMPLETED]
        
    def get_failed_tasks(self) -> List[TaskProgress]:
        return [task for task in self.tasks.values() if task.status == TaskStatus.FAILED]
        
    def get_overall_progress(self) -> Dict[str, Any]:
        if not self.tasks:
            return {
                "overall_completion": 0.0,
                "active_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "total_tasks": 0
            }
            
        total_tasks = len(self.tasks)
        completed_tasks = len(self.get_completed_tasks())
        failed_tasks = len(self.get_failed_tasks())
        active_tasks = len(self.get_active_tasks())
        
        overall_completion = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        return {
            "overall_completion": overall_completion,
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "total_tasks": total_tasks
        }
        
    def estimate_total_completion_time(self) -> Optional[timedelta]:
        active_tasks = self.get_active_tasks()
        if not active_tasks:
            return None
            
        remaining_times = []
        for task in active_tasks:
            remaining_time = task.get_estimated_remaining_time()
            if remaining_time:
                remaining_times.append(remaining_time.total_seconds())
                
        if remaining_times:
            max_remaining = max(remaining_times)
            return timedelta(seconds=max_remaining)
            
        return None
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        completed_tasks = self.get_completed_tasks()
        
        if not completed_tasks:
            return {
                "average_completion_time": 0,
                "median_completion_time": 0,
                "fastest_completion_time": 0,
                "slowest_completion_time": 0,
                "accuracy_rate": 0
            }
            
        completion_times = [
            task.actual_duration.total_seconds() 
            for task in completed_tasks 
            if task.actual_duration
        ]
        
        if completion_times:
            avg_time = statistics.mean(completion_times)
            median_time = statistics.median(completion_times)
            fastest_time = min(completion_times)
            slowest_time = max(completion_times)
        else:
            avg_time = median_time = fastest_time = slowest_time = 0
            
        total_tasks = len(self.tasks)
        failed_tasks = len(self.get_failed_tasks())
        accuracy_rate = ((total_tasks - failed_tasks) / total_tasks) * 100 if total_tasks > 0 else 0
        
        return {
            "average_completion_time": avg_time,
            "median_completion_time": median_time,
            "fastest_completion_time": fastest_time,
            "slowest_completion_time": slowest_time,
            "accuracy_rate": accuracy_rate
        }
        
    async def start_ui(self):
        if not self.enable_ui or self._running:
            return
            
        self._running = True
        self._ui_task = asyncio.create_task(self._ui_loop())
        
    async def stop_ui(self):
        if not self._running:
            return
            
        self._running = False
        
        if self._ui_task:
            self._ui_task.cancel()
            try:
                await self._ui_task
            except asyncio.CancelledError:
                pass
                
        if self._live:
            self._live.stop()
            
    async def _ui_loop(self):
        try:
            with Live(self._generate_ui(), refresh_per_second=2, console=console) as live:
                self._live = live
                while self._running:
                    live.update(self._generate_ui())
                    await asyncio.sleep(self.update_interval)
        except asyncio.CancelledError:
            pass
            
    def _generate_ui(self) -> Panel:
        table = Table(title="Task Progress")
        table.add_column("Task ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Progress", style="blue")
        table.add_column("Elapsed", style="yellow")
        table.add_column("Remaining", style="red")
        
        for task in self.tasks.values():
            status_emoji = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.RUNNING: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.CANCELLED: "🚫"
            }.get(task.status, "❓")
            
            progress_bar = f"{task.get_completion_percentage():.1f}%"
            elapsed = task.get_elapsed_time()
            elapsed_str = f"{elapsed.total_seconds():.1f}s" if elapsed else "N/A"
            
            remaining = task.get_estimated_remaining_time()
            remaining_str = f"{remaining.total_seconds():.1f}s" if remaining else "N/A"
            
            table.add_row(
                task.task_id[:10],
                task.name[:20],
                f"{status_emoji} {task.status.value}",
                progress_bar,
                elapsed_str,
                remaining_str
            )
            
        overall = self.get_overall_progress()
        metrics = self.get_performance_metrics()
        
        summary = f"""
Overall Progress: {overall['overall_completion']:.1f}%
Active Tasks: {overall['active_tasks']}
Completed Tasks: {overall['completed_tasks']}
Failed Tasks: {overall['failed_tasks']}
Total Tasks: {overall['total_tasks']}

Performance Metrics:
Average Completion Time: {metrics['average_completion_time']:.1f}s
Accuracy Rate: {metrics['accuracy_rate']:.1f}%
"""
        
        return Panel(f"{table}\n{summary}", title="Progress Tracker", border_style="blue")
        
    async def save_progress_report(self, file_path: str):
        report = {
            "timestamp": datetime.now().isoformat(),
            "tasks": [task.to_dict() for task in self.tasks.values()],
            "overall_progress": self.get_overall_progress(),
            "performance_metrics": self.get_performance_metrics(),
            "historical_data": self.historical_data
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"Progress report saved to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving progress report: {e}")
            return False
            
    async def load_progress_report(self, file_path: str):
        try:
            with open(file_path, 'r') as f:
                report = json.load(f)
                
            for task_data in report.get("tasks", []):
                task = TaskProgress(
                    task_id=task_data["task_id"],
                    name=task_data["name"],
                    description=task_data["description"],
                    status=TaskStatus(task_data["status"]),
                    progress=task_data["progress"],
                    total_work=task_data["total_work"],
                    parent_task_id=task_data.get("parent_task_id"),
                    subtasks=task_data.get("subtasks", []),
                    metadata=task_data.get("metadata", {})
                )
                
                if task_data.get("start_time"):
                    task.start_time = datetime.fromisoformat(task_data["start_time"])
                if task_data.get("end_time"):
                    task.end_time = datetime.fromisoformat(task_data["end_time"])
                if task_data.get("estimated_duration"):
                    task.estimated_duration = timedelta(seconds=task_data["estimated_duration"])
                if task_data.get("actual_duration"):
                    task.actual_duration = timedelta(seconds=task_data["actual_duration"])
                    
                self.tasks[task.task_id] = task
                
            self.historical_data = report.get("historical_data", [])
            self.logger.info(f"Progress report loaded from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading progress report: {e}")
            return False 