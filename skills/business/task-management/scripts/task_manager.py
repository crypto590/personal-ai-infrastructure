#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = []
# ///
"""
Task Manager - Unified task management with subcommands.

Usage:
    task_manager.py list [filter]
    task_manager.py update <id> [field] [value]
    task_manager.py complete <id>
    task_manager.py add
    task_manager.py create <file>
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ============================================================================
# TaskManager Core Library (inline)
# ============================================================================

class TaskManager:
    """Handles atomic task file operations with validation."""

    def __init__(self, task_dir: Optional[Path] = None):
        """
        Initialize TaskManager.

        Args:
            task_dir: Path to .claude/tasks/ directory.
                     If None, auto-detects project-local or global.
        """
        if task_dir is None:
            task_dir = self._detect_task_dir()

        self.task_dir = Path(task_dir)
        self.active_file = self.task_dir / "active.json"
        self.backlog_file = self.task_dir / "backlog.json"
        self.completed_file = self.task_dir / "completed.json"

        # Ensure directory exists
        self.task_dir.mkdir(parents=True, exist_ok=True)

        # Initialize files if they don't exist
        self._init_files()

    def _detect_task_dir(self) -> Path:
        """Detect task directory: project-local .claude/tasks/ or global ~/.claude/tasks/"""
        # Check for project-local first
        cwd = Path.cwd()
        project_tasks = cwd / ".claude" / "tasks"

        if project_tasks.exists() and (project_tasks / "active.json").exists():
            return project_tasks

        # Fall back to global PAI
        home = Path.home()
        global_tasks = home / ".claude" / "tasks"
        return global_tasks

    def _init_files(self):
        """Initialize JSON task files if they don't exist."""
        empty_container = {
            "version": "1.0.0",
            "source": None,
            "created": self._now(),
            "last_updated": self._now(),
            "tasks": []
        }

        for file_path in [self.active_file, self.backlog_file, self.completed_file]:
            if not file_path.exists():
                self._write_json(file_path, empty_container)

    def _now(self) -> str:
        """Get current timestamp in ISO 8601 format."""
        return datetime.now(timezone.utc).isoformat()

    def _read_json(self, file_path: Path) -> Dict:
        """Read and parse JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_json(self, file_path: Path, data: Dict):
        """Write JSON file atomically."""
        # Write to temp file first
        temp_file = file_path.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')

        # Atomic rename
        temp_file.replace(file_path)

    def get_next_id(self) -> int:
        """Get next available task ID across all files."""
        max_id = 0

        for file_path in [self.active_file, self.backlog_file, self.completed_file]:
            data = self._read_json(file_path)
            for task in data.get("tasks", []):
                task_id = task.get("id", 0)
                if task_id > max_id:
                    max_id = task_id

        return max_id + 1

    def find_task(self, task_id: int) -> Tuple[Optional[Dict], Optional[Path]]:
        """Find task by ID across all files."""
        for file_path in [self.active_file, self.backlog_file, self.completed_file]:
            data = self._read_json(file_path)
            for task in data.get("tasks", []):
                if task.get("id") == task_id:
                    return task, file_path

        return None, None

    def add_task(self, task: Dict, target_file: Optional[Path] = None) -> Dict:
        """Add new task to specified file (defaults to active.json)."""
        if target_file is None:
            target_file = self.active_file

        # Ensure task has required fields
        if "id" not in task:
            task["id"] = self.get_next_id()

        if "created" not in task:
            task["created"] = self._now()

        if "updated" not in task:
            task["updated"] = self._now()

        # Validate required fields
        required = ["id", "title", "status", "priority"]
        for field in required:
            if field not in task:
                raise ValueError(f"Task missing required field: {field}")

        # Normalize field order per TASK-MANAGEMENT.md schema
        normalized_task = {
            "id": task["id"],
            "title": task["title"],
            "status": task["status"],
            "priority": task["priority"],
            "created": task["created"],
            "updated": task["updated"],
            "completed": task.get("completed"),
            "source_file": task.get("source_file"),
            "source_line": task.get("source_line"),
            "notes": task.get("notes"),
            "tags": task.get("tags", []),
            "blocked_by": task.get("blocked_by"),
            "depends_on": task.get("depends_on", [])
        }

        # Read current data
        data = self._read_json(target_file)

        # Append normalized task
        data["tasks"].append(normalized_task)
        data["last_updated"] = self._now()

        # Write atomically
        self._write_json(target_file, data)

        return normalized_task

    def update_task(self, task_id: int, updates: Dict) -> Tuple[Dict, Path, Path]:
        """Update task fields."""
        task, source_file = self.find_task(task_id)

        if task is None:
            raise ValueError(f"Task #{task_id} not found")

        # Apply updates
        task.update(updates)
        task["updated"] = self._now()

        # Determine target file based on status
        status = task.get("status")
        if status == "completed":
            target_file = self.completed_file
            if "completed" not in task or task["completed"] is None:
                task["completed"] = self._now()
        elif status == "backlog":
            target_file = self.backlog_file
        else:  # pending, in_progress, blocked
            target_file = self.active_file

        # Normalize field order per TASK-MANAGEMENT.md schema
        normalized_task = {
            "id": task["id"],
            "title": task["title"],
            "status": task["status"],
            "priority": task["priority"],
            "created": task["created"],
            "updated": task["updated"],
            "completed": task.get("completed"),
            "source_file": task.get("source_file"),
            "source_line": task.get("source_line"),
            "notes": task.get("notes"),
            "tags": task.get("tags", []),
            "blocked_by": task.get("blocked_by"),
            "depends_on": task.get("depends_on", [])
        }

        # If file changed, move task
        if source_file != target_file:
            self._move_task(task_id, source_file, target_file, normalized_task)
        else:
            # Update in place
            self._update_task_in_file(task_id, source_file, normalized_task)

        return normalized_task, source_file, target_file

    def _update_task_in_file(self, task_id: int, file_path: Path, updated_task: Dict):
        """Update task in place within same file."""
        data = self._read_json(file_path)

        for i, task in enumerate(data["tasks"]):
            if task.get("id") == task_id:
                data["tasks"][i] = updated_task
                break

        data["last_updated"] = self._now()
        self._write_json(file_path, data)

    def _move_task(self, task_id: int, source_file: Path, target_file: Path, task: Dict):
        """Move task from source file to target file."""
        # Remove from source
        source_data = self._read_json(source_file)
        source_data["tasks"] = [t for t in source_data["tasks"] if t.get("id") != task_id]
        source_data["last_updated"] = self._now()

        # Add to target
        target_data = self._read_json(target_file)
        target_data["tasks"].append(task)
        target_data["last_updated"] = self._now()

        # Write both atomically
        self._write_json(source_file, source_data)
        self._write_json(target_file, target_data)

    def get_all_tasks(self, file_filter: Optional[str] = None) -> List[Dict]:
        """Get all tasks, optionally filtered by file."""
        files = []

        if file_filter is None:
            files = [self.active_file, self.backlog_file, self.completed_file]
        elif file_filter == "active":
            files = [self.active_file]
        elif file_filter == "backlog":
            files = [self.backlog_file]
        elif file_filter == "completed":
            files = [self.completed_file]

        all_tasks = []
        for file_path in files:
            data = self._read_json(file_path)
            all_tasks.extend(data.get("tasks", []))

        return all_tasks


# ============================================================================
# Subcommand Implementations
# ============================================================================

def cmd_list(args):
    """List active tasks."""
    tm = TaskManager()
    tasks = tm.get_all_tasks("active")

    if not tasks:
        print("📭 NO ACTIVE TASKS\n")
        print("Use the task management skill to create tasks")
        print("Or run: /tasks")
        return

    # Apply filter if provided
    filter_arg = args.filter
    if filter_arg:
        if filter_arg in ["low", "medium", "high", "critical"]:
            tasks = [t for t in tasks if t.get("priority") == filter_arg]
        elif filter_arg in ["pending", "in_progress", "blocked"]:
            tasks = [t for t in tasks if t.get("status") == filter_arg]

        if not tasks:
            print(f"📭 NO TASKS MATCHING FILTER: {filter_arg}\n")
            return

    # Group by priority
    priority_groups = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": []
    }

    for task in tasks:
        priority = task.get("priority", "medium")
        if priority in priority_groups:
            priority_groups[priority].append(task)

    # Sort by status within groups
    def sort_by_status(tasks_list):
        status_order = {"in_progress": 0, "blocked": 1, "pending": 2}
        return sorted(tasks_list, key=lambda t: (
            status_order.get(t.get("status"), 3),
            t.get("created", "")
        ))

    # Display
    print("🎯 ACTIVE TASKS\n")

    priority_emoji = {
        "critical": "🚨",
        "high": "🔥",
        "medium": "📋",
        "low": "📌"
    }

    priority_label = {
        "critical": "CRITICAL PRIORITY",
        "high": "HIGH PRIORITY",
        "medium": "MEDIUM PRIORITY",
        "low": "LOW PRIORITY"
    }

    total_tasks = 0
    status_counts = {"in_progress": 0, "pending": 0, "blocked": 0}

    for priority in ["critical", "high", "medium", "low"]:
        priority_tasks = sort_by_status(priority_groups[priority])

        if not priority_tasks:
            continue

        emoji = priority_emoji[priority]
        label = priority_label[priority]

        print(f"{emoji} {label}")

        for task in priority_tasks:
            total_tasks += 1
            status = task.get("status", "pending")
            status_counts[status] = status_counts.get(status, 0) + 1

            task_id = task.get("id")
            title = task.get("title")
            status_str = f"[{status}]"

            print(f"#{task_id} - {title} {status_str}")

            # Show metadata
            created = task.get("created")
            updated = task.get("updated")
            source_file = task.get("source_file")
            source_line = task.get("source_line")

            metadata_parts = []
            if created:
                metadata_parts.append(f"Created: {format_date(created)}")
            if updated and updated != created:
                metadata_parts.append(f"Updated: {format_date(updated)}")
            if source_file:
                source_str = source_file
                if source_line:
                    source_str += f":{source_line}"
                metadata_parts.append(f"Source: {source_str}")

            if metadata_parts:
                print(f"     {' | '.join(metadata_parts)}")

            # Show notes
            notes = task.get("notes")
            if notes:
                print(f"     Notes: {notes}")

            # Show blocked reason
            if status == "blocked" and task.get("blocked_by"):
                print(f"     Blocked by: {task.get('blocked_by')}")

            print()

    # Summary
    print("---")
    status_parts = []
    if status_counts.get("in_progress"):
        status_parts.append(f"{status_counts['in_progress']} in_progress")
    if status_counts.get("pending"):
        status_parts.append(f"{status_counts['pending']} pending")
    if status_counts.get("blocked"):
        status_parts.append(f"{status_counts['blocked']} blocked")

    summary = ", ".join(status_parts) if status_parts else "no tasks"
    print(f"Total: {total_tasks} tasks ({summary})")


def cmd_update(args):
    """Update task fields."""
    task_id = args.id
    tm = TaskManager()

    # Find task first
    task, source_file = tm.find_task(task_id)

    if task is None:
        print(f"❌ ERROR: Task #{task_id} not found")
        print("\nRun: task_manager.py list")
        sys.exit(1)

    # Display current task
    print(f"📋 CURRENT TASK\n")
    print(f"#{task['id']} - {task['title']}")
    print(f"Priority: {task['priority']}")
    print(f"Status: {task['status']}")
    print(f"Created: {task['created']}")
    print(f"Updated: {task['updated']}")
    if task.get('notes'):
        print(f"Notes: {task['notes']}")
    if task.get('tags'):
        print(f"Tags: {', '.join(task['tags'])}")
    if task.get('blocked_by'):
        print(f"Blocked: {task['blocked_by']}")
    print()

    # Parse field and value
    field = args.field
    value = args.value

    if not field:
        print("❌ ERROR: Field required")
        print("Usage: task_manager.py update <id> <field> <value>")
        sys.exit(1)

    # Validate field
    valid_fields = ["status", "priority", "notes", "tags", "blocked_by", "title"]

    if field not in valid_fields:
        print(f"❌ ERROR: Invalid field '{field}'")
        print(f"Valid fields: {', '.join(valid_fields)}")
        sys.exit(1)

    # Validate value based on field
    if field == "status":
        valid_statuses = ["pending", "in_progress", "blocked", "backlog", "completed"]
        if value not in valid_statuses:
            print(f"❌ ERROR: Invalid status '{value}'")
            print(f"Valid statuses: {', '.join(valid_statuses)}")
            sys.exit(1)

    elif field == "priority":
        valid_priorities = ["low", "medium", "high", "critical"]
        if value not in valid_priorities:
            print(f"❌ ERROR: Invalid priority '{value}'")
            print(f"Valid priorities: {', '.join(valid_priorities)}")
            sys.exit(1)

    elif field == "tags":
        # Parse comma-separated tags
        value = [tag.strip() for tag in value.split(',')]

    # Store old value for display
    old_value = task.get(field)

    # Perform update
    try:
        updates = {field: value}
        updated_task, source_file, target_file = tm.update_task(task_id, updates)

        # Display confirmation
        if source_file == target_file:
            print("✅ TASK UPDATED\n")
        else:
            print("✅ TASK UPDATED & MOVED\n")

        print(f"#{updated_task['id']} - {updated_task['title']}")
        print(f"{field.replace('_', ' ').title()}: {old_value} → {value}")
        print(f"Updated: {updated_task['updated']}")

        if source_file != target_file:
            print(f"\nMoved: {source_file.name} → {target_file.name}")

        print("\nChanges:")
        print(f"- {field}: {old_value} → {value}")

        print("\nRun: task_manager.py list")

    except Exception as e:
        print(f"❌ ERROR: Failed to update task")
        print(f"Details: {e}")
        sys.exit(1)


def cmd_complete(args):
    """Complete and archive task."""
    task_id = args.id
    tm = TaskManager()

    # Find task
    task, source_file = tm.find_task(task_id)

    if task is None:
        print(f"❌ ERROR: Task #{task_id} not found")
        print("\nRun: task_manager.py list")
        sys.exit(1)

    # Check if already completed
    if task.get("status") == "completed":
        print(f"⚠️  WARNING: Task #{task_id} already completed")
        print(f"Completed: {task.get('completed')}")
        print("\nTask is already in completed.json")
        sys.exit(0)

    # Mark as completed
    try:
        completed_time = datetime.now(timezone.utc).isoformat()

        updates = {
            "status": "completed",
            "completed": completed_time
        }

        updated_task, old_file, new_file = tm.update_task(task_id, updates)

        # Calculate duration
        duration = calculate_duration(task["created"], completed_time)

        # Display confirmation
        print("✅ TASK COMPLETED\n")
        print(f"#{updated_task['id']} - {updated_task['title']}")
        print(f"Completed: {completed_time}")
        print(f"Duration: {duration} (created → completed)")
        print("\nTask moved to archive (completed.json)")
        print("\nRun: task_manager.py list")

    except Exception as e:
        print(f"❌ ERROR: Failed to complete task")
        print(f"Details: {e}")
        sys.exit(1)


def cmd_create(args):
    """Parse markdown file and create tasks."""
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"❌ ERROR: File not found: {file_path}")
        sys.exit(1)

    # Read markdown file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ ERROR: Could not read file")
        print(f"Details: {e}")
        sys.exit(1)

    # Parse markdown into tasks
    tm = TaskManager()

    tasks_created = []
    tasks_completed = []

    lines = content.split('\n')
    current_priority = "medium"
    current_heading = None
    line_number = 0

    for line in lines:
        line_number += 1
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Check for priority headers
        if stripped.startswith('#'):
            heading_text = stripped.lstrip('#').strip().upper()
            current_heading = stripped

            # Extract priority from heading
            if 'CRITICAL' in heading_text:
                current_priority = "critical"
            elif 'HIGH' in heading_text:
                current_priority = "high"
            elif 'MEDIUM' in heading_text:
                current_priority = "medium"
            elif 'LOW' in heading_text:
                current_priority = "low"

            continue

        # Check for task markers
        if stripped.startswith('- [ ]') or stripped.startswith('- [x]'):
            is_completed = stripped.startswith('- [x]')

            # Extract title (remove checkbox)
            title = stripped[5:].strip()

            # Skip if title is empty
            if not title:
                continue

            # Extract tags from title (look for common keywords)
            tags = []
            tag_keywords = ['backend', 'frontend', 'auth', 'api', 'ui', 'database',
                           'testing', 'docs', 'documentation', 'deployment', 'security']

            title_lower = title.lower()
            for keyword in tag_keywords:
                if keyword in title_lower:
                    tags.append(keyword)

            # Create task object
            task = {
                "title": title,
                "status": "completed" if is_completed else "pending",
                "priority": current_priority,
                "source_file": str(file_path),
                "source_line": line_number,
                "notes": None,
                "tags": tags,
                "blocked_by": None,
                "depends_on": []
            }

            # Check for blocked indicator
            if '🚫' in title or 'BLOCKED' in title.upper():
                task["status"] = "blocked"

            # Add task to appropriate file
            if is_completed:
                task["completed"] = tm._now()
                tm.add_task(task, tm.completed_file)
                tasks_completed.append(task)
            else:
                tm.add_task(task, tm.active_file)
                tasks_created.append(task)

        # Check for indented notes (acceptance criteria)
        elif stripped.startswith('  - ') and tasks_created:
            # Add as notes to last created task
            note_text = stripped[4:].strip()
            last_task = tasks_created[-1]

            if last_task.get("notes"):
                last_task["notes"] += f" {note_text}"
            else:
                last_task["notes"] = note_text

            # Update task in active.json with notes
            tm.update_task(last_task["id"], {"notes": last_task["notes"]})

    # Display summary
    print(f"✅ TASKS CREATED FROM: {file_path}\n")
    print("📊 SUMMARY:")
    print(f"- Created: {len(tasks_created)} tasks in active.json")
    print(f"- Completed: {len(tasks_completed)} tasks in completed.json")
    print(f"- Total: {len(tasks_created) + len(tasks_completed)} tasks parsed\n")

    # Group by priority
    def group_by_priority(task_list):
        groups = {"critical": [], "high": [], "medium": [], "low": []}
        for task in task_list:
            priority = task.get("priority", "medium")
            if priority in groups:
                groups[priority].append(task)
        return groups

    priority_emoji = {
        "critical": "🚨",
        "high": "🔥",
        "medium": "📋",
        "low": "📌"
    }

    created_groups = group_by_priority(tasks_created)

    for priority in ["critical", "high", "medium", "low"]:
        priority_tasks = created_groups[priority]
        if not priority_tasks:
            continue

        emoji = priority_emoji[priority]
        label = f"{priority.upper()} PRIORITY"

        print(f"{emoji} {label} ({len(priority_tasks)} tasks)")
        for task in priority_tasks:
            print(f"#{task['id']} - {task['title']}")
        print()

    if tasks_completed:
        print(f"✅ ALREADY COMPLETED ({len(tasks_completed)} tasks)")
        for task in tasks_completed:
            print(f"#{task['id']} - {task['title']}")
        print()

    print("---")
    print("Run: task_manager.py list")


# ============================================================================
# Helper Functions
# ============================================================================

def format_date(iso_date: str) -> str:
    """Format ISO 8601 date to readable format."""
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_date


def calculate_duration(created_str: str, completed_str: str) -> str:
    """Calculate human-readable duration between timestamps."""
    try:
        created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
        completed = datetime.fromisoformat(completed_str.replace('Z', '+00:00'))
        delta = completed - created

        total_seconds = int(delta.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0 and days == 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

        if not parts:
            return "less than a minute"

        return ", ".join(parts)

    except Exception:
        return "unknown"


# ============================================================================
# Main CLI
# ============================================================================

def main():
    """Main entry point with subcommand routing."""
    parser = argparse.ArgumentParser(
        description="Task Manager - Unified task management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List subcommand
    parser_list = subparsers.add_parser("list", help="List active tasks")
    parser_list.add_argument("filter", nargs="?", help="Filter by priority or status")

    # Update subcommand
    parser_update = subparsers.add_parser("update", help="Update task field")
    parser_update.add_argument("id", type=int, help="Task ID")
    parser_update.add_argument("field", nargs="?", help="Field to update")
    parser_update.add_argument("value", nargs="?", help="New value")

    # Complete subcommand
    parser_complete = subparsers.add_parser("complete", help="Complete and archive task")
    parser_complete.add_argument("id", type=int, help="Task ID")

    # Create subcommand
    parser_create = subparsers.add_parser("create", help="Parse markdown file and create tasks")
    parser_create.add_argument("file", help="Path to markdown file (PRD, sprint plan, etc.)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to subcommand
    if args.command == "list":
        cmd_list(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "complete":
        cmd_complete(args)
    elif args.command == "create":
        cmd_create(args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
