# Vulpes and Branta Skills

This marketplace ships two plugins for spec-driven feature development:
`initialize` (set up the workspace) and `spec-driven-development` (the spec →
plan → build → validate workflow).

## Install

In Claude Code, add the marketplace:

**Via SSH Auth**
```
/plugin marketplace add git@github.com:vulpes-and-branta/skills.git
```

**Via HTTPS Auth**
```
/plugin marketplace add https://github.com/vulpes-and-branta/skills.git
```

Then install the plugins:
```
/plugin install initialize@skills
/plugin install spec-driven-development@skills
```

## Plugins & skills

Skills are designed to be used in order. Once installed, each is invoked as
`/<plugin>:<skill>`.

### `initialize`

| Skill | Invoke | Purpose |
| --- | --- | --- |
| [`vnb-init`](./plugins/initialize/skills/vnb-init) | `/initialize:vnb-init` | Initialize the `.agents/features/` directory structure used by the rest of the workflow. |

### `spec-driven-development`

| Skill | Invoke | Purpose |
| --- | --- | --- |
| [`sdd-spec`](./plugins/spec-driven-development/skills/sdd-spec) | `/spec-driven-development:sdd-spec` | Collaboratively author a non-technical specification for a feature. |
| [`sdd-plan`](./plugins/spec-driven-development/skills/sdd-plan) | `/spec-driven-development:sdd-plan` | Turn a spec into a structured backlog of build tasks. |
| [`sdd-build`](./plugins/spec-driven-development/skills/sdd-build) | `/spec-driven-development:sdd-build` | Drive a feature's backlog from in-progress to done. |
| [`sdd-build-task`](./plugins/spec-driven-development/skills/sdd-build-task) | `/spec-driven-development:sdd-build-task` | Build a single task from a `backlog.json`. |
| [`sdd-validate`](./plugins/spec-driven-development/skills/sdd-validate) | `/spec-driven-development:sdd-validate` | Verify the implementation matches the spec and acceptance criteria. |

## Repository layout

```
.claude-plugin/
└── marketplace.json              # marketplace manifest (lists the plugins)
plugins/
├── initialize/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   └── skills/
│       └── vnb-init/
└── spec-driven-development/
    ├── .claude-plugin/
    │   └── plugin.json
    └── skills/                    # each ships its own LICENSE
        ├── sdd-spec/
        ├── sdd-plan/
        ├── sdd-build/
        ├── sdd-build-task/
        └── sdd-validate/
tests/                            # exercise the skill scripts
```

## License

Apache License 2.0. A copy is included in each skill directory so individual
skills remain properly licensed when used or distributed on their own.
