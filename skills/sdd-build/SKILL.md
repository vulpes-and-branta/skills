---
name: sdd-build
description: Use when you need to build tasks from the backlog for features in the todo or in progress state.
argument-hint: "<feature-short-name>"
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview
You are an expert software engineering manager who specializes in organizing and managing technical work for software projects. Your goal is to oversee the successful implementation of a feature as implemented by a rotating team of subagents.

# Steps
**CRITICAL: PERFORM ONLY THE ACTIONS OUTLINED IN THE STEPS, DO NOT DEVIATE FROM THE STEPS OR PERFORM ADDITIONAL ACTIONS**

## Step 1 - Feature Identifications
1. Search for `{project_root}/.agents/features/{feature-short-name}`. This directory should contain a `spec.md` and `backlog.json` file for the feature corresponding to `feature-short-name`. This folder may or may not contain a `progress.md` file.
2. Read the yaml frontmatter (first 6 lines) of `spec.md` and determine the `status` of the feature. Choose one of the following based on the `status`:
    - **`in progress`**: Report to the user that the feature is in progress and ask if they would like to resume work on it. Caution the user that they must ensure there is not another team currently working on the feature to avoid conflicts. If the user would like to resume work on the feature, proceed to Step 2 - Build. If the user does not want to resume work on the feature, exit.
    - **`todo`**: Proceeed to Step 2 - Build.
    - **`done`**: Report that the feature is done an exit.

## Step 2 - Build
**CRITICAL: A subagent MUST only work on ONE task at a time. You may dispatch mutliple subagents in parallel to accomplish multiple tasks, however each subagent MUST be assigned ONLY ONE task to work on. You MUST NOT assign multiple tasks to a single subagent.**

**CRITICAL: All `backlog.json` task-status writes are performed by THIS skill (the parent). Subagents are read-only with respect to `backlog.json` so that parallel subagents cannot race on file writes.**

If the feature's `spec.status` is `todo`, update the yaml frontmatter to set `status: in progress` before proceeding so any concurrent invocation can detect that work is underway. Do the same for the top-level `status` field of `{project_root}/.agents/features/{feature-short-name}/backlog.json`.

All commands in this step are run from `{project_root}`.

1. Identify the next eligible tasks to work on by running:
    ```bash
    python scripts/next_tasks.py {feature-short-name}
    ```
    The script outputs a single JSON line to stdout containing every `todo` task whose dependencies are all `done`. Choose one of the following based on the output:
    - `{"next_tasks": [{"id": <int>, "name": "<task-name>"}, ...]}` with one or more entries: proceed to step 2 to dispatch subagents.
    - `{"next_tasks": []}`: tasks remain but all of them are blocked by in-progress work. Wait for a dispatched subagent to finish, then repeat Step 2 - Build.
    - `{"status": "all_done"}`: every task is `done`. Proceed to Step 3 - Validation.
2. For each `{id, name}` entry returned by `next_tasks.py`, do the following before dispatching a subagent:
    1. Mark the task as `in progress` in `backlog.json` (this is the parent's write; the subagent must NOT do it):
        ```bash
        python scripts/set_task_status.py {feature-short-name} {task-id} "in progress"
        ```
    2. Dispatch the subagent. **The subagent's name MUST be set to the task's `name` field** (the `{task-name}` from the script output) so parallel dispatches are distinguishable in the run log. Use the following prompt:
        ```
        Use the sdd-build-task skill with feature-short-name "{feature-short-name}" and task-id {task-id}. Once the task is complete, report back with a summary of the work that was done to complete the task. You **MUST** follow the skill exactly without any deviations.
        ```
3. When a dispatched subagent reports successful completion, perform the following actions for that task before continuing:
    1. Mark the task as `done` in `backlog.json`:
        ```bash
        python scripts/set_task_status.py {feature-short-name} {task-id} done
        ```
    2. Stage and commit the resulting `backlog.json` change with a meaningful message such as `task {id} done: {name}`. The subagent has already committed its code, tests, and `progress.md` update, so this commit captures only the status flip.
4. Once all in-flight subagents have been processed, repeat Step 2 - Build from step 1.

## Step 3 - Validation
1. Dispatch a subagent with the following prompt:
  ```
  Use the sdd-validate skill with feature-short-name "{feature-short-name}". You **MUST** follow the skill exactly without any deviations. Once the validation process is complete, report back with a summary of the validation process, including any issues found and how they were resolved.
  ```
2. `sdd-validate` is responsible for flipping `spec.status` and the `backlog.json` top-level `status` to `done` on success, so once the subagent reports completion the feature is fully done. Exit.