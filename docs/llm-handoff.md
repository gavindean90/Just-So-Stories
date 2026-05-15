# LLM Handoff Guide

This repository uses GitHub issues and documentation as durable working memory for LLM-assisted development.

The goal is not board polish. The goal is coherent execution across chats, agents, and time.

---

# Operating Model

Use the repository as the source of truth.

Chat conversations are temporary. Durable decisions belong in:

- `docs/`
- GitHub issues
- story package files
- pull request descriptions
- issue comments

---

# Current Architecture Anchor

Start here:

```text
docs/publishing-plan.md
```

That file explains the publishing-system direction, including:

- target outputs
- technology choices
- story lifecycle
- repo structure
- collection system
- pilot strategy

---

# Issue Usage

Issues are execution handles for LLM assistants.

Each issue should be treated as a small, durable unit of work that another assistant can pick up without needing the original chat.

When working an issue:

1. Read the relevant docs first.
2. Inspect current repo files before changing anything.
3. Make the smallest coherent change that advances the issue.
4. Comment on the issue if decisions are made.
5. Close the issue only when the repo itself satisfies the done condition.

---

# Current Pilot Strategy

The Raccoon story is the pilot.

Do not migrate every story at once.

Prove the complete pipeline with one story first:

```text
Raccoon package
→ text final
→ spread plan
→ prompts
→ approved images
→ web reader
→ PDF
→ EPUB
```

After the Raccoon pilot works, expand the same structure to the rest of Volume 1.

---

# Important Open Issues

- #1 Foundation epic
- #2 Repo skeleton
- #3 Generated-file gitignore rules
- #5 Story package schema
- #6 Collection schema
- #7 Raccoon story package
- #8 Volume 1 collection config
- #9 Text-final checklist
- #10 Finalize Raccoon text
- #11 Spread planning rules
- #12 Raccoon spread plan
- #13 Visual style bible
- #14 Image asset specs
- #15 Illustration prompt schema
- #16 Draft Raccoon prompts

Issue #4 is complete because `docs/publishing-plan.md` exists.

---

# Recommended Next Work

The next durable architecture files should be:

```text
docs/story-package-schema.md
docs/collection-schema.md
docs/visual-style-bible.md
```

After those exist, create the repo skeleton and convert the Raccoon story into its package.

---

# Rules for Future Assistants

- Do not rely on chat memory if the repo contains a relevant doc.
- Do not make large speculative rewrites.
- Prefer small commits that satisfy one issue at a time.
- Keep generated artifacts out of Git unless explicitly intended.
- Use issues as the coordination layer.
- Use docs as the architectural layer.
- Use story packages as the publishing source of truth.
