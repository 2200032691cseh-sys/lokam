"""Validate local Markdown links and the implementation backlog."""

import re
import sys
from pathlib import Path

TASK_SECTIONS = {
    "Problem being solved",
    "Purpose",
    "Dependencies",
    "Prerequisites",
    "Scope",
    "Explicitly excluded scope",
    "Relevant architecture decisions",
    "Files to create or modify",
    "Database changes",
    "Implementation instructions",
    "Security considerations",
    "Privacy considerations",
    "Accessibility considerations",
    "Failure handling",
    "Required tests",
    "Acceptance criteria",
    "Verification commands",
    "Documentation updates",
    "Definition of done",
    "Rollback considerations",
}


def main():
    root = Path(__file__).resolve().parents[1]
    docs = sorted((root / "docs").rglob("*.md"))
    task_files = sorted((root / "tasks").glob("LOK-*.md"))
    index = root / "tasks" / "README.md"
    entries = re.findall(
        r"^\| \[(LOK-\d+)\]\(([^)]+)\)", index.read_text(encoding="utf-8"), re.M
    )
    expected = [(path.name[:7], path.name) for path in task_files]
    errors = []
    if entries != expected or len({key for key, _ in entries}) != len(entries):
        errors.append("Task index must list all task files in unique ID order.")

    dependencies = {}
    for path in task_files:
        task = path.read_text(encoding="utf-8")
        task_id = path.name[:7]
        names = set(re.findall(r"^## (.+)$", task, re.M))
        if missing := TASK_SECTIONS - names:
            errors.append(f"{path.name}: missing sections {', '.join(sorted(missing))}")
        match = re.search(r"^## Dependencies\n\n(.*?)(?=\n## |\Z)", task, re.M | re.S)
        dependencies[task_id] = (
            set(re.findall(r"\[(LOK-\d+)\]", match[1])) if match else set()
        )
        for dep in dependencies[task_id]:
            if dep >= task_id:
                errors.append(f"{path.name}: dependency {dep} must precede its task")

    pending = ["LOK-069"]
    reachable = set()
    while pending:
        task_id = pending.pop()
        if task_id not in reachable:
            reachable.add(task_id)
            pending.extend(dependencies.get(task_id, ()))
    if missing := dependencies.keys() - reachable:
        errors.append(
            f"Release is missing prerequisite tasks {', '.join(sorted(missing))}."
        )

    repository_docs = [
        root / name
        for name in ("README.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md")
    ]
    for path in [*repository_docs, *docs, *task_files, index]:
        for target in re.findall(
            r"\]\(([^)]+?\.md)(?:#[^)]*)?\)", path.read_text(encoding="utf-8")
        ):
            if "://" not in target and not (path.parent / target).is_file():
                errors.append(f"{path.relative_to(root)}: missing link target {target}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"Verified {len(docs)} planning documents and {len(task_files)} task specifications."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
