---
name: vnb-init
description: Use to initialize the directory structure for use of sdd-* skills.
license: Apache-2.0. LICENSE.txt has complete terms
---
# Overview
You will initialize the directory structure for use of sdd-* skills. This should be used as the first step before using any other sdd-* skill to ensure that the necessary directory structure is in place for the other skills to function properly.

# Steps
1. Create the following directory structure in the project root if it does not already exist:
```
.project-root/
  .agents/
    features/
      .gitkeep
    .gitkeep
```

Commit the basic folder and .gitkeep files with the message "Init .agents/ directory structure for VB skills". Then create or update the project .gitignore file to include the following lines:
```
# Ignore produced artifacts from VB agent teams
.agents/
``` 