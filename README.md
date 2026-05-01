# skills

A Claude Code plugin marketplace for the Vulpes & Branta agent-skills workflow:
spec out a feature, plan a backlog, build the tasks, and validate against the
spec — each step as its own skill.

## Install

In Claude Code:

```
/plugin marketplace add vulpesandbranta/skills
/plugin install vulpes-and-branta@skills
```

(Replace `vulpesandbranta/skills` with the actual git remote once published.)

## Skills

The `vulpes-and-branta` plugin bundles six skills, designed to be used in order. Once installed, each skill is invoked as `/vulpes-and-branta:<skill>`.

| Skill | Purpose |
| --- | --- |
| [`vnb-init`](./skills/vnb-init) | Initialize the `.agents/features/` directory structure used by the rest of the workflow. |
| [`sdd-spec`](./skills/sdd-spec) | Collaboratively author a non-technical specification for a feature. |
| [`sdd-plan`](./skills/sdd-plan) | Turn a spec into a structured backlog of build tasks. |
| [`sdd-build`](./skills/sdd-build) | Drive a feature's backlog from in-progress to done. |
| [`sdd-build-task`](./skills/sdd-build-task) | Build a single task from a `backlog.json`. |
| [`sdd-validate`](./skills/sdd-validate) | Verify the implementation matches the spec and acceptance criteria. |

## Repository layout

```
plugins/
├── .claude-plugin/
│   └── marketplace.json     # plugin marketplace manifest
├── skills/                  # the six bundled skills (each ships its own LICENSE)
│   ├── vnb-init/
│   ├── sdd-spec/
│   ├── sdd-plan/
│   ├── sdd-build/
│   ├── sdd-build-task/
│   └── sdd-validate/
├── LICENSE.txt              # Apache License 2.0
└── README.md
```

## License

Apache License 2.0 — see [`LICENSE.txt`](./LICENSE.txt). A copy is included in
each skill directory so individual skills remain properly licensed when used or
distributed on their own.
