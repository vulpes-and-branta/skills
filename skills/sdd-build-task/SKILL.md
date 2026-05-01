---
name: sdd-build-task
description: Use when building a single task from a backlog.json file.
argument-hint: "<feature-short-name> <task-id>"
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview
You are a subagent implementing a single task from a feature's planned backog. You have been provided with a `{feature-short-name}` and `{task-id}` to help you identify the task you must implement. You will implement the singular task described by the task jason blob, verify it meets acceptance criteria, and report your outcome. You will perform this task in multiple phases.

**CRITICAL:** This skill is read-only with respect to `backlog.json`. The parent (`sdd-build`) has already marked your task as `in progress` before dispatching you, and will mark it `done` after you report successful completion. Do NOT call `set_task_status.py` from this skill — doing so would race with parallel subagents.

# Phases
## 1. Investigation
1. Retrieve the task JSON blob by running (from `{project_root}`):
    ```bash
    python scripts/get_task.py {feature-short-name} {task-id}
    ```
    The script prints the matched task as JSON to stdout. If it exits non-zero (for example, no task with id `{task-id}` exists in the backlog), report the error to the parent agent and exit.

2. Read `{project_root}/.agents/features/{feature-short-name}/progress.md` to understand the current progress made on the feature. This file will provide valuable context to help you understand the current state of the feature implementation and avoid duplicating work or conflicting with changes made by previous tasks.
    * If this file does not exist, create it as an empty `.md` file.
    * If this file is more than 10,000 characters, summarize older entries to keep it concise and focused on the most important details.
3. Read the task's `context`, `description`, and `acceptanceCritera` to understand why you are performing this task, what task you are performing, and how to know when you have completed the task successfully.
4. Study the files listed in `references` as this will give you valuable context in terms of how to implement the task.
5. Study the files listed in `locations` as this will tell you where the expected code changes will need to be made. If the files do not exist, you will need to create them as part of your implementation.

## 2. Build
1. Follow test-drive-development (TDD) principles to implement the task. This means you should write tests for any acceptance criteria that are programmatically testable before you implement the functionality to satisfy those acceptance criteria. Verify that these tests fail (the RED step in TDD's RED-GREEN-REFACTOR cycle) before progressing.
2. Implement the required changes in the codebase based on your investigation. Verify written tests pass after implementing the functionality (the GREEN step in TDD's RED-GREEN-REFACTOR cycle) before progressing.
3. Determine if you need to refactor any existing code to accommodate the new changes or expected workflows. If so, perform the necessary refactoring while ensuring that all tests continue to pass (the REFACTOR step in TDD's RED-GREEN-REFACTOR cycle) before progressing.
4. Ensure that the project builds successfully. If the build fails, fix the offending code. **CRITICAL: Fix the offending code even if your changes were not the cause of it.**
5. Ensure that all tests pass. If tests fail, fix the offending code. **CRITICAL: Fix the offending code even if your changes were not the cause of it.**
6. Append your progress to `{project_root}/.agents/features/{feature-short-name}/progress.md` with your progress. This update should act as an important note to the next engineer working on the feature.
7. Create a single git commit with a meaningful message summarizing the work done. The commit MUST capture all changes made during this task: code, tests, and the `progress.md` update. The parent's earlier `in progress` flip in `backlog.json` will also be picked up by this commit if it is uncommitted at this point — that is intentional.
8. Report your outcome to the parent agent. The parent is responsible for flipping the task status to `done` and committing that change.

# Pitfalls to Avoid
- **Skipping investigation:** Do not start implementing without understanding the existing codebase and how the task fits in.
- **Ignoring prior progress:** Read progress.md to avoid duplicating work or conflicting with changes made by previous tasks.
- **Breaking existing functionality:** When making code changes, ensure existing tests continue to pass and no regressions are introduced.
- **Forgetting to build and test:** Always build and test the project after making changes to confirm nothing is broken.
- **Missing acceptance criteria tests:** If an acceptance criterion is programmatically testable, it should have a corresponding test.
- **Incomplete implementation:** Ensure the task fully meets its acceptance criteria before reporting `done`.
