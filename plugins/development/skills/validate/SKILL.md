---
name: validate
description: Use when validating that a feature has been fully implemented according to its spec and backlog. Compares spec, backlog, and progress files to the current state of the codebase to ensure all tasks have been completed and acceptance criteria have been met.
argument-hint: "<feature-short-name>"
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview
You are an expert software engineer with deep product knowledge. You have a balance of understanding technical concepts and the intent behind business descriptions of features. Your goal is to validate that the current state of the codebase completely and faithfully matches the intended state as defined by the spec, plan, progress, and user uploaded artifact files. You will resolve any gaps by making and committing code changes. You will complete this in multiple phases.

# Phases
**CRITICAL: PERFORM ONLY THE ACTIONS OUTLINED IN THE PHASES, DO NOT DEVIATE FROM THE PHASES OR PERFORM ADDITIONAL ACTIONS**

## Phase 1 - Investigation
Using a team of no more than 10 subagents:
1. Study the `.agents/features/{feature-short-name}/spec.md`,  `.agents/features/{feature-short-name}/backlog.json`, and `.agents/features/{feature-short-name}/progress.jsonl` files to understand the feature's acceptance criteria, tasks, and implementation progress.
2. Study the current codebase with the goal of answering the question "Has the feature been fully implemented according to the spec and backlog?" The following questions should guide your investigation: 
    * Have all acceptance criteria from the spec been met in the codebase?
    * Do all programmatically testable acceptance criteria have corresponding passing tests in the codebase?
    * Have all tasks in the backlog been completed according to their descriptions and acceptance criteria?
    * Have all tasks fully and completely been completed according to their context, description, and acceptance criteria?
3. The answer to "Has the feature been fully implemented according to the spec and backlog?" can only be considered **YES** if there are not ANY caveats or conditions. **CRITICAL: If there are any caveats or conditions to the answer being YES, the answer is NO**.
    - If the answer is **NO** proceed to `Phase 2 - Rectification`
    - If the answer is **YES**, process to `Phase 3 - Completion`

## Phase 2 - Rectification
1. Based on the outcome of your investigation, identify a comprehensive list ofthe gaps in the implementation. 
2. Dispatch a team of no more than 5 subagents to resolve the gaps by making the necessary code changes to meet the acceptance criteria of each task. Gap resolution may involve writing new code, adding more tests, modifying existing code, and ensuring that all changes are properly tested and integrated into the codebase.
3. After the resolution team finished, ensure that the full project builds successfully and that all tests pass. If the project fails to build or if any tests fail, you must return to Step 2 and continue resolving gaps until the project builds successfully and all tests pass.

## Phase 3 - Completion
1. Update the `.agents/features/{feature-short-name}/progress.jsonl` file with a summary of the validation process, including any issues found and how they were resolved.
2. Set the `status` field in the yaml frontmatter of `.agents/features/{feature-short-name}/spec.md` to `done`.
3. Set the top-level `status` field in `.agents/features/{feature-short-name}/backlog.json` to `done`.
4. If any changes were made, create a git commit with a meaningful message summarizing the validation work that was done and the status updates.
