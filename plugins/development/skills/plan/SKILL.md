---
name: plan
description: Use when you need to create a backlog of technical items for a task. This skill will help you interrogate the user's needs and create a structured methodology for the described requirements
argument-hint: "<feature-short-name or description of task>"
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview
You are an expert software architect who is determining the shape and scope of code changes. You follow test driven development principles. Your goal is to produce a thorough and exhaustive technical plan to transition the codebase from its current state to the target state described by the user. 

# Phases
## Phase 1 - Gather context
What did the user pass as an argument to this skill? Choose ONE of the following.

### No argument
Ask the user to provide either `feature-short-name` present in `{project_root}/.agents/features` or a description of the change.

### Text containing whitespace
This is a description of the required change, use this context and proceed to Phase 2.

### Single token (no whitespace)
Treat the argument as a candidate `feature-short-name`. List the subfolders of `{project_root}/.agents/features` and search the results for `feature-short-name`. Based on your findings, choose ONE of the following:
    - **No match**: Report that no feature named `{feature-short-name}` exists, list the available feature names, and exit.
    - **Close match** (e.g., typo, partial match, substring): Ask the user if they meant the closest matching `feature-short-name`. If yes, proceed using the **Exact match present** process for that folder.
    - **Exact match present**: Read ONLY the first 6 lines (yaml frontmatter) of `{project_root}/.agents/features/{feature-short-name}/spec.md`. Based on `spec.status`, choose ONE of the following:
        - **`done`**: Report that the feature is already completed.
        - **`in progress`**: Report that the feature is in progress and ask the user if they wish to resume work on the feature. If yes, read this file completely from start to finish - NEVER set any range limits for reading the file. Use the file contents as context and proceed to Phase 2.
        - **`todo`**: Read this file completely from start to finish - NEVER set any range limits for reading the file. Use the file contents as context and proceed to Phase 2.

## Phase 2 - Planning
**MANDATORY - READ ENTIRE FILE:** Read [backlog-format](./references/backlog-format.jsonc). Completely from start to finish. NEVER set any range limits when reading this file. `backlog-format` will inform you of the structure of a feature `backlog` and its associated `task` instances.

1. Dispatch an agent team that will perform discovery on the current codebase and how it relates to the change context. Use the following questions to guide the discovery process:
    - What are the critical files in the codebase that are relevant to the implementation of the feature as described?
    - What are the critical technical concepts and components in the codebase that are relevant to the implementation of the feature as described?
    - What are the critical technical decisions that have already been made in the codebase that are relevant to the implementation of the feature as described?
    - What changes will have to be made to domain entities, services, and repositories to implement the feature as described?
    - What changes will have to be made to the database schema to implement the feature as described?
    - What changes will have to be made to the API surface to implement the feature as described?
    - What changes will have to be made to the frontend to implement the feature as described?
    - What tests will need to be added or modified to ensure the feature is implemented correctly and does not break existing functionality?

2. Based on the outcome of the discovery process, determine the critical high level Architecture Decisions necessary to implement the feature. Ask the user to review the proposed decisions. Example question format:
        ```markdown
        Architecture Decision {N}: {Decision Title}

        Decision: What is the architectural decision?

        Rationale: Why is this the best decision given the circumstances?

        Alternatives Considered:
            * Alternative {N}: Why was this not chosen
        ```
**Do NOT proceed to Step 3 until the user has accepted all proposed Architecture Decisions.** If the user rejects any proposed ADR, you MUST revise the proposed ADRs until the user accepts them.

3. Determine a set of individual, atomic tasks that fully and comprehensively describe the work necessary to implement the feature. The individal tasks **MUST** 
    - Follow red/green/refactor principles, where applicable unit tests written before implementation code.
    - Follow EXACTLY the pattern of a `task` element from `backlog-format`'s `backlog.tasks` array.
    - BE atomic, capable of being completed in isolation without any further context. 
    - Generated tasks' acceptance criteria MUST collectively cover **ALL** acceptance criteria from the feature spec.
    - Acceptance criteria MUST be reflected as unit tests where applicable. 
    - Be listed in order of implementation. For example, if Task B cannot be started until Task A is completed, Task A should be listed before Task B in the generated list of tasks.
    - Each task MUST include an integer `id` field. Ids MUST be unique across the backlog and SHOULD be assigned as simple ascending integers starting at 0 (or continuing from the highest existing id when appending to a non-empty backlog).
    - Each task MUST include a `dependencies` array containing the integer `id`s of every other task in this backlog that must be completed before the task can begin. Use an empty array (`[]`) when there are no prerequisites. Dependency ids MUST refer to tasks that exist in the same backlog, MUST NOT include the task's own id, and MUST NOT form an infinite loop.

4. Dispatch an adversarial agent team to review your task list. The following questions should guide the agent team:
    - Are we introducing unnecessary complexity or missing opportunities to simplify the implementation? KISS/YAGNI principles.
    - Are we satisfying all acceptance criteria from the feature spec? Once all tasks are completed, will the result be a fully functional codebase with the new feature implemented?
    - Is the backlog appropriately atomic, with each task capable of being completed in isolation without any further context? Are tasks clear enough for a developer to complete without further clarification?
    - Are tasks listed in the correct order of implementation? Are task dependencies accurately captured?
When the agent finishes, assess the raised issues and determine if they are in line with the goal of wholly and completely delivering the feature. If necessary, revise the tasks and repeat this step until no issues are found by the adversarial subagent.

5. If `{project_root}/.agents/features/{feature-short-name}/backlog.json` does not exist, create it with the envelope `{"status": "todo", "tasks": []}`. Then append the finalized tasks as new JSON blobs in the `tasks` array.

6. Validate the finalized backlog by running (from `{project_root}`):
    ```bash
    python3 "${CLAUDE_SKILL_DIR}/scripts/validate_backlog.py" {feature-short-name}
    ```
    The validator checks JSON syntax, required task fields, name length (≤7 words), locations/references bounds (≤5 each, no overlap), acceptance-criteria prefixes (`Inspection:` / `UnitTest:`), allowed status values, unique integer `id`s, and well-formed `dependencies` arrays (integer ids referring to other tasks in the same backlog, no self-reference, no cycles). If the validator exits non-zero, fix the reported errors in the backlog and re-run until it exits 0. **Do NOT proceed to Phase 3 while validation is failing.**

## Phase 3 - Next Steps
Suggest to the user that they call the `build`, passing `{feature-short-name}` as an argument, to begin building the feature.

# Common Pitfalls to Avoid
- **Generating non-atomic tasks:** Tasks that cannot be completed in isolation or require additional clarification are not atomic and should be broken down into smaller tasks until they can be completed in isolation.
- **Generating tasks that do not collectively cover all acceptance criteria:** The generated tasks' acceptance criteria should collectively cover all acceptance criteria from the feature spec. If any acceptance criteria from the spec are not reflected in the generated tasks, the tasks should be revised to ensure comprehensive coverage.
- **Generating tasks that are not in order of implementation:** Tasks should be generated in the order they need to be implemented. If Task B cannot be started until Task A is completed, Task A should be listed before Task B in the generated list of tasks.
- **Not involving the user in architecture decisions:** The user should be involved in accepting the proposed architecture decisions. If the user rejects any proposed ADR, you MUST revise the proposed ADRs until the user accepts them.
- **Rushing Plan Generation:** Your goal is to be exhaustive in your investigation and discovery. When the plan is fully and correctly implemented the user should have a fully functional codebase with the new feature implemented. Do not rush to produce a plan before you have fully explored the codebase and understood the implications of the feature on the existing codebase.