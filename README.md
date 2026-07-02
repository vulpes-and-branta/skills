# Vulpes and Branta Skills

This marketplace ships three plugins: `initialize` (set up the workspace),
`spec-driven-development` (the spec → plan → build → validate workflow), and
`general-purpose-agents` (delegable subagents at three model tiers).

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
/plugin install general-purpose-agents@skills
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

### `general-purpose-agents`

Three general-purpose subagents that share the same prompt but run on different
models. Delegate to the tier that matches the task's difficulty and your
cost/latency budget.

| Agent | Model | Use when |
| --- | --- | --- |
| `general-haiku` | Haiku | Simple, well-scoped, high-volume work: lookups, pattern searches, classification, routing, straightforward edits. Latency/cost matters most. |
| `general-sonnet` | Sonnet | The sensible default: feature implementation, bug fixes, standard refactors, multi-file research, code review. |
| `general-opus` | Opus | The hardest work: complex multi-step investigations, large-codebase analysis, architecture decisions, debugging unfamiliar systems. Quality matters most. |

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
├── spec-driven-development/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   └── skills/                    # each ships its own LICENSE
│       ├── sdd-spec/
│       ├── sdd-plan/
│       ├── sdd-build/
│       ├── sdd-build-task/
│       └── sdd-validate/
└── general-purpose-agents/
    ├── .claude-plugin/
    │   └── plugin.json
    └── agents/                    # general-haiku, general-sonnet, general-opus
        ├── general-haiku.md
        ├── general-sonnet.md
        └── general-opus.md
tests/                            # exercise the skill scripts
```

## License

Apache License 2.0. A copy is included in each skill directory so individual
skills remain properly licensed when used or distributed on their own.
