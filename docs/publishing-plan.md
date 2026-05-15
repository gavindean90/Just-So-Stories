# Just-So Stories Publishing System

## Purpose

Transform the repository from a collection of loose story text files into a structured publishing pipeline capable of producing:

- Interactive web storybook reader
- Designed PDF editions
- EPUB editions
- Release artifacts attached to GitHub releases

The system should support ongoing story development while preserving stable published collections.

---

# Core Philosophy

The source of truth is NOT the PDF, EPUB, or website.

The source of truth is the structured story package.

All publication formats derive from the same canonical source structure.

---

# Target Outputs

## Primary Experience

Interactive web storybook reader.

Features planned:

- illustrated spreads
- responsive layout
- page navigation
- future read-aloud support
- future audio highlighting
- tablet-friendly reading experience

## Secondary Outputs

- designed PDF editions
- EPUB editions
- downloadable release ZIP bundles

---

# Technology Direction

## Web Reader

- React
- Vite
- TypeScript

## PDF Pipeline

- Typst

## EPUB Pipeline

- Pandoc

## Build/Validation

- Python

## Automation

- GitHub Actions
- tag/release-driven publishing

---

# Story Lifecycle

Stories move through editorial and production stages.

## Status Values

- draft
- text_review
- text_final
- paged
- prompted
- image_review
- image_approved
- release_ready

---

# Repository Structure

```text
stories/
collections/
assets/
templates/
scripts/
apps/
docs/
archive/
```

---

# Story Package Structure

```text
stories/{story-slug}/
  story.md
  metadata.yaml
  pages.yaml
  prompts.yaml
  images/
    candidates/
    approved/
  audio/
  editorial-notes.md
```

---

# Collections

Collections define what ships in a release.

Stories may exist in the repository without being part of a published collection.

Example:

```yaml
id: night-wanderers-volume-1
title: Just-So Stories: Night-Wanderers
version: 0.1.0
stories:
  - raccoon-thieving-thumbs
```

---

# Publishing Flow

```text
story package
    ↓
validation
    ↓
build manifest
    ↓
web/PDF/EPUB generation
    ↓
GitHub release artifacts
```

---

# Pilot Strategy

The Raccoon story is the pilot implementation.

The entire publishing pipeline should be proven against one complete story before scaling to the rest of the collection.

Pilot flow:

```text
Raccoon text final
→ spread planning
→ illustration prompts
→ image approval
→ web reader
→ PDF
→ EPUB
```

---

# Long-Term Goals

- multi-volume collections
- read-aloud narration
- synchronized text highlighting
- offline-capable web app
- print-ready editions
- improved illustration workflows
- reusable visual style system
