import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.agents.base_agent import BaseAgent, MessageTag
from src.project.project_plan import ProjectPlan, ProjectStep
from src.team.coding_team import CodingTeam, CodingTeamConfig

class TestBaseAgent:
    def test_base_agent_initialization(self):
        agent = MockAgent("test_agent", "Test Agent", "Test prompt")
        assert agent.name == "test_agent"
        assert agent.role == "Test Agent"
        assert agent.is_active == True
        assert len(agent.messages) == 0
        
    def test_send_message(self):
        agent = MockAgent("test_agent", "Test Agent", "Test prompt")
        message = agent.send_message(MessageTag.PROGRESS, "Test", "Test content")
        
        assert message.role == "Test Agent"
        assert message.tag == MessageTag.PROGRESS
        assert message.title == "Test"
        assert message.content == "Test content"
        assert len(agent.messages) == 1
        
    def test_terminate(self):
        agent = MockAgent("test_agent", "Test Agent", "Test prompt")
        message = agent.terminate()
        
        assert not agent.is_active
        assert message.tag == MessageTag.AGENT_EXIT

class TestProjectPlan:
    def test_project_plan_creation(self):
        plan = ProjectPlan("Test Project", "Test Description")
        assert plan.project_name == "Test Project"
        assert plan.description == "Test Description"
        assert len(plan.steps) == 0
        
    def test_add_step(self):
        plan = ProjectPlan("Test Project", "Test Description")
        step = ProjectStep("STEP_01", "Test Step", "Test Description", "Test Owner")
        plan.add_step(step)
        
        assert len(plan.steps) == 1
        assert plan.get_step_by_id("STEP_01") == step
        
    def test_get_next_step(self):
        plan = ProjectPlan("Test Project", "Test Description")
        step1 = ProjectStep("STEP_01", "Step 1", "Description", "Owner")
        step2 = ProjectStep("STEP_02", "Step 2", "Description", "Owner", dependencies=["STEP_01"])
        
        plan.add_step(step1)
        plan.add_step(step2)
        
        next_step = plan.get_next_step()
        assert next_step == step1
        
        step1.complete_step()
        next_step = plan.get_next_step()
        assert next_step == step2

class TestCodingTeamConfig:
    def test_config_creation(self):
        config = CodingTeamConfig(
            claude_config={"test": "config"},
            output_directory="test_output",
            log_level="DEBUG"
        )
        
        assert config.claude_config == {"test": "config"}
        assert config.output_directory == "test_output"
        assert config.log_level == "DEBUG"
        assert config.max_escalation_attempts == 3
        assert config.step_timeout_minutes == 30

class MockAgent(BaseAgent):
    def __init__(self, name, role, system_prompt):
        super().__init__(name, role, system_prompt)
        
    def get_success_signal(self):
        return "MOCK_SUCCESS"
        
    def get_termination_signal(self):
        return "MOCK_EXIT"
        
    async def execute_step(self, step_info):
        return self.report_progress("Mock step executed")

if __name__ == "__main__":
    pytest.main([__file__]) 