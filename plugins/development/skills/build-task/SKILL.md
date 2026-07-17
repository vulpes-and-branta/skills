---
name: build-task
description: Use when building a single task from a backlog.json file.
argument-hint: "<feature-short-name> <task-id>"
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview
You are a subagent implementing a single task from a feature's planned backlog. You have been provided with a `{feature-short-name}` and `{task-id}` to help you identify the task you must implement. You will implement the singular task described by the task JSON blob, verify it meets acceptance criteria, and report your outcome. You will perform this task in multiple phases.

**CRITICAL:** This skill is read-only with respect to `backlog.json`. The parent agent has already marked your task as `in progress` before dispatching you, and will mark it `done` after you report successful completion. Do NOT call `set_task_status.py` from this skill — doing so would race with parallel subagents.

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
1. Implement the task based on your investigation. Verify all newly written tests pass after implementing the functionality before progressing.
2. Determine if you need to refactor any existing code to accommodate the new changes or expected workflows. If so, perform the necessary refactoring while ensuring that all tests continue to pass before progressing.
3. Ensure that the full project builds successfully. If the build fails, fix the offending code. **CRITICAL: Fix the offending code even if your changes were not the cause of it.**
4. Ensure that all tests pass. If tests fail, fix the offending code. **CRITICAL: Fix the offending code even if your changes were not the cause of it.**
5. Append a terse entry to `{project_root}/.agents/features/{feature-short-name}/progress.jsonl` following this format:
```json
{ "taskId": <task-id>, "summary": "<short summary of work done>", "deviations": ["<short description of any non-obvious deviations from the tasks description - empty string if none>"] }
``` 
6. Create a single git commit with a meaningful message summarizing the work done. The commit MUST capture all changes made during this task: code, tests, and the `progress.jsonl` update. The parent's earlier `in progress` flip in `backlog.json` will also be picked up by this commit if it is uncommitted at this point — that is intentional.
7. Report your outcome to the parent agent. Your response must be one of:  
            - "done"
            - "done with issues: {short description of issues}"
            - "failed: {short description of failure}".
The parent is responsible for flipping the task status to `done` and committing that change.

# Pitfalls to Avoid
- **Skipping investigation:** Do not start implementing without understanding the existing codebase and how the task fits in.
- **Ignoring prior progress:** Read progress.jsonl to avoid duplicating work or conflicting with changes made by previous tasks.
- **Breaking existing functionality:** When making code changes, ensure existing tests continue to pass and no regressions are introduced.
- **Forgetting to build and test:** Always build and test the project after making changes to confirm nothing is broken.
- **Missing acceptance criteria tests:** If an acceptance criterion is programmatically testable, it should have a corresponding test.
- **Incomplete implementation:** Ensure the task fully meets its acceptance criteria before reporting `done`.
