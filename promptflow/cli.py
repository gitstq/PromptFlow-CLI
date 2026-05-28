"""
Command Line Interface for PromptFlow-CLI

Provides a comprehensive CLI with commands for managing prompts,
workflows, and configurations.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from promptflow import __version__
from promptflow.core import PromptFlow
from promptflow.models import (
    LLMProvider,
    PromptCategory,
    PromptVariable,
    WorkflowStepType,
)


class CLI:
    """Command Line Interface handler"""

    def __init__(self):
        self.pf = PromptFlow()
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog="promptflow",
            description="🚀 PromptFlow-CLI - Lightweight Terminal AI Prompt Workflow Orchestration & Version Management Engine",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Create a new prompt
  promptflow create my-prompt --content "Write a {{style}} blog post about {{topic}}"
  
  # List all prompts
  promptflow list
  
  # Execute a prompt
  promptflow run abc123 --var style=professional --var topic=AI
  
  # Show prompt details
  promptflow show abc123
  
  # Version control
  promptflow version add abc123 --content "Updated content" --message "Improved prompt"
  promptflow version rollback abc123 1.0.1
  
  # Workflow management
  promptflow workflow create my-workflow
  promptflow workflow add-step my-workflow --prompt abc123 --name "Step 1"
  
  # Dashboard
  promptflow dashboard
            """,
        )

        parser.add_argument(
            "-V", "--version",
            action="version",
            version=f"%(prog)s {__version__}",
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Create command
        create_parser = subparsers.add_parser("create", help="Create a new prompt")
        create_parser.add_argument("name", help="Prompt name")
        create_parser.add_argument("-c", "--content", help="Prompt content")
        create_parser.add_argument("-d", "--description", help="Prompt description")
        create_parser.add_argument("--category", default="general", help="Prompt category")
        create_parser.add_argument("--tags", help="Comma-separated tags")
        create_parser.add_argument("--provider", help="LLM provider")
        create_parser.add_argument("--model", help="Model name")
        create_parser.add_argument("-f", "--file", help="Read content from file")
        create_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")

        # List command
        list_parser = subparsers.add_parser("list", aliases=["ls"], help="List prompts")
        list_parser.add_argument("--category", help="Filter by category")
        list_parser.add_argument("--tags", help="Filter by tags")
        list_parser.add_argument("-s", "--search", help="Search term")
        list_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

        # Show command
        show_parser = subparsers.add_parser("show", help="Show prompt details")
        show_parser.add_argument("id", help="Prompt ID or name")
        show_parser.add_argument("-v", "--version", help="Show specific version")
        show_parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

        # Edit command
        edit_parser = subparsers.add_parser("edit", help="Edit a prompt")
        edit_parser.add_argument("id", help="Prompt ID or name")
        edit_parser.add_argument("-c", "--content", help="New content")
        edit_parser.add_argument("-d", "--description", help="New description")
        edit_parser.add_argument("--tags", help="New tags")
        edit_parser.add_argument("-f", "--file", help="Read content from file")
        edit_parser.add_argument("-m", "--message", help="Version message")

        # Delete command
        delete_parser = subparsers.add_parser("delete", aliases=["rm", "del"], help="Delete a prompt")
        delete_parser.add_argument("id", help="Prompt ID or name")
        delete_parser.add_argument("-f", "--force", action="store_true", help="Force deletion")

        # Run command
        run_parser = subparsers.add_parser("run", aliases=["execute"], help="Execute a prompt")
        run_parser.add_argument("id", help="Prompt ID or name")
        run_parser.add_argument("--var", action="append", help="Variable (key=value)")
        run_parser.add_argument("--provider", help="Override provider")
        run_parser.add_argument("--model", help="Override model")
        run_parser.add_argument("-o", "--output", help="Output file")

        # Version commands
        version_parser = subparsers.add_parser("version", aliases=["v"], help="Version control")
        version_subparsers = version_parser.add_subparsers(dest="version_command")
        
        v_list = version_subparsers.add_parser("list", help="List versions")
        v_list.add_argument("id", help="Prompt ID or name")
        
        v_add = version_subparsers.add_parser("add", help="Add new version")
        v_add.add_argument("id", help="Prompt ID or name")
        v_add.add_argument("-c", "--content", help="New content")
        v_add.add_argument("-m", "--message", help="Version message")
        v_add.add_argument("-f", "--file", help="Read content from file")
        
        v_rollback = version_subparsers.add_parser("rollback", help="Rollback to version")
        v_rollback.add_argument("id", help="Prompt ID or name")
        v_rollback.add_argument("version", help="Version to rollback to")
        
        v_diff = version_subparsers.add_parser("diff", help="Compare versions")
        v_diff.add_argument("id", help="Prompt ID or name")
        v_diff.add_argument("version1", help="First version")
        v_diff.add_argument("version2", help="Second version")

        # Workflow commands
        workflow_parser = subparsers.add_parser("workflow", aliases=["wf"], help="Workflow management")
        wf_subparsers = workflow_parser.add_subparsers(dest="workflow_command")
        
        wf_create = wf_subparsers.add_parser("create", help="Create workflow")
        wf_create.add_argument("name", help="Workflow name")
        wf_create.add_argument("-d", "--description", help="Workflow description")
        
        wf_list = wf_subparsers.add_parser("list", aliases=["ls"], help="List workflows")
        wf_list.add_argument("-s", "--search", help="Search term")
        
        wf_show = wf_subparsers.add_parser("show", help="Show workflow")
        wf_show.add_argument("id", help="Workflow ID or name")
        
        wf_add = wf_subparsers.add_parser("add-step", help="Add step to workflow")
        wf_add.add_argument("id", help="Workflow ID or name")
        wf_add.add_argument("--name", required=True, help="Step name")
        wf_add.add_argument("--prompt", help="Prompt ID")
        wf_add.add_argument("--type", default="prompt", help="Step type")
        
        wf_run = wf_subparsers.add_parser("run", help="Execute workflow")
        wf_run.add_argument("id", help="Workflow ID or name")
        wf_run.add_argument("--var", action="append", help="Variable (key=value)")
        
        wf_delete = wf_subparsers.add_parser("delete", aliases=["rm"], help="Delete workflow")
        wf_delete.add_argument("id", help="Workflow ID or name")

        # Config commands
        config_parser = subparsers.add_parser("config", help="Configuration")
        config_subparsers = config_parser.add_subparsers(dest="config_command")
        
        config_show = config_subparsers.add_parser("show", help="Show configuration")
        config_set = config_subparsers.add_parser("set", help="Set configuration")
        config_set.add_argument("key", help="Configuration key")
        config_set.add_argument("value", help="Configuration value")

        # Backup commands
        backup_parser = subparsers.add_parser("backup", help="Backup management")
        backup_subparsers = backup_parser.add_subparsers(dest="backup_command")
        
        backup_create = backup_subparsers.add_parser("create", help="Create backup")
        backup_list = backup_subparsers.add_parser("list", help="List backups")
        backup_restore = backup_subparsers.add_parser("restore", help="Restore backup")
        backup_restore.add_argument("name", help="Backup name")

        # Export/Import
        export_parser = subparsers.add_parser("export", help="Export data")
        export_parser.add_argument("-o", "--output", default="promptflow_export.json", help="Output file")
        
        import_parser = subparsers.add_parser("import", help="Import data")
        import_parser.add_argument("file", help="Import file")
        import_parser.add_argument("--no-merge", action="store_true", help="Replace existing data")

        # Dashboard
        subparsers.add_parser("dashboard", aliases=["ui"], help="Launch TUI dashboard")

        # Stats
        subparsers.add_parser("stats", help="Show statistics")

        return parser

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run CLI with arguments"""
        parsed = self.parser.parse_args(args)
        
        if not parsed.command:
            self.parser.print_help()
            return 0

        # Map commands to handlers
        handlers = {
            "create": self._cmd_create,
            "list": self._cmd_list,
            "ls": self._cmd_list,
            "show": self._cmd_show,
            "edit": self._cmd_edit,
            "delete": self._cmd_delete,
            "rm": self._cmd_delete,
            "del": self._cmd_delete,
            "run": self._cmd_run,
            "execute": self._cmd_run,
            "version": self._cmd_version,
            "v": self._cmd_version,
            "workflow": self._cmd_workflow,
            "wf": self._cmd_workflow,
            "config": self._cmd_config,
            "backup": self._cmd_backup,
            "export": self._cmd_export,
            "import": self._cmd_import,
            "dashboard": self._cmd_dashboard,
            "ui": self._cmd_dashboard,
            "stats": self._cmd_stats,
        }

        handler = handlers.get(parsed.command)
        if handler:
            try:
                return handler(parsed)
            except Exception as e:
                print(f"❌ Error: {e}", file=sys.stderr)
                return 1
        else:
            self.parser.print_help()
            return 0

    def _cmd_create(self, args) -> int:
        """Create a new prompt"""
        content = args.content
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        elif args.interactive:
            print("Enter prompt content (Ctrl+D to finish):")
            lines = []
            try:
                while True:
                    lines.append(input())
            except EOFError:
                content = "\n".join(lines)

        if not content:
            print("❌ Content is required", file=sys.stderr)
            return 1

        tags = args.tags.split(",") if args.tags else []
        provider = LLMProvider(args.provider) if args.provider else None
        category = PromptCategory(args.category) if args.category else PromptCategory.GENERAL

        prompt = self.pf.create_prompt(
            name=args.name,
            content=content,
            description=args.description or "",
            category=category,
            tags=tags,
            provider=provider,
            model=args.model,
        )

        print(f"✅ Created prompt: {prompt.id}")
        print(f"   Name: {prompt.name}")
        print(f"   Category: {prompt.category.value}")
        if prompt.tags:
            print(f"   Tags: {', '.join(prompt.tags)}")
        return 0

    def _cmd_list(self, args) -> int:
        """List prompts"""
        category = PromptCategory(args.category) if args.category else None
        tags = args.tags.split(",") if args.tags else None

        prompts = self.pf.list_prompts(category=category, tags=tags, search=args.search)

        if args.json:
            print(json.dumps([p.to_dict() for p in prompts], indent=2))
        else:
            if not prompts:
                print("No prompts found")
                return 0

            print(f"\n📋 Found {len(prompts)} prompt(s):\n")
            print(f"{'ID':<10} {'Name':<25} {'Category':<12} {'Versions':<10} {'Updated'}")
            print("-" * 80)
            for p in prompts:
                print(f"{p.id:<10} {p.name[:25]:<25} {p.category.value:<12} {len(p.versions):<10} {p.updated_at[:10]}")
        return 0

    def _cmd_show(self, args) -> int:
        """Show prompt details"""
        prompt = self.pf.get_prompt(args.id) or self.pf.get_prompt_by_name(args.id)
        if not prompt:
            print(f"❌ Prompt not found: {args.id}", file=sys.stderr)
            return 1

        if args.version:
            version = prompt.get_version(args.version)
            if not version:
                print(f"❌ Version not found: {args.version}", file=sys.stderr)
                return 1
            if args.json:
                print(json.dumps(version.to_dict(), indent=2))
            else:
                print(f"\n📜 Version {version.version}")
                print(f"   Created: {version.created_at}")
                print(f"   Message: {version.message}")
                print(f"   Checksum: {version.checksum}")
                print(f"\nContent:\n{'-'*40}")
                print(version.content)
        else:
            if args.json:
                print(json.dumps(prompt.to_dict(), indent=2))
            else:
                print(f"\n📜 Prompt: {prompt.name} ({prompt.id})")
                print(f"   Description: {prompt.description or 'N/A'}")
                print(f"   Category: {prompt.category.value}")
                print(f"   Current Version: {prompt.current_version}")
                print(f"   Total Versions: {len(prompt.versions)}")
                if prompt.tags:
                    print(f"   Tags: {', '.join(prompt.tags)}")
                if prompt.provider:
                    print(f"   Provider: {prompt.provider.value}")
                if prompt.model:
                    print(f"   Model: {prompt.model}")
                print(f"   Created: {prompt.created_at}")
                print(f"   Updated: {prompt.updated_at}")
                print(f"\nContent:\n{'-'*40}")
                print(prompt.content)
        return 0

    def _cmd_edit(self, args) -> int:
        """Edit a prompt"""
        prompt = self.pf.get_prompt(args.id) or self.pf.get_prompt_by_name(args.id)
        if not prompt:
            print(f"❌ Prompt not found: {args.id}", file=sys.stderr)
            return 1

        content = args.content
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()

        tags = args.tags.split(",") if args.tags else None

        updated = self.pf.update_prompt(
            prompt.id,
            content=content,
            description=args.description,
            tags=tags,
            version_message=args.message,
        )

        if updated:
            print(f"✅ Updated prompt: {updated.id}")
            print(f"   Current Version: {updated.current_version}")
        else:
            print("❌ Failed to update prompt", file=sys.stderr)
            return 1
        return 0

    def _cmd_delete(self, args) -> int:
        """Delete a prompt"""
        prompt = self.pf.get_prompt(args.id) or self.pf.get_prompt_by_name(args.id)
        if not prompt:
            print(f"❌ Prompt not found: {args.id}", file=sys.stderr)
            return 1

        if not args.force:
            confirm = input(f"Delete prompt '{prompt.name}' ({prompt.id})? [y/N] ")
            if confirm.lower() != "y":
                print("Cancelled")
                return 0

        if self.pf.delete_prompt(prompt.id):
            print(f"✅ Deleted prompt: {prompt.id}")
        else:
            print("❌ Failed to delete prompt", file=sys.stderr)
            return 1
        return 0

    def _cmd_run(self, args) -> int:
        """Execute a prompt"""
        prompt = self.pf.get_prompt(args.id) or self.pf.get_prompt_by_name(args.id)
        if not prompt:
            print(f"❌ Prompt not found: {args.id}", file=sys.stderr)
            return 1

        variables = {}
        if args.var:
            for v in args.var:
                if "=" in v:
                    k, val = v.split("=", 1)
                    variables[k] = val

        provider = LLMProvider(args.provider) if args.provider else None

        print(f"🚀 Executing prompt: {prompt.name}")
        print(f"   Provider: {provider.value if provider else prompt.provider.value if prompt.provider else 'default'}")
        print(f"   Model: {args.model or prompt.model or 'default'}")
        if variables:
            print(f"   Variables: {variables}")
        print()

        result = self.pf.execute_prompt(
            prompt.id,
            variables=variables,
            provider=provider,
            model=args.model,
        )

        if result.success:
            print(f"✅ Execution completed in {result.duration_ms}ms")
            print(f"   Tokens used: {result.tokens_used}")
            print(f"\n{'='*40}\nOutput:\n{'='*40}")
            print(result.output)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(result.output)
                print(f"\n💾 Output saved to: {args.output}")
        else:
            print(f"❌ Execution failed: {result.error}", file=sys.stderr)
            return 1
        return 0

    def _cmd_version(self, args) -> int:
        """Version control commands"""
        if not args.version_command:
            print("Usage: promptflow version <command>")
            print("Commands: list, add, rollback, diff")
            return 1

        if args.version_command == "list":
            prompt = self.pf.get_prompt(args.id) or self.pf.get_prompt_by_name(args.id)
            if not prompt:
                print(f"❌ Prompt not found: {args.id}", file=sys.stderr)
                return 1

            versions = self.pf.get_prompt_versions(prompt.id)
            print(f"\n📜 Versions for '{prompt.name}':\n")
            print(f"{'Version':<12} {'Created':<20} {'Message':<40} {'Checksum'}")
            print("-" * 90)
            for v in versions:
                current = " (current)" if v.version == prompt.current_version else ""
                print(f"{v.version + current:<12} {v.created_at[:19]:<20} {v.message[:40]:<40} {v.checksum}")
            return 0

        elif args.version_command == "add":
            prompt = self.pf.get_prompt(args.id) or self.pf.get_prompt_by_name(args.id)
            if not prompt:
                print(f"❌ Prompt not found: {args.id}", file=sys.stderr)
                return 1

            content = args.content
            if args.file:
                with open(args.file, "r", encoding="utf-8") as f:
                    content = f.read()

            if not content:
                print("❌ Content is required", file=sys.stderr)
                return 1

            version = self.pf.add_prompt_version(
                prompt.id,
                content=content,
                message=args.message or "",
            )
            print(f"✅ Added version {version.version} to prompt {prompt.id}")
            return 0

        elif args.version_command == "rollback":
            prompt = self.pf.get_prompt(args.id) or self.pf.get_prompt_by_name(args.id)
            if not prompt:
                print(f"❌ Prompt not found: {args.id}", file=sys.stderr)
                return 1

            if self.pf.rollback_prompt(prompt.id, args.version):
                print(f"✅ Rolled back to version {args.version}")
            else:
                print(f"❌ Failed to rollback to version {args.version}", file=sys.stderr)
                return 1
            return 0

        elif args.version_command == "diff":
            prompt = self.pf.get_prompt(args.id) or self.pf.get_prompt_by_name(args.id)
            if not prompt:
                print(f"❌ Prompt not found: {args.id}", file=sys.stderr)
                return 1

            diff = self.pf.diff_prompt_versions(prompt.id, args.version1, args.version2)
            if not diff:
                print("❌ Failed to compare versions", file=sys.stderr)
                return 1

            print(f"\n📜 Comparing {args.version1} vs {args.version2}:\n")
            print(f"Version {args.version1}:")
            print(f"  Message: {diff['message1']}")
            print(f"  Created: {diff['created_at1']}")
            print(f"\nVersion {args.version2}:")
            print(f"  Message: {diff['message2']}")
            print(f"  Created: {diff['created_at2']}")
            print(f"\n{'='*40}\nContent Diff:\n{'='*40}")
            print(f"\n--- {args.version1}\n+++ {args.version2}\n")
            # Simple diff output
            lines1 = diff["content1"].split("\n")
            lines2 = diff["content2"].split("\n")
            for i, (l1, l2) in enumerate(zip(lines1, lines2)):
                if l1 != l2:
                    print(f"  Line {i+1}:")
                    print(f"  - {l1}")
                    print(f"  + {l2}")
            return 0

        return 1

    def _cmd_workflow(self, args) -> int:
        """Workflow commands"""
        if not args.workflow_command:
            print("Usage: promptflow workflow <command>")
            print("Commands: create, list, show, add-step, run, delete")
            return 1

        if args.workflow_command in ["list", "ls"]:
            workflows = self.pf.list_workflows(search=args.search)
            if not workflows:
                print("No workflows found")
                return 0

            print(f"\n📋 Found {len(workflows)} workflow(s):\n")
            print(f"{'ID':<10} {'Name':<30} {'Steps':<10} {'Updated'}")
            print("-" * 70)
            for w in workflows:
                print(f"{w.id:<10} {w.name[:30]:<30} {len(w.steps):<10} {w.updated_at[:10]}")
            return 0

        elif args.workflow_command == "create":
            workflow = self.pf.create_workflow(
                name=args.name,
                description=args.description or "",
            )
            print(f"✅ Created workflow: {workflow.id}")
            print(f"   Name: {workflow.name}")
            return 0

        elif args.workflow_command == "show":
            workflow = self.pf.get_workflow(args.id)
            if not workflow:
                print(f"❌ Workflow not found: {args.id}", file=sys.stderr)
                return 1

            print(f"\n📋 Workflow: {workflow.name} ({workflow.id})")
            print(f"   Description: {workflow.description or 'N/A'}")
            print(f"   Steps: {len(workflow.steps)}")
            print(f"   Created: {workflow.created_at}")
            print(f"   Updated: {workflow.updated_at}")
            if workflow.steps:
                print(f"\n   Steps:")
                for i, step in enumerate(workflow.steps, 1):
                    print(f"     {i}. {step.name} ({step.type.value})")
            return 0

        elif args.workflow_command == "add-step":
            workflow = self.pf.get_workflow(args.id)
            if not workflow:
                print(f"❌ Workflow not found: {args.id}", file=sys.stderr)
                return 1

            step_type = WorkflowStepType(args.type) if args.type else WorkflowStepType.PROMPT
            step = self.pf.add_workflow_step(
                workflow.id,
                name=args.name,
                type=step_type,
                prompt_id=args.prompt,
            )
            if step:
                print(f"✅ Added step '{step.name}' to workflow {workflow.id}")
            else:
                print("❌ Failed to add step", file=sys.stderr)
                return 1
            return 0

        elif args.workflow_command == "run":
            workflow = self.pf.get_workflow(args.id)
            if not workflow:
                print(f"❌ Workflow not found: {args.id}", file=sys.stderr)
                return 1

            variables = {}
            if args.var:
                for v in args.var:
                    if "=" in v:
                        k, val = v.split("=", 1)
                        variables[k] = val

            print(f"🚀 Executing workflow: {workflow.name}")
            results = self.pf.execute_workflow(workflow.id, variables=variables)

            print(f"\n✅ Workflow completed")
            for step_id, result in results.items():
                status = "✅" if result.success else "❌"
                print(f"   {status} Step {step_id}: {result.output[:50] if result.success else result.error}...")
            return 0

        elif args.workflow_command in ["delete", "rm"]:
            workflow = self.pf.get_workflow(args.id)
            if not workflow:
                print(f"❌ Workflow not found: {args.id}", file=sys.stderr)
                return 1

            if self.pf.delete_workflow(workflow.id):
                print(f"✅ Deleted workflow: {workflow.id}")
            else:
                print("❌ Failed to delete workflow", file=sys.stderr)
                return 1
            return 0

        return 1

    def _cmd_config(self, args) -> int:
        """Configuration commands"""
        if not args.config_command:
            print("Usage: promptflow config <command>")
            print("Commands: show, set")
            return 1

        if args.config_command == "show":
            config = self.pf.config
            print(f"\n⚙️  Configuration:\n")
            print(f"   Default Provider: {config.default_provider.value}")
            print(f"   Default Model: {config.default_model}")
            print(f"   Default Temperature: {config.default_temperature}")
            print(f"   Default Max Tokens: {config.default_max_tokens}")
            print(f"   Storage Path: {config.storage_path}")
            print(f"   Auto Save: {config.auto_save}")
            print(f"   Auto Version: {config.auto_version}")
            print(f"   Git Integration: {config.git_integration}")
            return 0

        elif args.config_command == "set":
            self.pf.update_config(**{args.key: args.value})
            print(f"✅ Set {args.key} = {args.value}")
            return 0

        return 1

    def _cmd_backup(self, args) -> int:
        """Backup commands"""
        if not args.backup_command:
            print("Usage: promptflow backup <command>")
            print("Commands: create, list, restore")
            return 1

        if args.backup_command == "create":
            backup_path = self.pf.create_backup()
            print(f"✅ Created backup: {backup_path}")
            return 0

        elif args.backup_command == "list":
            backups = self.pf.list_backups()
            if not backups:
                print("No backups found")
                return 0

            print(f"\n💾 Found {len(backups)} backup(s):\n")
            print(f"{'Name':<25} {'Created':<25}")
            print("-" * 50)
            for b in backups:
                print(f"{b['name']:<25} {b['created_at'][:19]:<25}")
            return 0

        elif args.backup_command == "restore":
            if self.pf.restore_backup(args.name):
                print(f"✅ Restored from backup: {args.name}")
            else:
                print(f"❌ Failed to restore backup: {args.name}", file=sys.stderr)
                return 1
            return 0

        return 1

    def _cmd_export(self, args) -> int:
        """Export data"""
        self.pf.export_data(args.output)
        print(f"✅ Exported data to: {args.output}")
        return 0

    def _cmd_import(self, args) -> int:
        """Import data"""
        stats = self.pf.import_data(args.file, merge=not args.no_merge)
        print(f"✅ Imported data:")
        print(f"   Prompts: {stats['prompts_imported']}")
        print(f"   Workflows: {stats['workflows_imported']}")
        return 0

    def _cmd_dashboard(self, args) -> int:
        """Launch TUI dashboard"""
        try:
            from promptflow.tui import run_dashboard
            run_dashboard(self.pf)
        except ImportError:
            print("❌ TUI dashboard requires additional dependencies")
            print("   Install with: pip install promptflow-cli[tui]")
            return 1
        return 0

    def _cmd_stats(self, args) -> int:
        """Show statistics"""
        stats = self.pf.get_stats()
        print(f"\n📊 PromptFlow Statistics:\n")
        print(f"   📜 Prompts: {stats['prompts_count']}")
        print(f"   📋 Workflows: {stats['workflows_count']}")
        print(f"   💾 Backups: {stats['backups_count']}")
        print(f"   🚀 Executions: {stats['executions_count']}")
        print(f"   📁 Storage Size: {stats['storage_size_bytes']:,} bytes")
        print(f"   📂 Storage Path: {stats['storage_path']}")
        print(f"\n   Categories:")
        for cat, count in stats['categories'].items():
            if count > 0:
                print(f"      {cat}: {count}")
        return 0


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point"""
    cli = CLI()
    return cli.run(args)


if __name__ == "__main__":
    sys.exit(main())
