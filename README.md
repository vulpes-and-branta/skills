# Vulpes and Branta Skills

This marketplace ships two plugins: `development` (the spec → plan → build →
validate workflow) and `agents` (delegable subagents at three model tiers).

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
/plugin install development@vulpes-and-branta
/plugin install agents@vulpes-and-branta
```

## Plugins & skills

### `development`

Skills are designed to be used in order. Once installed, each is invoked as
`/development:<skill>`. Each takes an argument — most commonly the
`feature-short-name` that names the feature's directory under
`.agents/features/`.

| Skill | Invoke | Purpose |
| --- | --- | --- |
| [`spec`](./plugins/development/skills/spec) | `/development:spec <feature description>` | Collaboratively author a non-technical specification (PRD) for a feature. |
| [`plan`](./plugins/development/skills/plan) | `/development:plan <feature-short-name>` | Turn a spec into a structured backlog of build tasks. |
| [`build`](./plugins/development/skills/build) | `/development:build <feature-short-name>` | Drive a feature's backlog from todo/in-progress to done. |
| [`build-task`](./plugins/development/skills/build-task) | `/development:build-task <feature-short-name> <task-id>` | Build a single task from a `backlog.json`. |
| [`validate`](./plugins/development/skills/validate) | `/development:validate <feature-short-name>` | Verify the implementation matches the spec and acceptance criteria. |

The workflow reads and writes `{project_root}/.agents/features/<feature-short-name>/`,
which holds `spec.md`, `backlog.json`, and `progress.jsonl`. The skills create
these as needed — no separate setup step is required.

### `agents`

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
├── development/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── LICENSE.txt
│   └── skills/
│       ├── spec/                 # SKILL.md + references/
│       ├── plan/                 # SKILL.md + references/ + scripts/
│       ├── build/                # SKILL.md + scripts/
│       ├── build-task/           # SKILL.md + scripts/
│       └── validate/             # SKILL.md
└── agents/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── LICENSE.txt
    └── agents/
        ├── general-haiku.md
        ├── general-sonnet.md
        └── general-opus.md
tests/                            # exercise the skill scripts
```

## License

Apache License 2.0. A copy is included in each plugin directory so individual
plugins remain properly licensed when used or distributed on their own.
