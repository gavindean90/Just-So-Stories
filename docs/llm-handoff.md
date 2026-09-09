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

# Current Architecture Anchors

Start here:

```text
docs/publishing-plan.md
collections/just-so-stories-volume-1.json
README.md
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

# Current Publishing Strategy

The six root-level `.txt` files are canonical for prose. The text-first web, EPUB and tagged PDF pipeline publishes all six in the order declared by the collection manifest. Do not migrate or copy that prose into story packages. Add the richer package and asset layers only when artwork, illustration-specific pagination, or narration work begins.

---

# Historical Planning Issues

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

Run `make check` before publication changes. Future illustration or narration work should extend story entries in the collection manifest with asset references while leaving the root-level canonical prose in place.

---

# Rules for Future Assistants

- Do not rely on chat memory if the repo contains a relevant doc.
- Do not make large speculative rewrites.
- Prefer small commits that satisfy one issue at a time.
- Keep generated artifacts out of Git unless explicitly intended.
- Use issues as the coordination layer.
- Use docs as the architectural layer.
- Use the root-level `.txt` files as the publishing source of truth for prose.
