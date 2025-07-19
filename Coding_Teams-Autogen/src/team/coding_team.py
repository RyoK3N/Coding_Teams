import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from src.agents.base_agent import BaseAgent, MessageTag
from src.agents.principle_software_engineer import PrincipleSoftwareEngineer
from src.agents.smart_coding_agent import SmartCodingAgent
from src.agents.requirements_analyst import RequirementsAnalyst
from src.workspace.workspace_manager import WorkspaceManager
from src.tools.agent_tools import AgentTools

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class TeamState(Enum):
    INITIALIZING = "INITIALIZING"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"

@dataclass
class CodingTeamConfig:
    claude_config: Dict[str, Any]
    output_directory: str = "output"
    log_level: str = "INFO"
    max_escalation_attempts: int = 3
    step_timeout_minutes: int = 10
    enable_rich_ui: bool = True
    enable_caching: bool = True
    cache_write_cycle_minutes: int = 5
    enable_progress_tracking: bool = True
    enable_code_analysis: bool = True
    batch_processing_size: int = 3
    enable_streaming: bool = True

class CodingTeam:
    def __init__(self, config: CodingTeamConfig):
        self.config = config
        self.state = TeamState.INITIALIZING
        self.agents: Dict[str, BaseAgent] = {}
        self.principle_engineer: Optional[PrincipleSoftwareEngineer] = None
        self.work_packages: List[Dict[str, Any]] = []
        self.completed_packages: List[str] = []
        self.message_history: List[Dict[str, Any]] = []
        self.escalation_count = 0
        self.start_time = datetime.now()
        
        self.setup_logging()
        self.logger = logging.getLogger("coding_team")
        
        workspace_path = os.path.join(self.config.output_directory, "workspace")
        cache_path = os.path.join(self.config.output_directory, "cache")
        
        self.workspace_manager = WorkspaceManager(workspace_path)
        self.agent_tools = AgentTools(workspace_path, cache_path)
        
        os.makedirs(self.config.output_directory, exist_ok=True)
        
    def setup_logging(self):
        os.makedirs(self.config.output_directory, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{self.config.output_directory}/team.log"),
                logging.StreamHandler()
            ]
        )
        
    async def initialize_team(self):
        await self.agent_tools.initialize()
        
        workspace_path = os.path.join(self.config.output_directory, "workspace")
        
        # Initialize Principle Software Engineer
        self.principle_engineer = PrincipleSoftwareEngineer(
            self.config.claude_config,
            self.workspace_manager,
            self.agent_tools
        )
        
        # Initialize Smart Coding Agents
        self.agents = {
            "backend_specialist": SmartCodingAgent(
                name="backend_specialist",
                role="Backend Specialist",
                specialization="backend development, APIs, databases, server-side logic",
                claude_config=self.config.claude_config,
                workspace_path=workspace_path,
                tools=self.agent_tools
            ),
            "frontend_specialist": SmartCodingAgent(
                name="frontend_specialist", 
                role="Frontend Specialist",
                specialization="user interfaces, web development, responsive design, JavaScript",
                claude_config=self.config.claude_config,
                workspace_path=workspace_path,
                tools=self.agent_tools
            ),
            "fullstack_specialist": SmartCodingAgent(
                name="fullstack_specialist",
                role="Fullstack Specialist", 
                specialization="full-stack development, integration, end-to-end solutions",
                claude_config=self.config.claude_config,
                workspace_path=workspace_path,
                tools=self.agent_tools
            ),
            "ml_specialist": SmartCodingAgent(
                name="ml_specialist",
                role="ML Specialist",
                specialization="machine learning, data processing, neural networks, AI models",
                claude_config=self.config.claude_config,
                workspace_path=workspace_path,
                tools=self.agent_tools
            ),
            "devops_specialist": SmartCodingAgent(
                name="devops_specialist",
                role="DevOps Specialist",
                specialization="deployment, infrastructure, CI/CD, containerization, cloud",
                claude_config=self.config.claude_config,
                workspace_path=workspace_path,
                tools=self.agent_tools
            ),
            "qa_specialist": SmartCodingAgent(
                name="qa_specialist",
                role="QA Specialist",
                specialization="testing, quality assurance, test automation, validation",
                claude_config=self.config.claude_config,
                workspace_path=workspace_path,
                tools=self.agent_tools
            ),
            "requirements_analyst": RequirementsAnalyst(
                self.config.claude_config,
                self.workspace_manager,
                self.agent_tools
            )
        }
        
        # Initialize all agents
        await self.principle_engineer.initialize_tools()
        for agent in self.agents.values():
            await agent.initialize_tools()
        
        self.logger.info(f"Initialized Principle Engineer and {len(self.agents)} smart coding agents")
        
    async def shutdown_team(self):
        if self.principle_engineer:
            await self.principle_engineer.shutdown_tools()
            
        for agent in self.agents.values():
            await agent.shutdown_tools()
        
        await self.agent_tools.shutdown()
        self.logger.info("Team shutdown completed")
        
    async def solve_problem(self, problem_statement: str) -> Dict[str, Any]:
        self.state = TeamState.ANALYZING
        
        try:
            await self.initialize_team()
            
            if self.config.enable_rich_ui:
                await self._display_team_initialization()
            
            # Create minimal workspace (no predefined structure)
            await self.workspace_manager.initialize_workspace()
            
            project_task_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            await self.agent_tools.create_progress_task(
                project_task_id,
                "Solve Software Problem",
                f"Problem: {problem_statement[:100]}...",
                estimated_duration=timedelta(hours=1)
            )
            await self.agent_tools.start_progress_task(project_task_id)
            
            # Step 1: Principle Engineer analyzes problem and creates work packages
            await self.analyze_problem_systematically(problem_statement)
            await self.update_project_progress(30, "Problem analyzed and work packages created")
            
            # Step 2: Execute work packages with appropriate agents
            await self.execute_work_packages()
            await self.update_project_progress(90, "All work packages completed")
            
            # Step 3: Generate final report
            final_report = await self.generate_final_report()
            await self.update_project_progress(100, "Final report generated")
            
            await self.agent_tools.complete_progress_task(project_task_id)
            
            self.state = TeamState.COMPLETED
            return final_report
            
        except Exception as e:
            self.state = TeamState.FAILED
            self.logger.error(f"Project failed: {str(e)}")
            if hasattr(self, 'project_task_id'):
                await self.agent_tools.fail_progress_task(project_task_id, str(e))
            raise
        finally:
            await self.shutdown_team()
            
    async def _display_team_initialization(self):
        if not self.config.enable_rich_ui:
            return
            
        console.print(Panel(
            f"[bold blue]🧠 Intelligent Multi-Agent Coding Team[/bold blue]\n\n"
            f"[bold]New Architecture:[/bold]\n"
            f"• Principle Software Engineer: Problem analysis & coordination\n"
            f"• Smart Coding Agents: Dynamic code generation\n"
            f"• No Hardcoded Templates: Every solution is custom\n"
            f"• Minimal File Structure: Only what's needed\n"
            f"• Function-Level Design: Precise specifications\n\n"
            f"[bold]Features:[/bold]\n"
            f"• Real-time Progress Tracking: {self.config.enable_progress_tracking}\n"
            f"• Intelligent Caching: {self.config.enable_caching}\n"
            f"• Code Analysis: {self.config.enable_code_analysis}\n"
            f"• Batch Processing: {self.config.batch_processing_size} concurrent tasks\n\n"
            f"[bold]Team:[/bold] Principle Engineer + {len(self.agents)} specialists\n"
            f"[bold]Workspace:[/bold] {self.workspace_manager.workspace_path}",
            title="🎯 Next-Generation Software Engineering Team",
            border_style="blue"
        ))
        
    async def update_project_progress(self, progress: float, message: str):
        if hasattr(self, 'project_task_id'):
            await self.agent_tools.update_progress_task(self.project_task_id, progress, message)
            
    async def analyze_problem_systematically(self, problem_statement: str) -> None:
        self.state = TeamState.ANALYZING
        self.logger.info("Starting systematic problem analysis")
        
        # Principle Engineer analyzes the problem and creates work packages
        await self.principle_engineer.execute_step({
            "action": "solve_problem_systematically",
            "problem_statement": problem_statement
        })
        
        # Get the created work packages
        self.work_packages = self.principle_engineer.work_packages
        
        if not self.work_packages:
            raise Exception("No work packages were created by the Principle Engineer")
            
        # Save work packages for reference
        work_packages_file = f"{self.config.output_directory}/work_packages.json"
        with open(work_packages_file, 'w') as f:
            json.dump({"work_packages": self.work_packages}, f, indent=2)
            
        self.logger.info(f"Problem analysis completed: {len(self.work_packages)} work packages created")
        
    async def execute_work_packages(self) -> None:
        self.state = TeamState.EXECUTING
        self.logger.info(f"Executing {len(self.work_packages)} work packages")
        
        if self.config.enable_rich_ui:
            await self._display_work_packages()
        
        # Execute work packages respecting dependencies
        while len(self.completed_packages) < len(self.work_packages):
            # Get next available packages (dependencies satisfied)
            available_packages = self._get_available_packages()
            
            if not available_packages:
                blocked_packages = [wp for wp in self.work_packages if wp["package_id"] not in self.completed_packages]
                self.logger.error(f"No available packages found. Blocked: {[wp['package_id'] for wp in blocked_packages]}")
                break
                
            # Execute packages in batch
            batch_size = min(len(available_packages), self.config.batch_processing_size)
            batch = available_packages[:batch_size]
            
            self.logger.info(f"Executing batch of {len(batch)} packages: {[p['package_id'] for p in batch]}")
            
            # Execute batch in parallel
            tasks = [self._execute_single_package(package) for package in batch]
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                self.logger.error(f"Batch execution error: {e}")
                
        self.logger.info(f"Work package execution completed: {len(self.completed_packages)}/{len(self.work_packages)} packages completed")
        
    def _get_available_packages(self) -> List[Dict[str, Any]]:
        """Get work packages that can be executed (all dependencies completed)"""
        available = []
        
        for package in self.work_packages:
            if package["package_id"] in self.completed_packages:
                continue
                
            # Check if all dependencies are completed
            dependencies = package.get("dependencies", [])
            if all(dep in self.completed_packages for dep in dependencies):
                available.append(package)
                
        return available
        
    async def _execute_single_package(self, package: Dict[str, Any]) -> None:
        """Execute a single work package"""
        package_id = package["package_id"]
        agent_name = package.get("agent", "fullstack_specialist")
        
        try:
            # Find appropriate agent
            agent = self._find_agent_for_package(package)
            if not agent:
                self.logger.error(f"No suitable agent found for package {package_id}")
                return
                
            # Execute the work package
            await agent.execute_step({"work_package": package})
            
            # Mark as completed
            self.completed_packages.append(package_id)
            self.logger.info(f"Package {package_id} completed successfully by {agent.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to execute package {package_id}: {str(e)}")
            # Don't add to completed packages if failed
            
    def _find_agent_for_package(self, package: Dict[str, Any]) -> Optional[BaseAgent]:
        """Find the most appropriate agent for a work package"""
        agent_name = package.get("agent", "")
        
        # Direct agent mapping
        agent_mapping = {
            "backend_engineer": "backend_specialist",
            "frontend_engineer": "frontend_specialist", 
            "fullstack_engineer": "fullstack_specialist",
            "ml_engineer": "ml_specialist",
            "devops_engineer": "devops_specialist",
            "qa_engineer": "qa_specialist",
            "requirements_analyst": "requirements_analyst"
        }
        
        # Try direct mapping first
        mapped_name = agent_mapping.get(agent_name, agent_name)
        if mapped_name in self.agents:
            return self.agents[mapped_name]
            
        # Fallback based on file types in the package
        files_to_create = package.get("files_to_create", [])
        file_types = [self._get_file_type(f.get("file_path", "")) for f in files_to_create]
        
        if any(ft in ["python", "api"] for ft in file_types):
            return self.agents.get("backend_specialist")
        elif any(ft in ["html", "css", "javascript"] for ft in file_types):
            return self.agents.get("frontend_specialist")
        elif any(ft in ["ml", "data"] for ft in file_types):
            return self.agents.get("ml_specialist")
        elif any(ft in ["docker", "deploy"] for ft in file_types):
            return self.agents.get("devops_specialist")
        elif any(ft in ["test"] for ft in file_types):
            return self.agents.get("qa_specialist")
        else:
            # Default to fullstack specialist
            return self.agents.get("fullstack_specialist")
            
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type category from file path"""
        if not file_path:
            return "unknown"
            
        path_lower = file_path.lower()
        
        if any(x in path_lower for x in ["test", "spec"]):
            return "test"
        elif path_lower.endswith((".py", ".pyx")):
            return "python"
        elif path_lower.endswith((".js", ".ts", ".jsx", ".tsx")):
            return "javascript"
        elif path_lower.endswith((".html", ".htm")):
            return "html"
        elif path_lower.endswith((".css", ".scss", ".sass")):
            return "css"
        elif path_lower.endswith((".json", ".yaml", ".yml")):
            return "config"
        elif any(x in path_lower for x in ["docker", "deploy", "ci", "cd"]):
            return "deploy"
        elif any(x in path_lower for x in ["ml", "model", "train", "predict", "data"]):
            return "ml"
        elif any(x in path_lower for x in ["api", "server", "backend"]):
            return "api"
        else:
            return "generic"
            
    async def _display_work_packages(self):
        if not self.config.enable_rich_ui:
            return
            
        table = Table(title="Work Packages")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="magenta")
        table.add_column("Agent", style="green")
        table.add_column("Files", style="blue")
        table.add_column("Dependencies", style="yellow")
        
        for package in self.work_packages:
            files_count = len(package.get("files_to_create", []))
            deps = ", ".join(package.get("dependencies", [])) or "None"
            
            table.add_row(
                package["package_id"],
                package.get("title", "")[:30],
                package.get("agent", ""),
                str(files_count),
                deps
            )
            
        console.print(table)
        
    async def generate_final_report(self) -> Dict[str, Any]:
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Get design summary from Principle Engineer
        design_summary = self.principle_engineer.get_design_summary() if self.principle_engineer else {}
        
        # Get completion status from all agents
        agent_status = {}
        for name, agent in self.agents.items():
            if hasattr(agent, 'get_completion_status'):
                agent_status[name] = agent.get_completion_status()
                
        # Collect all artifacts
        artifacts = []
        for package in self.work_packages:
            if package["package_id"] in self.completed_packages:
                files = [f.get("file_path") for f in package.get("files_to_create", [])]
                artifacts.extend(files)
                
        workspace_stats = await self.agent_tools.get_workspace_statistics()
        
        report = {
            "problem_analysis": design_summary.get("problem_analysis", {}),
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "final_state": self.state.value,
            "work_packages": {
                "total": len(self.work_packages),
                "completed": len(self.completed_packages),
                "success_rate": len(self.completed_packages) / len(self.work_packages) * 100 if self.work_packages else 0
            },
            "file_generation": {
                "total_files_planned": design_summary.get("total_files", 0),
                "files_created": len(artifacts),
                "artifacts": artifacts
            },
            "team_performance": {
                "agents_used": len([a for a in agent_status.values() if a.get("total_completed", 0) > 0]),
                "agent_status": agent_status
            },
            "workspace_statistics": workspace_stats,
            "complexity_assessment": design_summary.get("complexity_level", "unknown"),
            "escalation_count": self.escalation_count
        }
        
        # Save report
        report_file = f"{self.config.output_directory}/final_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        if self.config.enable_rich_ui:
            await self._display_final_report(report)
            
        return report
        
    async def _display_final_report(self, report: Dict[str, Any]):
        console.print(Panel(
            f"[bold green]🎉 Project Completed Successfully![/bold green]\n\n"
            f"[bold]Duration:[/bold] {report['duration_seconds']:.1f} seconds\n"
            f"[bold]Work Packages:[/bold] {report['work_packages']['completed']}/{report['work_packages']['total']} "
            f"({report['work_packages']['success_rate']:.1f}% success)\n"
            f"[bold]Files Created:[/bold] {report['file_generation']['files_created']}\n"
            f"[bold]Active Agents:[/bold] {report['team_performance']['agents_used']}\n"
            f"[bold]Complexity:[/bold] {report['complexity_assessment']}\n"
            f"[bold]Total Files:[/bold] {report['workspace_statistics'].get('total_files', 0)}\n"
            f"[bold]Total Lines:[/bold] {report['workspace_statistics'].get('total_lines', 0)}\n\n"
            f"[bold green]✓ Intelligent Problem Analysis[/bold green]\n"
            f"[bold green]✓ Minimal File Structure[/bold green]\n" 
            f"[bold green]✓ Dynamic Code Generation[/bold green]\n"
            f"[bold green]✓ No Hardcoded Templates[/bold green]",
            title="🧠 Intelligent Coding Team Results",
            border_style="green"
        ))
        
    def get_status(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "principle_engineer": self.principle_engineer is not None,
            "smart_agents_count": len(self.agents),
            "work_packages": {
                "total": len(self.work_packages),
                "completed": len(self.completed_packages),
                "remaining": len(self.work_packages) - len(self.completed_packages)
            },
            "escalation_count": self.escalation_count,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "features_enabled": {
                "progress_tracking": self.config.enable_progress_tracking,
                "caching": self.config.enable_caching,
                "code_analysis": self.config.enable_code_analysis,
                "rich_ui": self.config.enable_rich_ui,
                "batch_processing": self.config.batch_processing_size > 1
            }
        } 