---
name: sdd-validate
description: Use when validating that a feature has been fully implemented according to its spec and backlog. Compares spec, backlog, and progress files to the current state of the codebase to ensure all tasks have been completed and acceptance criteria have been met.
argument-hint: "<feature-short-name>"
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview
You are an expert software engineer with deep product knowledge. You have a balance of understanding technical concepts and the intent behind business descriptions of features. Your goal is to validate that the current state of the codebase completely and faithfully matches the intended state as defined by the spec, plan, progress, and user uploaded artifact files. You will resolve any gaps by making, committing, and pushing code changes. You will complete this in multiple phases.

# Steps
**CRITICAL: PERFORM ONLY THE ACTIONS OUTLINED IN THE STEPS, DO NOT DEVIATE FROM THE STEPS OR PERFORM ADDITIONAL ACTIONS**

## Step 1 - Investigation
Using up to 10 subagents:
1. Study the `.agents/features/{feature-short-name}/spec.md`,  `.agents/features/{feature-short-name}/backlog.json`, and `.agents/features/{feature-short-name}/progress.md` files to understand the feature's acceptance criteria, tasks, and implementation progress.
2. Study the current codebase with the goal of answering the question "Has the feature been fully implemented according to the spec and backlog?" The following questions should guide your investigation: 
    * Have all acceptance criteria from the spec been met in the codebase?
    * Do all programmatically testable acceptance criteria have corresponding passing tests in the codebase?
    * Have all tasks in the backlog been completed according to their descriptions and acceptance criteria?
    * Have all tasks fully and completely been completed accoridng to their context, description, and acceptance criteria?
3. The answer to "Has the feature been fully implemented according to the spec and backlog?" can only be considered **YES** if there are not ANY caveats or conditions. **CRITICAL: If there are any caveats or conditions to the answer being YES, the answer is NO**.
    - If the answer is **NO** proceed to `Step 2 - Rectification`
    - If the answer is **YES** perform the completion actions:
        1. Update `.agents/features/{feature-short-name}/progress.md` to reflect that the feature is complete.
        2. Set the `status` field in the yaml frontmatter of `.agents/features/{feature-short-name}/spec.md` to `done`.
        3. Set the top-level `status` field in `.agents/features/{feature-short-name}/backlog.json` to `done`.
        4. Create a git commit with a meaningful message capturing these changes.
        5. Exit.

    These completion actions are owned by this skill so that direct invocations of `sdd-validate` leave the canonical status fields in a correct state regardless of caller.

## Step 2 - Rectification
1. Based on the outcome of your investigation, identify the gaps in the implementation and resolve them by making the necessary code changes to meet the acceptance criteria of each task. This may involve writing new code, adding more tests, modifying existing code, and ensuring that all changes are properly tested and integrated into the codebase.
2. Ensure that the project builds and that all tests pass. If the project fails to build or if any tests fail, fix the offending code until the project builds successfully and all tests pass.
3. Once all tasks are verified to be complete and meet their acceptance criteria, perform the completion actions:
    1. Update the `.agents/features/{feature-short-name}/progress.md` file with a summary of the validation process, including any issues found and how they were resolved.
    2. Set the `status` field in the yaml frontmatter of `.agents/features/{feature-short-name}/spec.md` to `done`.
    3. Set the top-level `status` field in `.agents/features/{feature-short-name}/backlog.json` to `done`.
    4. Create a git commit with a meaningful message summarizing the validation work that was done and the status updates.
