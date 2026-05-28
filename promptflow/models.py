"""
Data models for PromptFlow-CLI

Defines core data structures for prompts, versions, workflows, and configurations.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class PromptCategory(str, Enum):
    """Prompt category enumeration"""
    CODING = "coding"
    WRITING = "writing"
    ANALYSIS = "analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    CREATIVE = "creative"
    EDUCATION = "education"
    BUSINESS = "business"
    GENERAL = "general"
    CUSTOM = "custom"


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"
    ZHIPU = "zhipu"
    MOONSHOT = "moonshot"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class WorkflowStepType(str, Enum):
    """Workflow step types"""
    PROMPT = "prompt"
    TRANSFORM = "transform"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    HTTP = "http"
    SHELL = "shell"


@dataclass
class PromptVariable:
    """Prompt variable definition"""
    name: str
    description: str = ""
    default: Optional[str] = None
    required: bool = True
    type: str = "string"  # string, number, boolean, list
    options: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "default": self.default,
            "required": self.required,
            "type": self.type,
            "options": self.options,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptVariable":
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            default=data.get("default"),
            required=data.get("required", True),
            type=data.get("type", "string"),
            options=data.get("options", []),
        )


@dataclass
class PromptVersion:
    """Prompt version with full history tracking"""
    version: str
    content: str
    message: str = ""
    author: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Compute SHA256 checksum of content"""
        return hashlib.sha256(self.content.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "content": self.content,
            "message": self.message,
            "author": self.author,
            "created_at": self.created_at,
            "tags": self.tags,
            "metadata": self.metadata,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptVersion":
        return cls(
            version=data["version"],
            content=data["content"],
            message=data.get("message", ""),
            author=data.get("author", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            checksum=data.get("checksum", ""),
        )


@dataclass
class Prompt:
    """
    Core Prompt model with version control support
    
    A prompt can have multiple versions, variables, and metadata.
    Supports template rendering with variable substitution.
    """
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    name: str = ""
    description: str = ""
    category: PromptCategory = PromptCategory.GENERAL
    content: str = ""
    variables: List[PromptVariable] = field(default_factory=list)
    versions: List[PromptVersion] = field(default_factory=list)
    current_version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    provider: Optional[LLMProvider] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.content and not self.versions:
            self.versions.append(PromptVersion(
                version="1.0.0",
                content=self.content,
                message="Initial version",
            ))

    def add_version(
        self,
        content: str,
        message: str = "",
        author: str = "",
        tags: Optional[List[str]] = None,
    ) -> PromptVersion:
        """Add a new version of the prompt"""
        # Calculate new version number
        if self.versions:
            last_version = self.versions[-1].version
            parts = last_version.split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            new_version = ".".join(parts)
        else:
            new_version = "1.0.0"

        version = PromptVersion(
            version=new_version,
            content=content,
            message=message,
            author=author,
            tags=tags or [],
        )
        self.versions.append(version)
        self.content = content
        self.current_version = new_version
        self.updated_at = datetime.now().isoformat()
        return version

    def get_version(self, version: str) -> Optional[PromptVersion]:
        """Get a specific version of the prompt"""
        for v in self.versions:
            if v.version == version:
                return v
        return None

    def rollback(self, version: str) -> bool:
        """Rollback to a specific version"""
        v = self.get_version(version)
        if v:
            self.content = v.content
            self.current_version = version
            self.updated_at = datetime.now().isoformat()
            return True
        return False

    def render(self, variables: Optional[Dict[str, str]] = None) -> str:
        """Render the prompt with variable substitution"""
        result = self.content
        if variables:
            for key, value in variables.items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
                result = result.replace(f"{{{key}}}", str(value))
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "content": self.content,
            "variables": [v.to_dict() for v in self.variables],
            "versions": [v.to_dict() for v in self.versions],
            "current_version": self.current_version,
            "tags": self.tags,
            "provider": self.provider.value if self.provider else None,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prompt":
        return cls(
            id=data.get("id", str(uuid4())[:8]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=PromptCategory(data.get("category", "general")),
            content=data.get("content", ""),
            variables=[PromptVariable.from_dict(v) for v in data.get("variables", [])],
            versions=[PromptVersion.from_dict(v) for v in data.get("versions", [])],
            current_version=data.get("current_version", "1.0.0"),
            tags=data.get("tags", []),
            provider=LLMProvider(data["provider"]) if data.get("provider") else None,
            model=data.get("model"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 4096),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )


@dataclass
class WorkflowStep:
    """A single step in a workflow"""
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    name: str = ""
    type: WorkflowStepType = WorkflowStepType.PROMPT
    prompt_id: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    condition: Optional[str] = None
    on_error: str = "fail"  # fail, skip, retry
    retry_count: int = 0
    timeout: int = 300

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "prompt_id": self.prompt_id,
            "config": self.config,
            "input_mapping": self.input_mapping,
            "output_mapping": self.output_mapping,
            "condition": self.condition,
            "on_error": self.on_error,
            "retry_count": self.retry_count,
            "timeout": self.timeout,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowStep":
        return cls(
            id=data.get("id", str(uuid4())[:8]),
            name=data.get("name", ""),
            type=WorkflowStepType(data.get("type", "prompt")),
            prompt_id=data.get("prompt_id"),
            config=data.get("config", {}),
            input_mapping=data.get("input_mapping", {}),
            output_mapping=data.get("output_mapping", {}),
            condition=data.get("condition"),
            on_error=data.get("on_error", "fail"),
            retry_count=data.get("retry_count", 0),
            timeout=data.get("timeout", 300),
        )


@dataclass
class Workflow:
    """
    Workflow model for orchestrating multiple prompts
    
    Supports sequential, parallel, and conditional execution.
    """
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    name: str = ""
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_step(
        self,
        name: str,
        type: WorkflowStepType = WorkflowStepType.PROMPT,
        prompt_id: Optional[str] = None,
        **kwargs,
    ) -> WorkflowStep:
        """Add a step to the workflow"""
        step = WorkflowStep(
            name=name,
            type=type,
            prompt_id=prompt_id,
            **kwargs,
        )
        self.steps.append(step)
        self.updated_at = datetime.now().isoformat()
        return step

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "variables": self.variables,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        return cls(
            id=data.get("id", str(uuid4())[:8]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            steps=[WorkflowStep.from_dict(s) for s in data.get("steps", [])],
            variables=data.get("variables", {}),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ExecutionResult:
    """Result of a prompt or workflow execution"""
    success: bool
    output: str = ""
    error: str = ""
    tokens_used: int = 0
    duration_ms: int = 0
    model: str = ""
    provider: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "tokens_used": self.tokens_used,
            "duration_ms": self.duration_ms,
            "model": self.model,
            "provider": self.provider,
            "metadata": self.metadata,
        }


@dataclass
class Config:
    """Global configuration for PromptFlow"""
    default_provider: LLMProvider = LLMProvider.OPENAI
    default_model: str = "gpt-4"
    default_temperature: float = 0.7
    default_max_tokens: int = 4096
    storage_path: str = "~/.promptflow"
    auto_save: bool = True
    auto_version: bool = True
    git_integration: bool = True
    log_level: str = "INFO"

    # API Keys (stored separately, not in config file)
    api_keys: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "default_provider": self.default_provider.value,
            "default_model": self.default_model,
            "default_temperature": self.default_temperature,
            "default_max_tokens": self.default_max_tokens,
            "storage_path": self.storage_path,
            "auto_save": self.auto_save,
            "auto_version": self.auto_version,
            "git_integration": self.git_integration,
            "log_level": self.log_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        return cls(
            default_provider=LLMProvider(data.get("default_provider", "openai")),
            default_model=data.get("default_model", "gpt-4"),
            default_temperature=data.get("default_temperature", 0.7),
            default_max_tokens=data.get("default_max_tokens", 4096),
            storage_path=data.get("storage_path", "~/.promptflow"),
            auto_save=data.get("auto_save", True),
            auto_version=data.get("auto_version", True),
            git_integration=data.get("git_integration", True),
            log_level=data.get("log_level", "INFO"),
        )
