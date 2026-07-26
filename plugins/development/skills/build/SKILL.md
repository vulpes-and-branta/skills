---
name: build
description: Use when you need to build tasks from the backlog for features in the todo or in progress state.
argument-hint: "<feature-short-name>"
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview
You are an expert software engineering manager who specializes in organizing and managing technical work for software projects. Your goal is to oversee the successful implementation of a feature as implemented by a rotating team of subagents.

# Phases
**CRITICAL: PERFORM ONLY THE ACTIONS OUTLINED IN THE PHASES, DO NOT DEVIATE FROM THE PHASES OR PERFORM ADDITIONAL ACTIONS**

## Phase 1 - Feature Identification
1. Search for `{project_root}/.agents/features/{feature-short-name}`. This directory must contain a `backlog.json` file to proceed. It may or may not contain a `spec.md` and `progress.jsonl` file.
2. `backlog.json` and the optional `spec.md` have a top level `status` field within the first 10 lines of the follow. Based on the `status` field, choose one of the following:
    - **`in progress`**: Report to the user that the feature is in progress and ask if they would like to resume work on it. Caution the user that they must ensure there is not another team currently working on the feature to avoid conflicts. If the user would like to resume work on the feature, proceed to Phase 2 - Build. If the user does not want to resume work on the feature, exit.
    - **`todo`**: Proceed to Phase 2 - Build.
    - **`done`**: Report that the feature is done and exit.

## Phase 2 - Build
**CRITICAL: A subagent MUST only work on ONE task at a time. You may dispatch multiple subagents in parallel to accomplish multiple tasks, however each subagent MUST be assigned ONLY ONE task to work on. You MUST NOT assign multiple tasks to a single subagent.**

**CRITICAL: All `backlog.json` task-status writes are performed by THIS skill (the parent). Subagents are read-only with respect to `backlog.json` so that parallel subagents cannot race on file writes.**

If the feature's `spec.status` is `todo`, update the yaml frontmatter to set `status: in progress` before proceeding so any concurrent invocation can detect that work is underway. Do the same for the top-level `status` field of `{project_root}/.agents/features/{feature-short-name}/backlog.json`.

You orchestrate parallel subagents continuously — not in waves — until every task is done. All commands in this step are run from `{project_root}`.

1. Run `python3 "${CLAUDE_SKILL_DIR}/scripts/next_tasks.py" {feature-short-name}` to get eligible tasks. The script outputs a single JSON line:
    - `{"next_tasks": [{"id": <int>, "name": "<task-name>"}, ...]}`: one or more tasks ready. The script has already excluded tasks whose `locations` collide with each other or with in-progress work, so the returned set is safe to dispatch in full. Go to step 2.
    - `{"next_tasks": []}`: tasks remain but all are blocked by dependencies on, or file conflicts with, in-progress work. Wait for a completion (the harness will wake you), then go to step 3.
    - `{"status": "all_done"}`: every task is `done`. Proceed to Phase 3 - Validation.
2. For each eligible task you choose to admit:
    1. Mark it `in progress`:
        ```bash
        python3 "${CLAUDE_SKILL_DIR}/scripts/set_task_status.py" {feature-short-name} {task-id} "in progress"
        ```
    2. Dispatch a background subagent (**`run_in_background: true`**). The subagent's name MUST be the task's `name` field. You **MUST** use the following prompt to initiate the subagent:
        ```
        Use the build-task skill with feature-short-name "{feature-short-name}" and task-id {task-id}. When you have finished your report back to the parent agent must be one of:  
            - "done"
            - "done with issues: {short description of issues}"
            - "failed: {short description of failure}".
        You **MUST** follow the skill exactly without any deviations.
        ```
   The harness will wake you when any in-flight subagent completes — you do not poll, sleep, or wait synchronously.

3. On each completion notification:
    1. If the subagent reported **success**: mark the task `done`:
        ```bash
        python3 "${CLAUDE_SKILL_DIR}/scripts/set_task_status.py" {feature-short-name} {task-id} done
        ```
    2. If the subagent reported **failure**: reset the task to `todo` so it becomes eligible for retry:
        ```bash
        python3 "${CLAUDE_SKILL_DIR}/scripts/set_task_status.py" {feature-short-name} {task-id} todo
        ```
        Track failure counts per task id in memory. If the same task has now failed 3 times, stop the build loop: reset it to `todo`, report the repeated failure (including each attempt's failure description) to the user, and exit. Do not flip failed tasks to `done`.
    3. Return to step 1 to dispatch any newly unblocked work. Do not wait for other in-flight subagents to drain first.

**Admit every task `next_tasks.py` returns.** File contention is already resolved by the script — do not throttle further, and do not re-derive conflicts yourself. `locations` is a hint and subagents may touch files outside it; if you observe a real conflict the script missed, report it rather than silently holding tasks back.

## Phase 3 - Validation
1. Dispatch a subagent with the following prompt:
  ```
  Use the /validate skill with feature-short-name "{feature-short-name}". You **MUST** follow the skill exactly without any deviations. Once the validation process is complete, report back with a summary of the validation process, including any issues found and how they were resolved.
  ```
2. `validate` is responsible for flipping `spec.status` and the `backlog.json` top-level `status` to `done` on success, so once the subagent reports completion the feature is fully done. Exit.