"""
Tests for PromptFlow-CLI
"""

import pytest
from promptflow.models import (
    Prompt,
    PromptCategory,
    PromptVariable,
    PromptVersion,
    Workflow,
    WorkflowStep,
    WorkflowStepType,
    LLMProvider,
    Config,
)
from promptflow.storage import Storage
from promptflow.core import PromptFlow


class TestModels:
    """Test data models"""

    def test_prompt_creation(self):
        """Test prompt creation"""
        prompt = Prompt(
            name="test-prompt",
            content="Hello {{name}}!",
            description="A test prompt",
        )
        assert prompt.name == "test-prompt"
        assert prompt.content == "Hello {{name}}!"
        assert prompt.category == PromptCategory.GENERAL
        assert len(prompt.versions) == 1

    def test_prompt_render(self):
        """Test prompt variable rendering"""
        prompt = Prompt(
            name="test",
            content="Hello {{name}}, welcome to {{place}}!",
        )
        result = prompt.render({"name": "Alice", "place": "PromptFlow"})
        assert result == "Hello Alice, welcome to PromptFlow!"

    def test_prompt_versioning(self):
        """Test prompt version control"""
        prompt = Prompt(name="test", content="v1")
        assert prompt.current_version == "1.0.0"
        
        prompt.add_version("v2", message="Updated")
        assert prompt.current_version == "1.0.1"
        assert len(prompt.versions) == 2
        
        prompt.rollback("1.0.0")
        assert prompt.current_version == "1.0.0"
        assert prompt.content == "v1"

    def test_prompt_variable(self):
        """Test prompt variables"""
        var = PromptVariable(
            name="topic",
            description="The topic to write about",
            default="AI",
            required=True,
        )
        assert var.name == "topic"
        assert var.default == "AI"

    def test_workflow_creation(self):
        """Test workflow creation"""
        workflow = Workflow(name="test-workflow")
        assert workflow.name == "test-workflow"
        assert len(workflow.steps) == 0

    def test_workflow_add_step(self):
        """Test adding steps to workflow"""
        workflow = Workflow(name="test")
        step = workflow.add_step(
            name="step1",
            type=WorkflowStepType.PROMPT,
            prompt_id="abc123",
        )
        assert len(workflow.steps) == 1
        assert workflow.steps[0].name == "step1"


class TestStorage:
    """Test storage operations"""

    def test_storage_init(self, tmp_path):
        """Test storage initialization"""
        storage = Storage(str(tmp_path / ".promptflow"))
        assert storage.base_path.exists()
        assert (storage.base_path / "prompts").exists()
        assert (storage.base_path / "workflows").exists()

    def test_prompt_save_load(self, tmp_path):
        """Test prompt save and load"""
        storage = Storage(str(tmp_path / ".promptflow"))
        prompt = Prompt(
            id="test123",
            name="test-prompt",
            content="Test content",
        )
        storage.save_prompt(prompt)
        
        loaded = storage.load_prompt("test123")
        assert loaded is not None
        assert loaded.name == "test-prompt"
        assert loaded.content == "Test content"

    def test_prompt_list(self, tmp_path):
        """Test listing prompts"""
        storage = Storage(str(tmp_path / ".promptflow"))
        
        for i in range(3):
            prompt = Prompt(
                id=f"test{i}",
                name=f"prompt-{i}",
                content=f"content-{i}",
            )
            storage.save_prompt(prompt)
        
        prompts = storage.list_prompts()
        assert len(prompts) == 3

    def test_workflow_save_load(self, tmp_path):
        """Test workflow save and load"""
        storage = Storage(str(tmp_path / ".promptflow"))
        workflow = Workflow(
            id="wf123",
            name="test-workflow",
        )
        storage.save_workflow(workflow)
        
        loaded = storage.load_workflow("wf123")
        assert loaded is not None
        assert loaded.name == "test-workflow"


class TestPromptFlow:
    """Test PromptFlow core functionality"""

    def test_create_prompt(self, tmp_path):
        """Test creating a prompt"""
        pf = PromptFlow(storage_path=str(tmp_path / ".promptflow"))
        prompt = pf.create_prompt(
            name="test",
            content="Hello {{name}}!",
        )
        assert prompt.name == "test"
        assert prompt.id is not None

    def test_list_prompts(self, tmp_path):
        """Test listing prompts"""
        pf = PromptFlow(storage_path=str(tmp_path / ".promptflow"))
        
        pf.create_prompt("prompt1", "content1")
        pf.create_prompt("prompt2", "content2")
        
        prompts = pf.list_prompts()
        assert len(prompts) == 2

    def test_update_prompt(self, tmp_path):
        """Test updating a prompt"""
        pf = PromptFlow(storage_path=str(tmp_path / ".promptflow"))
        prompt = pf.create_prompt("test", "original")
        
        updated = pf.update_prompt(prompt.id, content="updated")
        assert updated is not None
        assert updated.content == "updated"
        assert len(updated.versions) == 2

    def test_delete_prompt(self, tmp_path):
        """Test deleting a prompt"""
        pf = PromptFlow(storage_path=str(tmp_path / ".promptflow"))
        prompt = pf.create_prompt("test", "content")
        
        assert pf.delete_prompt(prompt.id)
        assert pf.get_prompt(prompt.id) is None

    def test_execute_prompt(self, tmp_path):
        """Test executing a prompt"""
        pf = PromptFlow(storage_path=str(tmp_path / ".promptflow"))
        prompt = pf.create_prompt("test", "Hello {{name}}!")
        
        result = pf.execute_prompt(prompt.id, variables={"name": "World"})
        assert result.success
        assert "Simulated response" in result.output

    def test_workflow_management(self, tmp_path):
        """Test workflow management"""
        pf = PromptFlow(storage_path=str(tmp_path / ".promptflow"))
        
        workflow = pf.create_workflow("test-workflow")
        assert workflow.name == "test-workflow"
        
        prompt = pf.create_prompt("step1", "Step 1 content")
        step = pf.add_workflow_step(
            workflow.id,
            name="step1",
            prompt_id=prompt.id,
        )
        assert step is not None
        
        loaded = pf.get_workflow(workflow.id)
        assert len(loaded.steps) == 1

    def test_version_control(self, tmp_path):
        """Test version control"""
        pf = PromptFlow(storage_path=str(tmp_path / ".promptflow"))
        prompt = pf.create_prompt("test", "v1")
        
        version = pf.add_prompt_version(prompt.id, "v2", message="Updated")
        assert version.version == "1.0.1"
        
        versions = pf.get_prompt_versions(prompt.id)
        assert len(versions) == 2
        
        assert pf.rollback_prompt(prompt.id, "1.0.0")
        loaded = pf.get_prompt(prompt.id)
        assert loaded.current_version == "1.0.0"

    def test_config(self, tmp_path):
        """Test configuration"""
        pf = PromptFlow(storage_path=str(tmp_path / ".promptflow"))
        
        config = pf.update_config(default_model="gpt-4o")
        assert config.default_model == "gpt-4o"

    def test_stats(self, tmp_path):
        """Test statistics"""
        pf = PromptFlow(storage_path=str(tmp_path / ".promptflow"))
        
        pf.create_prompt("p1", "c1")
        pf.create_prompt("p2", "c2")
        pf.create_workflow("w1")
        
        stats = pf.get_stats()
        assert stats["prompts_count"] == 2
        assert stats["workflows_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
