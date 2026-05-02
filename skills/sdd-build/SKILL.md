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

You orchestrate parallel subagents continuously — not in waves — until every task is done. All commands in this step are run from `{project_root}`.

1. Run `python3 "${CLAUDE_SKILL_DIR}/scripts/next_tasks.py" {feature-short-name}` to get eligible tasks. The script outputs a single JSON line:
    - `{"next_tasks": [{"id": <int>, "name": "<task-name>"}, ...]}`: one or more tasks ready. Go to step 2.
    - `{"next_tasks": []}`: tasks remain but all are blocked by in-progress work. Wait for a completion (the harness will wake you), then go to step 3.
    - `{"status": "all_done"}`: every task is `done`. Proceed to Step 3 - Validation.
2. For each eligible task you choose to admit:
    1. Mark it `in progress`:
        ```bash
        python3 "${CLAUDE_SKILL_DIR}/scripts/set_task_status.py" {feature-short-name} {task-id} "in progress"
        ```
    2. Dispatch a subagent using the Task tool with **`run_in_background: true`**. The subagent's name MUST be the task's `name` field. Prompt:
        ```
        Use the sdd-build-task skill with feature-short-name "{feature-short-name}" and task-id {task-id}. Once the task is complete, report back with a summary of the work that was done to complete the task. You **MUST** follow the skill exactly without any deviations.
        ```
   The harness will wake you when any in-flight subagent completes — you do not poll, sleep, or wait synchronously.
3. On each completion notification:
    1. If the subagent reported **success**: mark the task `done`:
        ```bash
        python3 "${CLAUDE_SKILL_DIR}/scripts/set_task_status.py" {feature-short-name} {task-id} done
        ```
    2. If the subagent reported **failure**: leave the task `in progress` and report the failure to the user. Do not flip to `done`.
    3. Return to step 1 to dispatch any newly unblocked work. Do not wait for other in-flight subagents to drain first.

**You set the in-flight count.** Default: admit every eligible task. Throttle only on concrete same-file write contention. `locations` is a hint — subagents touch files outside it. Throttle order: highest fan-out first, lowest id breaks ties.

## Step 3 - Validation
1. Dispatch a subagent with the following prompt:
  ```
  Use the sdd-validate skill with feature-short-name "{feature-short-name}". You **MUST** follow the skill exactly without any deviations. Once the validation process is complete, report back with a summary of the validation process, including any issues found and how they were resolved.
  ```
2. `sdd-validate` is responsible for flipping `spec.status` and the `backlog.json` top-level `status` to `done` on success, so once the subagent reports completion the feature is fully done. Exit.