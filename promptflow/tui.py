"""
Terminal User Interface (TUI) Dashboard for PromptFlow-CLI

Provides an interactive dashboard for managing prompts and workflows.
Uses only Python standard library for zero dependencies.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Callable, Dict, List, Optional

# Simple TUI using ANSI escape codes (no external dependencies)
class Colors:
    """ANSI color codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class TUI:
    """Simple Terminal User Interface"""

    def __init__(self):
        self.width = 80
        self.height = 24
        self._update_size()

    def _update_size(self) -> None:
        """Update terminal size"""
        try:
            size = os.get_terminal_size()
            self.width = size.columns
            self.height = size.lines
        except Exception:
            pass

    def clear(self) -> None:
        """Clear screen"""
        print("\033[2J\033[H", end="")

    def move(self, row: int, col: int) -> None:
        """Move cursor to position"""
        print(f"\033[{row};{col}H", end="")

    def print_at(self, row: int, col: int, text: str) -> None:
        """Print text at position"""
        self.move(row, col)
        print(text, end="")

    def draw_box(self, row: int, col: int, width: int, height: int, title: str = "") -> None:
        """Draw a box"""
        # Top border
        top = "┌" + "─" * (width - 2) + "┐"
        if title:
            title_str = f" {title} "
            title_pos = (width - len(title_str)) // 2
            top = "┌" + "─" * title_pos + title_str + "─" * (width - 2 - title_pos - len(title_str)) + "┐"
        
        self.print_at(row, col, top)
        
        # Middle rows
        for i in range(1, height - 1):
            self.print_at(row + i, col, "│" + " " * (width - 2) + "│")
        
        # Bottom border
        self.print_at(row + height - 1, col, "└" + "─" * (width - 2) + "┘")

    def draw_header(self, title: str) -> None:
        """Draw header"""
        self._update_size()
        header = f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD} {title} {' ' * (self.width - len(title) - 3)}{Colors.RESET}"
        self.print_at(1, 1, header)

    def draw_footer(self, text: str) -> None:
        """Draw footer"""
        self._update_size()
        footer = f"{Colors.BG_BLACK}{Colors.WHITE} {text}{' ' * (self.width - len(text) - 2)}{Colors.RESET}"
        self.print_at(self.height, 1, footer)

    def draw_menu(self, row: int, col: int, items: List[Dict[str, Any]], selected: int) -> None:
        """Draw menu items"""
        for i, item in enumerate(items):
            prefix = "→ " if i == selected else "  "
            color = Colors.CYAN if i == selected else Colors.WHITE
            text = f"{prefix}{item['label']}"
            self.print_at(row + i, col, f"{color}{text}{Colors.RESET}")

    def draw_table(self, row: int, col: int, headers: List[str], rows: List[List[str]], widths: List[int]) -> None:
        """Draw a table"""
        # Header
        header_line = "│"
        for i, h in enumerate(headers):
            header_line += f" {h:<{widths[i]}} │"
        self.print_at(row, col, f"{Colors.BOLD}{header_line}{Colors.RESET}")
        
        # Separator
        sep_line = "├"
        for i, w in enumerate(widths):
            sep_line += "─" * (w + 2) + "┼" if i < len(widths) - 1 else "─" * (w + 2) + "┤"
        self.print_at(row + 1, col, sep_line)
        
        # Rows
        for i, r in enumerate(rows):
            row_line = "│"
            for j, cell in enumerate(r):
                row_line += f" {cell[:widths[j]]:<{widths[j]}} │"
            self.print_at(row + 2 + i, col, row_line)


class Dashboard:
    """Interactive Dashboard for PromptFlow"""

    def __init__(self, pf):
        self.pf = pf
        self.tui = TUI()
        self.current_view = "main"
        self.selected_index = 0
        self.running = True
        self.message = ""

        # View-specific data
        self.prompts = []
        self.workflows = []
        self.current_prompt = None
        self.current_workflow = None

    def run(self) -> None:
        """Run the dashboard"""
        try:
            # Set terminal to raw mode for key input
            self._setup_terminal()
            
            while self.running:
                self._render()
                self._handle_input()
        finally:
            self._restore_terminal()

    def _setup_terminal(self) -> None:
        """Setup terminal for TUI"""
        os.system("stty raw -echo")

    def _restore_terminal(self) -> None:
        """Restore terminal settings"""
        os.system("stty cooked echo")
        self.tui.clear()

    def _render(self) -> None:
        """Render current view"""
        self.tui.clear()
        self.tui.draw_header("🚀 PromptFlow Dashboard")

        if self.current_view == "main":
            self._render_main()
        elif self.current_view == "prompts":
            self._render_prompts()
        elif self.current_view == "prompt_detail":
            self._render_prompt_detail()
        elif self.current_view == "workflows":
            self._render_workflows()
        elif self.current_view == "workflow_detail":
            self._render_workflow_detail()
        elif self.current_view == "stats":
            self._render_stats()

        self.tui.draw_footer("↑↓ Navigate | Enter Select | q Quit | h Home")
        sys.stdout.flush()

    def _render_main(self) -> None:
        """Render main menu"""
        menu_items = [
            {"label": "📜 Prompts", "action": "prompts"},
            {"label": "📋 Workflows", "action": "workflows"},
            {"label": "📊 Statistics", "action": "stats"},
            {"label": "❌ Exit", "action": "exit"},
        ]
        self.tui.draw_box(3, 2, 40, 8, "Main Menu")
        self.tui.draw_menu(5, 4, menu_items, self.selected_index)

        # Quick stats
        stats = self.pf.get_stats()
        stats_text = f"""
Quick Stats:
  Prompts: {stats['prompts_count']}
  Workflows: {stats['workflows_count']}
  Executions: {stats['executions_count']}
        """
        self.tui.print_at(3, 50, f"{Colors.DIM}{stats_text}{Colors.RESET}")

    def _render_prompts(self) -> None:
        """Render prompts list"""
        self.prompts = self.pf.list_prompts()
        
        self.tui.print_at(3, 2, f"{Colors.BOLD}📜 Prompts ({len(self.prompts)}){Colors.RESET}")
        
        if not self.prompts:
            self.tui.print_at(5, 2, f"{Colors.DIM}No prompts found. Create one with: promptflow create <name>{Colors.RESET}")
            return

        headers = ["ID", "Name", "Category", "Versions"]
        widths = [10, 30, 12, 10]
        rows = [[p.id, p.name[:28], p.category.value, str(len(p.versions))] for p in self.prompts[:15]]
        
        self.tui.draw_table(5, 2, headers, rows, widths)
        
        # Highlight selected
        if self.selected_index < len(rows):
            self.tui.print_at(7 + self.selected_index, 2, f"{Colors.BG_CYAN}{Colors.BLACK} {rows[self.selected_index][0]:<10} {rows[self.selected_index][1]:<30} {rows[self.selected_index][2]:<12} {rows[self.selected_index][3]:<10} {Colors.RESET}")

    def _render_prompt_detail(self) -> None:
        """Render prompt detail view"""
        if not self.current_prompt:
            return

        p = self.current_prompt
        self.tui.print_at(3, 2, f"{Colors.BOLD}📜 Prompt: {p.name}{Colors.RESET}")
        self.tui.print_at(4, 2, f"{Colors.DIM}ID: {p.id} | Category: {p.category.value}{Colors.RESET}")
        
        # Content box
        content_lines = p.content.split("\n")[:10]
        self.tui.draw_box(6, 2, self.tui.width - 4, 8, "Content")
        for i, line in enumerate(content_lines):
            self.tui.print_at(7 + i, 4, line[:self.tui.width - 8])
        
        # Metadata
        meta = f"Version: {p.current_version} | Versions: {len(p.versions)} | Tags: {', '.join(p.tags) or 'None'}"
        self.tui.print_at(15, 2, f"{Colors.DIM}{meta}{Colors.RESET}")
        
        # Actions
        actions = ["[E] Edit", "[V] Versions", "[R] Run", "[D] Delete", "[B] Back"]
        self.tui.print_at(17, 2, "  ".join(actions))

    def _render_workflows(self) -> None:
        """Render workflows list"""
        self.workflows = self.pf.list_workflows()
        
        self.tui.print_at(3, 2, f"{Colors.BOLD}📋 Workflows ({len(self.workflows)}){Colors.RESET}")
        
        if not self.workflows:
            self.tui.print_at(5, 2, f"{Colors.DIM}No workflows found. Create one with: promptflow workflow create <name>{Colors.RESET}")
            return

        headers = ["ID", "Name", "Steps", "Updated"]
        widths = [10, 30, 10, 12]
        rows = [[w.id, w.name[:28], str(len(w.steps)), w.updated_at[:10]] for w in self.workflows[:15]]
        
        self.tui.draw_table(5, 2, headers, rows, widths)

    def _render_workflow_detail(self) -> None:
        """Render workflow detail view"""
        if not self.current_workflow:
            return

        w = self.current_workflow
        self.tui.print_at(3, 2, f"{Colors.BOLD}📋 Workflow: {w.name}{Colors.RESET}")
        self.tui.print_at(4, 2, f"{Colors.DIM}ID: {w.id} | Steps: {len(w.steps)}{Colors.RESET}")
        
        # Steps
        self.tui.print_at(6, 2, f"{Colors.BOLD}Steps:{Colors.RESET}")
        for i, step in enumerate(w.steps[:10]):
            step_text = f"  {i+1}. {step.name} ({step.type.value})"
            if step.prompt_id:
                step_text += f" → {step.prompt_id}"
            self.tui.print_at(7 + i, 2, step_text)
        
        # Actions
        actions = ["[R] Run", "[D] Delete", "[B] Back"]
        self.tui.print_at(18, 2, "  ".join(actions))

    def _render_stats(self) -> None:
        """Render statistics view"""
        stats = self.pf.get_stats()
        
        self.tui.print_at(3, 2, f"{Colors.BOLD}📊 Statistics{Colors.RESET}")
        
        stats_lines = [
            f"  📜 Prompts: {stats['prompts_count']}",
            f"  📋 Workflows: {stats['workflows_count']}",
            f"  💾 Backups: {stats['backups_count']}",
            f"  🚀 Executions: {stats['executions_count']}",
            f"  📁 Storage Size: {stats['storage_size_bytes']:,} bytes",
            f"  📂 Storage Path: {stats['storage_path']}",
            "",
            "  Categories:",
        ]
        
        for cat, count in stats['categories'].items():
            if count > 0:
                stats_lines.append(f"    {cat}: {count}")
        
        for i, line in enumerate(stats_lines):
            self.tui.print_at(5 + i, 2, line)

    def _handle_input(self) -> None:
        """Handle keyboard input"""
        try:
            key = sys.stdin.read(1)
        except Exception:
            return

        if key == "q":
            self.running = False
        elif key == "h":
            self.current_view = "main"
            self.selected_index = 0
        elif key == "\x1b":  # Arrow keys
            next_key = sys.stdin.read(2)
            if next_key == "[A":  # Up
                self.selected_index = max(0, self.selected_index - 1)
            elif next_key == "[B":  # Down
                self.selected_index += 1
        elif key == "\r" or key == "\n":  # Enter
            self._handle_select()
        elif key == "b":
            self._go_back()
        elif key == "e" and self.current_view == "prompt_detail":
            self.message = "Edit mode not available in TUI. Use CLI: promptflow edit <id>"
        elif key == "r" and self.current_view in ["prompt_detail", "workflow_detail"]:
            self.message = "Run not available in TUI. Use CLI: promptflow run <id>"

    def _handle_select(self) -> None:
        """Handle selection"""
        if self.current_view == "main":
            actions = ["prompts", "workflows", "stats", "exit"]
            if self.selected_index < len(actions):
                action = actions[self.selected_index]
                if action == "exit":
                    self.running = False
                else:
                    self.current_view = action
                    self.selected_index = 0

        elif self.current_view == "prompts":
            if self.selected_index < len(self.prompts):
                self.current_prompt = self.prompts[self.selected_index]
                self.current_view = "prompt_detail"

        elif self.current_view == "workflows":
            if self.selected_index < len(self.workflows):
                self.current_workflow = self.workflows[self.selected_index]
                self.current_view = "workflow_detail"

    def _go_back(self) -> None:
        """Go back to previous view"""
        if self.current_view in ["prompt_detail", "workflow_detail"]:
            self.current_view = self.current_view.replace("_detail", "") + "s"
            self.selected_index = 0
        elif self.current_view in ["prompts", "workflows", "stats"]:
            self.current_view = "main"
            self.selected_index = 0


def run_dashboard(pf) -> None:
    """Run the TUI dashboard"""
    dashboard = Dashboard(pf)
    dashboard.run()
