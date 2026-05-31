---
name: sdd-spec
description: Collaboratively create specification documents. Use when the user needs to document non-technical feature requirements, create specification documents, or define business logic for new functionality.
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview 
You will work with the user to create a comprehensive specification document for a new feature. Your goal is to perform a thorough and exhaustive investigation of the user's feature request, fully discovering their intent and possible edge-cases. Your goal IS NOT to quickly produce a documnet based on their input.

**MANDATORY - READ ENTIRE FILE:** Read the [spec-format](./references/spec-format.md) document completely from start to finish. NEVER set any range limits when reading this file. `spec-format` will give inform you of the type of information you will be expected to gather and provide the exact format of the resulting document.

# Steps
**CRITICAL: PERFORM ONLY THE ACTIONS OUTLINED IN THE STEPS, DO NOT DEVIATE FROM THE STEPS OR PERFORM ADDITIONAL ACTIONS**

## Step 1 - Discovery:
1. Gather detailed information about the feature from the user. Using a tool to ask questions, interact with the user to ensure you have a complete understanding of the feature's requirements, business logic, and intended user experience.

2. Use subagents and tools to explore the codebase and gather context relevant to the user's feature description. The following questions should guide the investigation:

   - What existing workflows and business logic will be affected by this request?
   - What possible edge cases exist and have not been addressed?
   - How might the experience of the end user be affected by these changes?
   - If there is a frontend for this project, how does the request affect it? What UX will need to change based on the request?

   Your investigation should be exhaustive and iterative exercise in determining the current state of the codebase as it relates to the user's request.

3. Based on the outcome of your investigation, identify any gaps in your understanding of the feature. Using a tool to ask questions, interact with the user to clarify any incomplete requirements and determine edge case behavior. For each piece of missing information, you should:

   - Explain why additional information is relevant to ensure comprehensive coverage
   - Iterate until all aspects of the feature are understood

4. When you believe you have enough information to document the feature, dispatch an adversarial subagent to double-check your work. The subagent should:
   - Question your assumptions about the feature to identify gaps in your understanding
   - Challenge you to consider edge cases and scenarios you may not have thought of
   - Provide critical feedback on the completeness and clarity of your understanding of the feature
   - Stay focused on the business logic and user experience of the feature, not technical implementation details

5. Based on the outcome of the subagent's analysis, choose ONE of the following:
   - Gaps Identified: Repeat `Discovery` to gather more information and clarify your understanding of the feature.
   - No Gaps Identified: Display the full set of acceptance criteria as a bulleted list, then **EXPLICITLY** ask the user for approval to move on to `Spec Generation`. Do not proceed without confirmation.

# Step 2 - Spec Generation:

Produce a specification file that accurately represents all information gathered during Step 1 in `{project_root}/.agents/features/{feature-short-name}/spec.md`. **CRITICAL:** {feature-name} MUST match `spec.name` in the YAML frontmatter of the generated `spec.md` file. The specification file **MUST**:
   - Be written in clear, concise English
   - Provide sufficient detail for implementation teams to understand business intent
   - Follow the `spec-format` EXACTLY

# Step 3 - Next Steps
Suggest to the user that they call the `sdd-plan`, passing `{feature-short-name}` as an argument, to create a technical plan for implementing the feature. `feature-short-name` is the kebab-case version of `spec.name`. For example, if `spec.name` is "Add User Authentication", `feature-short-name` would be "add-user-authentication".

# Common Pitfalls to Avoid
- **Vague acceptance criteria:** Each scenario should be specific and ideally programmatically testable
- **Missing edge cases:** The spec does not consider how the feature should behave in less common but plausible situations
- **Assuming knowledge:** Explicitly document all requirements even if they seem obvious 
- **Starting documentation too early:** Ensure you have complete information before asking to move to spec generation
- **Overwriting or appending to existing spec files:** Always create new spec files for new features. Do not modify existing spec files.