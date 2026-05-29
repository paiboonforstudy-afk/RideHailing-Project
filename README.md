The Effective Workflow
1. Read the Source of Truth (SoT) First

Always require the AI to read the specifications, existing code, design patterns, naming conventions, and architecture before doing anything else. Never allow it to start generating code immediately.

2. Enforce a "Reuse-First" Policy

Include explicit rules in your prompts (e.g., "Do not create new abstractions, classes, or helpers if existing ones can be reused"). Require the AI to explicitly cite the existing files or functions it plans to utilize before writing any new code.

3. Break Tasks into Short Iterations

Guide the AI to work layer by layer: Inspect → Propose Change → Implement → Test. Do not prompt it to build an entire feature in a single, massive command.

4. Establish a Clear Definition of Done (DoD)

Ensure strict criteria are met before completion: tests must pass, no new patterns are introduced without justification, the existing codebase style is preserved, and no unnecessary dependencies are added.

5. Review AI Output via "Policy Reviews"

Shift away from strictly line-by-line reviews. Prioritize evaluating three core policies first:

Did it reuse existing code?

Did it preserve existing design patterns?

Did it avoid adding unnecessary complexity?

Orchestrator Agent Pipeline
(The framework currently used to develop the "brain" of the team's Orchestrator)

Read SoT → Lock Scope → Inspect Codebase First → Break Work into Short Iterations → Implement (Reuse-First) → Test/QA Gate → Handoff