"""
Storage module for PromptFlow-CLI

Handles persistence of prompts, workflows, and configurations.
Supports JSON file storage with atomic writes and backup.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from promptflow.models import (
    Config,
    Prompt,
    PromptCategory,
    PromptVersion,
    Workflow,
)

T = TypeVar("T")


class StorageError(Exception):
    """Storage operation error"""
    pass


class Storage:
    """
    File-based storage for prompts and workflows
    
    Structure:
    ~/.promptflow/
    ├── config.json
    ├── prompts/
    │   ├── prompt-abc123.json
    │   └── prompt-def456.json
    ├── workflows/
    │   ├── workflow-xyz789.json
    │   └── ...
    ├── backups/
    │   └── 2026-05-28/
    └── logs/
        └── promptflow.log
    """

    DEFAULT_STORAGE_PATH = "~/.promptflow"

    def __init__(self, path: Optional[str] = None):
        self.base_path = Path(path or self.DEFAULT_STORAGE_PATH).expanduser()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create storage directories if they don't exist"""
        dirs = [
            self.base_path,
            self.base_path / "prompts",
            self.base_path / "workflows",
            self.base_path / "backups",
            self.base_path / "logs",
            self.base_path / "templates",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    # ==================== Config Operations ====================

    def load_config(self) -> Config:
        """Load global configuration"""
        config_path = self.base_path / "config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return Config.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass
        return Config()

    def save_config(self, config: Config) -> None:
        """Save global configuration"""
        config_path = self.base_path / "config.json"
        self._write_json(config_path, config.to_dict())

    # ==================== Prompt Operations ====================

    def list_prompts(
        self,
        category: Optional[PromptCategory] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
    ) -> List[Prompt]:
        """List all prompts with optional filtering"""
        prompts = []
        prompts_dir = self.base_path / "prompts"
        
        for file_path in prompts_dir.glob("prompt-*.json"):
            try:
                prompt = self.load_prompt(file_path.stem.replace("prompt-", ""))
                if prompt:
                    # Apply filters
                    if category and prompt.category != category:
                        continue
                    if tags and not any(t in prompt.tags for t in tags):
                        continue
                    if search:
                        search_lower = search.lower()
                        if (
                            search_lower not in prompt.name.lower()
                            and search_lower not in prompt.description.lower()
                            and search_lower not in prompt.content.lower()
                        ):
                            continue
                    prompts.append(prompt)
            except Exception:
                continue
        
        # Sort by updated_at descending
        prompts.sort(key=lambda p: p.updated_at, reverse=True)
        return prompts

    def load_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Load a prompt by ID"""
        file_path = self.base_path / "prompts" / f"prompt-{prompt_id}.json"
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Prompt.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def save_prompt(self, prompt: Prompt) -> None:
        """Save a prompt"""
        file_path = self.base_path / "prompts" / f"prompt-{prompt.id}.json"
        self._write_json(file_path, prompt.to_dict())

    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt"""
        file_path = self.base_path / "prompts" / f"prompt-{prompt_id}.json"
        if file_path.exists():
            # Create backup before deletion
            self._backup_file(file_path, "prompts")
            file_path.unlink()
            return True
        return False

    def prompt_exists(self, prompt_id: str) -> bool:
        """Check if a prompt exists"""
        return (self.base_path / "prompts" / f"prompt-{prompt_id}.json").exists()

    # ==================== Workflow Operations ====================

    def list_workflows(self, search: Optional[str] = None) -> List[Workflow]:
        """List all workflows"""
        workflows = []
        workflows_dir = self.base_path / "workflows"
        
        for file_path in workflows_dir.glob("workflow-*.json"):
            try:
                workflow = self.load_workflow(file_path.stem.replace("workflow-", ""))
                if workflow:
                    if search:
                        search_lower = search.lower()
                        if (
                            search_lower not in workflow.name.lower()
                            and search_lower not in workflow.description.lower()
                        ):
                            continue
                    workflows.append(workflow)
            except Exception:
                continue
        
        workflows.sort(key=lambda w: w.updated_at, reverse=True)
        return workflows

    def load_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Load a workflow by ID"""
        file_path = self.base_path / "workflows" / f"workflow-{workflow_id}.json"
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Workflow.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    def save_workflow(self, workflow: Workflow) -> None:
        """Save a workflow"""
        file_path = self.base_path / "workflows" / f"workflow-{workflow.id}.json"
        self._write_json(file_path, workflow.to_dict())

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        file_path = self.base_path / "workflows" / f"workflow-{workflow_id}.json"
        if file_path.exists():
            self._backup_file(file_path, "workflows")
            file_path.unlink()
            return True
        return False

    # ==================== Template Operations ====================

    def list_templates(self) -> List[Dict[str, Any]]:
        """List available templates"""
        templates = []
        templates_dir = self.base_path / "templates"
        
        for file_path in templates_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                templates.append(data)
            except Exception:
                continue
        
        return templates

    def save_template(self, name: str, template: Dict[str, Any]) -> None:
        """Save a template"""
        file_path = self.base_path / "templates" / f"{name}.json"
        self._write_json(file_path, template)

    # ==================== Backup Operations ====================

    def create_backup(self) -> str:
        """Create a full backup of all data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_path / "backups" / timestamp
        
        shutil.copytree(
            self.base_path / "prompts",
            backup_dir / "prompts",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            self.base_path / "workflows",
            backup_dir / "workflows",
            dirs_exist_ok=True,
        )
        
        return str(backup_dir)

    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = []
        backups_dir = self.base_path / "backups"
        
        for backup_path in sorted(backups_dir.iterdir(), reverse=True):
            if backup_path.is_dir():
                backups.append({
                    "name": backup_path.name,
                    "path": str(backup_path),
                    "created_at": datetime.fromtimestamp(
                        backup_path.stat().st_mtime
                    ).isoformat(),
                })
        
        return backups

    def restore_backup(self, backup_name: str) -> bool:
        """Restore from a backup"""
        backup_dir = self.base_path / "backups" / backup_name
        if not backup_dir.exists():
            return False
        
        # Restore prompts
        prompts_backup = backup_dir / "prompts"
        if prompts_backup.exists():
            shutil.rmtree(self.base_path / "prompts")
            shutil.copytree(prompts_backup, self.base_path / "prompts")
        
        # Restore workflows
        workflows_backup = backup_dir / "workflows"
        if workflows_backup.exists():
            shutil.rmtree(self.base_path / "workflows")
            shutil.copytree(workflows_backup, self.base_path / "workflows")
        
        return True

    # ==================== Utility Methods ====================

    def _write_json(self, path: Path, data: Dict[str, Any]) -> None:
        """Write JSON file atomically"""
        temp_path = path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            shutil.move(str(temp_path), str(path))
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise StorageError(f"Failed to write {path}: {e}")

    def _backup_file(self, file_path: Path, category: str) -> None:
        """Create a backup of a file before modification/deletion"""
        if not file_path.exists():
            return
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        backup_dir = self.base_path / "backups" / date_str / category
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}.json"
        shutil.copy2(file_path, backup_dir / backup_name)

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        prompts = self.list_prompts()
        workflows = self.list_workflows()
        backups = self.list_backups()
        
        # Calculate total size
        total_size = 0
        for path in self.base_path.rglob("*"):
            if path.is_file():
                total_size += path.stat().st_size
        
        return {
            "prompts_count": len(prompts),
            "workflows_count": len(workflows),
            "backups_count": len(backups),
            "storage_size_bytes": total_size,
            "storage_path": str(self.base_path),
            "categories": {
                cat.value: len([p for p in prompts if p.category == cat])
                for cat in PromptCategory
            },
        }

    def export_all(self, export_path: str) -> None:
        """Export all data to a single JSON file"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "prompts": [p.to_dict() for p in self.list_prompts()],
            "workflows": [w.to_dict() for w in self.list_workflows()],
            "config": self.load_config().to_dict(),
        }
        self._write_json(Path(export_path), data)

    def import_all(self, import_path: str, merge: bool = True) -> Dict[str, int]:
        """Import data from an export file"""
        with open(import_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        stats = {"prompts_imported": 0, "workflows_imported": 0}
        
        # Import prompts
        for prompt_data in data.get("prompts", []):
            prompt = Prompt.from_dict(prompt_data)
            if merge and self.prompt_exists(prompt.id):
                continue
            self.save_prompt(prompt)
            stats["prompts_imported"] += 1
        
        # Import workflows
        for workflow_data in data.get("workflows", []):
            workflow = Workflow.from_dict(workflow_data)
            self.save_workflow(workflow)
            stats["workflows_imported"] += 1
        
        return stats
