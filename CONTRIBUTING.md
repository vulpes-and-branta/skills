# Contributing

Thanks for your interest in improving the Vulpes & Branta skills marketplace.
This document covers how the repo is laid out, the conventions a skill needs to
follow, and how to get a change reviewed.

## What we accept

- **Bug fixes** in any of the bundled skills or their helper scripts.
- **Improvements** to existing `SKILL.md` instructions — clearer steps, better
  examples, tighter prompts.
- **Tests** for any script under `plugins/*/skills/*/scripts/`.

For larger changes (new skill, new plugin, reworking the workflow, breaking
changes to a script's CLI), please
[open an issue](https://github.com/vulpes-and-branta/skills/issues) to discuss
before sending a PR.

## Local setup

```sh
git clone https://github.com/vulpes-and-branta/skills.git
cd skills
python -m unittest discover -s tests
```

To try the skills inside Claude Code while iterating, install the marketplace
from your local checkout:

```
/plugin marketplace add /absolute/path/to/your/skills
/plugin install development@vulpes-and-branta
/plugin install agents@vulpes-and-branta
```

## Repository layout

```
.claude-plugin/marketplace.json   # marketplace manifest — register new plugins here
plugins/<plugin-name>/
  .claude-plugin/plugin.json      # required — plugin manifest
  LICENSE.txt                     # required — Apache 2.0 copy
  skills/<skill-name>/
    SKILL.md                      # required — frontmatter + instructions
    scripts/                      # optional — Python helpers invoked by the skill
    references/                   # optional — supporting docs the skill links to
  agents/                         # optional — subagent definitions (see `agents`)
tests/                            # unittest suite for scripts
```

## Skill conventions

Every skill directory must contain a **`SKILL.md`** with this frontmatter:

```markdown
---
name: <skill-name>
description: <one sentence — when should the model use this?>
argument-hint: "<what the user passes after the skill name>"
license: Apache-2.0. LICENSE.txt has complete terms
---
```

- `name` must match the containing directory name. The skill is invoked as
  `/<plugin-name>:<skill-name>`, so the plugin supplies the namespace — don't
  prefix the skill name itself.
- `description` is what Claude reads to decide whether to invoke the skill, so
  be specific about the trigger.
- `argument-hint` is shown to the user in the slash-command menu. Omit it only
  if the skill genuinely takes no argument.

Licensing is handled per plugin, not per skill: each `plugins/<plugin-name>/`
ships one `LICENSE.txt` covering all the skills inside it.

A new **plugin** additionally needs a `.claude-plugin/plugin.json` and an entry
in the `plugins` array of `.claude-plugin/marketplace.json` pointing at its
`source` directory. Individual skills are discovered from the plugin's `skills/`
directory and do not need to be registered anywhere.

## Scripts and tests

Helper scripts live under `plugins/<plugin-name>/skills/<skill-name>/scripts/`
and are invoked by the skill's instructions, not imported as a package. Tests
load them by absolute path via `tests/_loader.py`:

```python
from _loader import load
my_script = load("my_script")  # add the path to _loader.py's _SCRIPTS map
```

When you add a new script that warrants tests:

1. Add an entry to `_SCRIPTS` in `tests/_loader.py`.
2. Add a `test_<script>.py` file under `tests/` using `unittest`.
3. Confirm `python -m unittest discover -s tests` passes.

If you move or rename a skill, grep `tests/` for the old path — `_loader.py`
is not the only place a script path is hardcoded.

Keep scripts dependency-free where possible — they should run with a stock
Python 3 install.

## Pull requests

- One logical change per PR. Bundle related edits, but don't combine a bug fix
  with a refactor.
- Update `README.md` if you add a skill or change how an existing one is used.
- Update `marketplace.json`'s `version` if the change is user-visible.
- Make sure tests pass locally before pushing.

A short PR description that explains *why* the change matters is more useful
than a long one that restates the diff.

## Licensing

By contributing, you agree that your contributions are licensed under the
Apache License 2.0, the same license as the rest of the repo.

## Contact

Questions or proposals: hello@vulpesandbranta.com.
