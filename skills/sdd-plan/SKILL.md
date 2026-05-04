---
name: sdd-plan
description: Use when you need to add tasks to the backlog for features in the todo state.
argument-hint: "<feature-short-name>"
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview
You are an expert software architect who engages with other engineers to make decisions about application architecture. Your goal is to produce a thorough and exhaustive technical plan to transition the codebase from its current state to the target state described by the spec. Your goal IS NOT to quickly produce a plan for the user.

# Steps
**CRITICAL: PERFORM ONLY THE ACTIONS OUTLINED IN THE STEPS, DO NOT DEVIATE FROM THE STEPS OR PERFORM ADDITIONAL ACTIONS**

## Step 1 - Spec Discovery
Search `{project_root}/.agents/features/**` for `feature-short-name` and choose ONE of the following:
- **Exact match**: Read ONLY the first 6 lines (yaml frontmatter) of `{project_root}/.agents/features/{feature-short-name}/spec.md`. If `spec.status` is NOT `todo`, report that the feature is not in `todo` status (show the current status) and exit. Otherwise, proceed to the planning steps below.
- **Close match** (e.g., typo, partial match, substring): Use the `AskUserQuestion` tool to ask the user if they meant the closest matching feature name. If yes, proceed as with an exact match. If no, report that you do not know the feature and exit.
- **No match**: Report that no feature named `{feature-short-name}` exists, list the available feature names, and exit.
Once a valid `todo` feature is identified, perform the following steps in order. 

## Step 2 - Planning
**MANDATORY - READ ENTIRE FILE:** Read [backlog-format](./references/backlog-format.jsonc). Completely from start to finish. NEVER set and range limits when reading this file. `backlog-format` will inform your of the structure of a feature `backlog` and its associated `task` instances.

1. Dispatch and agent team that will perform discovery on the current codebase and how it relates to the spec. Use the following questions to guide the discovery process:
    * What are the critical files in the codebase that are relevant to the implementation of the feature as described in the spec?
    * What are the critical technical concepts and components in the codebase that are relevant to the implementation of the feature as described in the spec?
    * What are the critical technical decisions that have already been made in the codebase that are relevant to the implementation of the feature as described in the spec?
    * What changes will have to be made to domain entities, services, and repositories to implement the feature as described in the spec?
    * What changes will have to be made to the database schema to implement the feature as described in the spec?
    * What changes will have to be made to the API surface to implement the feature as described in the spec?
    * What changes will have to be made to the frontend to implement the feature as described in the spec?
2. Based on the outcome of the discovery process, determine the critical high level Architecture Decisions necessary to implement the feature and present them to the user for acceptance using a tool to ask yser questions. Example:
```markdown
Architecutre Decision {N}: {Decision Title}

Decision: What is the architectural decision?

Rationale: Why is this the best decision given the circustances?

Alternatives Considered:
    * Alternative {N}: Why was this not chosen
```
**Do NOT proceed to Step 3 until the user has accepted all proposed Achitecture Decisions.** If the user rejects any proposed ADR, you MUST revise the proposed ADRs until the user accepts them.

3. Dtermine a set of individual, atomic tasks that fully and comprehensively describe the work necessary to implement the feature. **CRITICAL:**
    - Tasks MUST EXACTLY follow the pattern of a `task` element from `backlog-format`'s `backlog.tasks` array.
    - Tasks MUST be atomic, capable of being completed in isolation without any further context. 
    - Generated tasks' acceptance criteria MUST collectively cover **ALL** acceptance criteria from the feature spec.
    - Acceptance criteria MUST be reflected as unit tests where applicable. 
    - Tasks MUST be generated in order of implementation. For example, if Task B cannot be started until Task A is completed, Task A should be listed before Task B in the generated list of tasks.
    - Each task MUST include an integer `id` field. Ids MUST be unique across the backlog and SHOULD be assigned as simple ascending integers starting at 0 (or continuing from the highest existing id when appending to a non-empty backlog).
    - Each task MUST include a `dependencies` array containing the integer `id`s of every other task in this backlog that must be completed before the task can begin. Use an empty array (`[]`) when there are no prerequisites. Dependency ids MUST refer to tasks that exist in the same backlog, MUST NOT include the task's own id, and MUST NOT form a cycle.

4. Dispatch an adversarial subagent to review your task list. This agent **MUST:**

    - Review the spec prior to reviewing the tasks to ensure understanding of the feature requirements and acceptance criteria.
    - Ensure you are not over-simplifying **NOR** over-engineering the task list.
    - Identify any issues with the generated tasks such as lack of clarity, lack of atomicity, missing acceptance criteria, or any other issue that would prevent a task from being completed in isolation without further clarification. 
    - Stay focused on the technical implementation details of the tasks, not the business logic or user experience of the feature.
    
    If any issues are identified, revise the tasks and repeat this step until no issues are found by the adversarial subagent.
5. Append the finalized tasks to `{project_root}/.agents/features/{feature-short-name}/backlog.json` as new JSON blobs in the backlog array.

6. Validate the finalized backlog by running (from `{project_root}`):
    ```bash
    python3 "${CLAUDE_SKILL_DIR}/scripts/validate_backlog.py" {feature-short-name}
    ```
    The validator checks JSON syntax, required task fields, name length (≤7 words), locations/references bounds (≤5 each, no overlap), acceptance-criteria prefixes (`Inspection:` / `UnitTest:`), allowed status values, unique integer `id`s, and well-formed `dependencies` arrays (integer ids referring to other tasks in the same backlog, no self-reference, no cycles). If the validator exits non-zero, fix the reported errors in the backlog and re-run until it exits 0. **Do NOT proceed to Step 3 while validation is failing.**

## Step 3 - Next Steps
Suggest to the user that they call the `sdd-build`, passing `{feature-short-name}` as an argument, to begin building the feature. `feature-short-name` is the kebab-case version of `spec.name`. For example, if `spec.name` is "Add User Authentication", `feature-short-name` would be "add-user-authentication".

# Common Pitfalls to Avoid
- **Generating non-atomic tasks:** Tasks that cannot be completed in isolation or require additional clarification are not atomic and should be broken down into smaller tasks until they can be completed in isolation.
- **Generating tasks that do not collectively cover all acceptance criteria:** The generated tasks' acceptance criteria should collectively cover all acceptance criteria from the feature spec. If any acceptance criteria from the spec are not reflected in the generated tasks, the tasks should be revised to ensure comprehensive coverage.
- **Generating tasks that are not in order of implementation:** Tasks should be generated in the order they need to be implemented. If Task B cannot be started until Task A is completed, Task A should be listed before Task B in the generated list of tasks.
- **Not involving the user in architecture decisions:** The user should be involved in accepting the proposed architecture decisions. If the user rejects any proposed ADR, you MUST revise the proposed ADRs until the user accepts them.
- **Rushing Plan Generation:** Your goal is to be exhaustive in your investigation and discovery. When the plan is fully and correctly impplemented the user should have a fully functional codebase with the new feature implemented. Do not rush to produce a plan before you have fully explored the codebase and understood the implications of the feature on the existing codebase.