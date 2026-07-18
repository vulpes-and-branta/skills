---
name: build-task
description: Use when building a single task from a backlog.json file.
argument-hint: "<feature-short-name> <task-id>"
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview
You are a subagent implementing a single task from a feature's planned backlog in parellel with other subagents. You have been provided with a `{feature-short-name}` and `{task-id}` to help you identify the task you must implement. You will implement the singular task described by the task JSON blob, verify it meets acceptance criteria, and report your outcome. You will perform this task in multiple phases. Your parent agent has already marked your task as `in progress` before dispatching you, and will mark it `done` after you report successful completion. Do NOT call `set_task_status.py` from this skill — doing so would race with parallel subagents.

# Concurrency Rules
**CRITICAL: Never deviate from these rules - if you strongly feel a deviation is necessary you must report it to the parent agent and they will handle the issue. Deviating from these rule risk introducing race conditions and conflicts with other subagents.**

## Staging and committing
1. Never run git add -A, git add ., or git commit -a. Only git add the exact files in your task's locations (plus progress.jsonl and backlog.json, which the parent owns and may leave staged from its own status flips).
2. Always pass an explicit pathspec on the commit itself: git commit -m "..." -- <file1> <file2> .... A bare git commit after git add commits everything currently staged, including files a sibling agent staged moments earlier — this is the #1 cause of sweep-in.

## Forbidden operations
4. Never run git reset (any form), git rebase, git commit --amend, git checkout -- <path>, git restore <path> (unstaged form), git clean, or git push --force — on your own commits or anyone else's. These mutate shared branch history or the working tree in ways a concurrent sibling can't see coming.

# Phases
## Phase 1: Investigation
1. Read the progress of tasks your task depended on by running (from `{project_root}`):
    ```bash
    python3 "${CLAUDE_SKILL_DIR}/scripts/get_dependency_progress.py" {feature-short-name} {task-id}
    ```
    This will provide information about the progress of tasks your task depends on, helping you understand the current state of the feature implementation and avoid duplicating work or conflicting with changes made by previous tasks.

2. Retrieve your task JSON blob by running (from `{project_root}`):
    ```bash
    python3 "${CLAUDE_SKILL_DIR}/scripts/get_task.py" {feature-short-name} {task-id}
    ```
    The script prints the matched task as JSON to stdout. If it exits non-zero (for example, no task with id `{task-id}` exists in the backlog), report the error to the parent agent and exit. 

3. Read the task's `context`, `description`, and `acceptanceCriteria` to understand why you are performing this task, what task you are performing, and how to know when you have completed the task successfully.
4. Study the files listed in `references` as this will give you valuable context in terms of how to implement the task in accordance with existing patterns.
5. Study the files listed in `locations` as this will tell you where the expected code changes will need to be made. If the files do not exist, you will need to create them as part of your implementation.

## Phase 2: Build
1. Implement the task based on your investigation.
2. Determine if you need to refactor any existing code to accommodate the new changes or expected workflows. If so, perform the necessary refactoring.
3. Ensure that all new code changes have appropriate tests written. The newly written test relevant to your changes must all pass.
5. Append a terse entry to `{project_root}/.agents/features/{feature-short-name}/progress.jsonl` following this format:
```json
{ "taskId": <task-id>, "summary": "<short summary of work done>", "deviations": ["<short description of any non-obvious deviations from the tasks description - empty string if none>"] }
``` 
6. Commit your work using `git commit -m "..." -- <file1> <file2> <fileN>`. You must not commit files that you did not directly modify. Writea meaningful message that captures all changes made during this task.
7. Report your outcome to the parent agent. Your response must be one of:  
            - "done"
            - "done with issues: {short description of issues}"
            - "failed: {short description of failure}".
The parent is responsible for flipping the task status to `done` and committing that change.

# Pitfalls to Avoid
- **Skipping investigation:** Do not start implementing without understanding the existing codebase and how the task fits in.
- **Ignoring prior progress:** Read progress.jsonl to avoid duplicating work or conflicting with changes made by previous tasks.
- **Breaking existing functionality:** When making code changes, ensure existing tests continue to pass and no regressions are introduced.
- **Missing acceptance criteria tests:** If an acceptance criterion is programmatically testable, it should have a corresponding test.
- **Incomplete implementation:** Ensure the task fully meets its acceptance criteria before reporting `done`.
