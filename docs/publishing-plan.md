# Just-So Stories Publishing System

## Purpose

Publish the six-story collection from its approved canonical text files through a small, maintainable pipeline capable of producing:

- Responsive static web reader
- EPUB editions
- Release artifacts attached to GitHub releases

Designed PDFs, illustration and interactive read-aloud features remain possible future additions.

The system should support ongoing story development while preserving stable published collections.

---

# Core Philosophy

The source of truth is NOT the EPUB or website.

The source of truth for prose is the six root-level `.txt` files. Collection identity and order come from `collections/just-so-stories-volume-1.json`.

All publication formats derive directly from those sources. Generated formats and future asset metadata must not duplicate the story bodies.

---

# Target Outputs

## Primary Experience

Responsive, text-first static web reader.

Current features:

- responsive layout
- table of contents and chapter navigation
- reader-controlled text size and light/dark theme
- local story bookmark
- accessible, semantic HTML

## Secondary Outputs

- designed PDF editions
- illustrations and read-aloud narration
- downloadable release bundles beyond EPUB

---

# Technology Direction

## Web Reader

- generated static HTML
- plain CSS and small progressive-enhancement JavaScript

## EPUB Pipeline

- Pandoc 3.1.3

## Build/Validation

- dependency-free Python 3.12

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

# Future Story Package Structure

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
root `.txt` files + collection manifest
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

# First Release Strategy

The text-first pipeline publishes all six provisionally text-final stories in the approved order. Rich story packages, pagination, artwork, narration and PDF layout are deferred until an actual asset workflow requires them.

---

# Long-Term Goals

- multi-volume collections
- read-aloud narration
- synchronized text highlighting
- offline-capable web app
- print-ready editions
- improved illustration workflows
- reusable visual style system
