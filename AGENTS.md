# SQL AI Agent tutorial workflow

This project uses two repositories:

- `sql-ai-agent` contains reader-facing supporting code and notebooks.
- `sql-ai-agent-tutorials` contains private planning documents and tutorial
  drafts.

Build and execute supporting code before drafting the related tutorial. Use
Jupyter notebooks by default unless Rami requests another format.

## Agent use by stage

### Initial draft creation

- The primary Codex agent may use specialized agents when they materially help
  bring the initial tutorial draft close to publication readiness.

### Editing

- Use only the primary Codex agent for routine tutorial edits.
- Do not invoke Book Builder during drafting or editing.
- Do not automatically run fact, code, continuity, or full-review agents after
  incremental edits.

### Author-requested checkpoints

- Use a style-review agent only when Rami explicitly requests review of a
  completed paragraph, section, or similar checkpoint.
- A checkpoint review does not trigger Book Builder or the full review process.

### Completed-draft review

- Start the completed-draft review only when Rami explicitly says the tutorial
  is complete or ready for review and requests the review.
- At that point, Book Builder may be invoked to coordinate full style and code
  reviews.
- Add fact or continuity review only when Rami explicitly requests it or when a
  concrete issue discovered during the completed-draft review makes that lens
  necessary. Explain the need before adding it.
- After fixes, rerun only the review lens affected by the changes.

Never infer that an ordinary editing request means the draft is ready for the
completed-draft review.

## Tutorial conventions

- Refer to the reader-facing repository as the "tutorial supporting
  repository," not the "public repository," in tutorial prose.
- Use `I` and `my` for the author's recommendations, preferences, decisions,
  and genuine personal experiences.
- Use inclusive `we` and `our` for guided actions that the author explains and
  expects readers to follow with them.
- Avoid `you` and `your` in normal tutorial prose unless direct address is
  specifically useful.
- Never invent a personal experience.
- Do not add a license file, license section, or license notice unless Rami
  explicitly requests one.
