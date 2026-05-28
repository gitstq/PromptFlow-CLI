"""
Core engine for PromptFlow-CLI

Provides the main PromptFlow class that orchestrates all operations.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from promptflow.models import (
    Config,
    ExecutionResult,
    LLMProvider,
    Prompt,
    PromptCategory,
    PromptVariable,
    PromptVersion,
    Workflow,
    WorkflowStep,
    WorkflowStepType,
)
from promptflow.storage import Storage


class PromptFlow:
    """
    Main PromptFlow engine class
    
    Provides high-level API for managing prompts, workflows, and executions.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage = Storage(storage_path)
        self.config = self.storage.load_config()
        self._execution_history: List[Dict[str, Any]] = []

    # ==================== Prompt Management ====================

    def create_prompt(
        self,
        name: str,
        content: str,
        description: str = "",
        category: PromptCategory = PromptCategory.GENERAL,
        variables: Optional[List[PromptVariable]] = None,
        tags: Optional[List[str]] = None,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Prompt:
        """Create a new prompt"""
        prompt = Prompt(
            name=name,
            content=content,
            description=description,
            category=category,
            variables=variables or [],
            tags=tags or [],
            provider=provider or self.config.default_provider,
            model=model or self.config.default_model,
            temperature=temperature or self.config.default_temperature,
            max_tokens=max_tokens or self.config.default_max_tokens,
        )
        self.storage.save_prompt(prompt)
        return prompt

    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Get a prompt by ID"""
        return self.storage.load_prompt(prompt_id)

    def get_prompt_by_name(self, name: str) -> Optional[Prompt]:
        """Get a prompt by name"""
        prompts = self.storage.list_prompts(search=name)
        for prompt in prompts:
            if prompt.name == name:
                return prompt
        return None

    def update_prompt(
        self,
        prompt_id: str,
        content: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs,
    ) -> Optional[Prompt]:
        """Update a prompt"""
        prompt = self.storage.load_prompt(prompt_id)
        if not prompt:
            return None

        if name is not None:
            prompt.name = name
        if description is not None:
            prompt.description = description
        if tags is not None:
            prompt.tags = tags

        # Handle content update with versioning
        if content is not None and content != prompt.content:
            if self.config.auto_version:
                prompt.add_version(
                    content=content,
                    message=kwargs.get("version_message", "Updated content"),
                )
            else:
                prompt.content = content

        prompt.updated_at = datetime.now().isoformat()
        self.storage.save_prompt(prompt)
        return prompt

    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt"""
        return self.storage.delete_prompt(prompt_id)

    def list_prompts(
        self,
        category: Optional[PromptCategory] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
    ) -> List[Prompt]:
        """List prompts with optional filtering"""
        return self.storage.list_prompts(category=category, tags=tags, search=search)

    # ==================== Version Control ====================

    def add_prompt_version(
        self,
        prompt_id: str,
        content: str,
        message: str = "",
        author: str = "",
        tags: Optional[List[str]] = None,
    ) -> Optional[PromptVersion]:
        """Add a new version to a prompt"""
        prompt = self.storage.load_prompt(prompt_id)
        if not prompt:
            return None

        version = prompt.add_version(
            content=content,
            message=message,
            author=author,
            tags=tags,
        )
        self.storage.save_prompt(prompt)
        return version

    def get_prompt_versions(self, prompt_id: str) -> List[PromptVersion]:
        """Get all versions of a prompt"""
        prompt = self.storage.load_prompt(prompt_id)
        if not prompt:
            return []
        return prompt.versions

    def rollback_prompt(self, prompt_id: str, version: str) -> bool:
        """Rollback a prompt to a specific version"""
        prompt = self.storage.load_prompt(prompt_id)
        if not prompt:
            return False

        if prompt.rollback(version):
            self.storage.save_prompt(prompt)
            return True
        return False

    def diff_prompt_versions(
        self, prompt_id: str, version1: str, version2: str
    ) -> Dict[str, str]:
        """Compare two versions of a prompt"""
        prompt = self.storage.load_prompt(prompt_id)
        if not prompt:
            return {}

        v1 = prompt.get_version(version1)
        v2 = prompt.get_version(version2)

        if not v1 or not v2:
            return {}

        return {
            "version1": version1,
            "version2": version2,
            "content1": v1.content,
            "content2": v2.content,
            "message1": v1.message,
            "message2": v2.message,
            "created_at1": v1.created_at,
            "created_at2": v2.created_at,
        }

    # ==================== Workflow Management ====================

    def create_workflow(
        self,
        name: str,
        description: str = "",
        variables: Optional[Dict[str, Any]] = None,
    ) -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(
            name=name,
            description=description,
            variables=variables or {},
        )
        self.storage.save_workflow(workflow)
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID"""
        return self.storage.load_workflow(workflow_id)

    def add_workflow_step(
        self,
        workflow_id: str,
        name: str,
        type: WorkflowStepType = WorkflowStepType.PROMPT,
        prompt_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[WorkflowStep]:
        """Add a step to a workflow"""
        workflow = self.storage.load_workflow(workflow_id)
        if not workflow:
            return None

        step = workflow.add_step(
            name=name,
            type=type,
            prompt_id=prompt_id,
            config=config or {},
            **kwargs,
        )
        self.storage.save_workflow(workflow)
        return step

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        return self.storage.delete_workflow(workflow_id)

    def list_workflows(self, search: Optional[str] = None) -> List[Workflow]:
        """List workflows"""
        return self.storage.list_workflows(search=search)

    # ==================== Execution ====================

    def execute_prompt(
        self,
        prompt_id: str,
        variables: Optional[Dict[str, str]] = None,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> ExecutionResult:
        """
        Execute a prompt with an LLM
        
        Note: This is a simulation. In production, it would call actual LLM APIs.
        """
        prompt = self.storage.load_prompt(prompt_id)
        if not prompt:
            return ExecutionResult(
                success=False,
                error=f"Prompt not found: {prompt_id}",
            )

        start_time = time.time()

        # Render the prompt with variables
        rendered_content = prompt.render(variables)

        # Get execution parameters
        exec_provider = provider or prompt.provider or self.config.default_provider
        exec_model = model or prompt.model or self.config.default_model
        exec_temperature = temperature or prompt.temperature or self.config.default_temperature
        exec_max_tokens = max_tokens or prompt.max_tokens or self.config.default_max_tokens

        # Simulate execution (in production, call actual LLM API)
        # This is a placeholder that returns a simulated response
        simulated_output = self._simulate_llm_response(
            rendered_content,
            exec_provider,
            exec_model,
        )

        duration_ms = int((time.time() - start_time) * 1000)

        result = ExecutionResult(
            success=True,
            output=simulated_output,
            tokens_used=len(rendered_content.split()) + len(simulated_output.split()),
            duration_ms=duration_ms,
            model=exec_model,
            provider=exec_provider.value,
            metadata={
                "prompt_id": prompt_id,
                "variables": variables,
                "temperature": exec_temperature,
                "max_tokens": exec_max_tokens,
            },
        )

        # Record execution
        self._record_execution(result)

        return result

    def execute_workflow(
        self,
        workflow_id: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, ExecutionResult]:
        """
        Execute a workflow
        
        Note: This is a simulation. In production, it would orchestrate actual executions.
        """
        workflow = self.storage.load_workflow(workflow_id)
        if not workflow:
            return {"error": ExecutionResult(success=False, error="Workflow not found")}

        results: Dict[str, ExecutionResult] = {}
        context: Dict[str, Any] = {**(workflow.variables), **(variables or {})}

        for step in workflow.steps:
            if step.type == WorkflowStepType.PROMPT and step.prompt_id:
                # Execute prompt step
                result = self.execute_prompt(
                    step.prompt_id,
                    variables=context,
                )
                results[step.id] = result

                # Update context with output
                if result.success:
                    context[f"step_{step.id}_output"] = result.output

            elif step.type == WorkflowStepType.TRANSFORM:
                # Transform step (placeholder)
                results[step.id] = ExecutionResult(
                    success=True,
                    output="[Transform step executed]",
                    metadata={"step_type": "transform"},
                )

            elif step.type == WorkflowStepType.CONDITION:
                # Conditional step (placeholder)
                results[step.id] = ExecutionResult(
                    success=True,
                    output="[Condition evaluated]",
                    metadata={"step_type": "condition"},
                )

        return results

    def _simulate_llm_response(
        self,
        prompt_content: str,
        provider: LLMProvider,
        model: str,
    ) -> str:
        """Simulate LLM response for testing"""
        # This is a placeholder simulation
        # In production, this would call actual LLM APIs
        return f"[Simulated response from {provider.value}/{model}]\n\nBased on your prompt, here's a simulated response. In production, this would be the actual LLM output.\n\nPrompt length: {len(prompt_content)} characters"

    def _record_execution(self, result: ExecutionResult) -> None:
        """Record execution in history"""
        self._execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "result": result.to_dict(),
        })

    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self._execution_history[-limit:]

    # ==================== Configuration ====================

    def update_config(self, **kwargs) -> Config:
        """Update configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.storage.save_config(self.config)
        return self.config

    def set_api_key(self, provider: LLMProvider, api_key: str) -> None:
        """Set API key for a provider"""
        self.config.api_keys[provider.value] = api_key

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        stats = self.storage.get_stats()
        stats["executions_count"] = len(self._execution_history)
        return stats

    # ==================== Import/Export ====================

    def export_data(self, export_path: str) -> None:
        """Export all data"""
        self.storage.export_all(export_path)

    def import_data(
        self,
        import_path: str,
        merge: bool = True,
    ) -> Dict[str, int]:
        """Import data"""
        return self.storage.import_all(import_path, merge=merge)

    def create_backup(self) -> str:
        """Create a backup"""
        return self.storage.create_backup()

    def list_backups(self) -> List[Dict[str, Any]]:
        """List backups"""
        return self.storage.list_backups()

    def restore_backup(self, backup_name: str) -> bool:
        """Restore from backup"""
        return self.storage.restore_backup(backup_name)
