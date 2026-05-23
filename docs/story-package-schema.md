# Story Package Schema (Issue #5)

This document defines the **canonical structure** for a story package used in this repository.

Design goals:
- **Human-readable first**: editors and collaborators should be able to inspect and update packages with standard Markdown/YAML tools.
- **Machine-friendly second**: fields and structure are explicit enough for future validation or automation.
- **Single story per package directory**: each story lives under its own slug.

---

## Canonical Directory Layout

All story packages should follow this structure:

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

### Concrete Example Tree

```text
stories/how-the-skunk-demanded-respect/
  story.md
  metadata.yaml
  pages.yaml
  prompts.yaml
  images/
    candidates/
      p01-v1.png
      p01-v2.png
      p02-v1.png
    approved/
      p01.png
      p02.png
  audio/
    narration-full.wav
    page-01.wav
    page-02.wav
    timings.yaml
  editorial-notes.md
```

---

## Required vs Optional Files

| Path | Required? | Purpose |
|---|---|---|
| `story.md` | Required | Canonical story text source used for editorial finalization and pagination. |
| `metadata.yaml` | Required | Story-level metadata (identity, status, credits, target audience, etc.). |
| `pages.yaml` | Required | Pagination map for reading/viewing experiences; page-by-page text and sequencing. |
| `prompts.yaml` | Required | Structured image-prompt plan aligned to pages/spreads. |
| `images/` | Required | Image asset container for candidate and approved art. |
| `images/candidates/` | Required | Working area for generated or drafted image options. |
| `images/approved/` | Required | Final approved image assets for publication builds. |
| `audio/` | Optional (recommended) | Narration assets and optional timing data for read-aloud experiences. |
| `editorial-notes.md` | Optional (recommended) | Human notes on revisions, decisions, unresolved questions, and QA findings. |

Notes:
- “Required” means it should exist for a package to be considered schema-complete.
- Optional items can be absent in early stages, but should be added before publication workflows.

---

## File and Folder Purpose

### `story.md`
- Holds the authoritative prose text for the story.
- Should be written for human editorial readability.
- Should avoid embedding presentation-specific layout details that belong in `pages.yaml`.

### `metadata.yaml`
- Holds package-level metadata fields used for tracking, credits, and lifecycle.
- Expected to be compact and stable over time.

### `pages.yaml`
- Defines how the story text is split across display units (pages and/or spreads).
- Serves reading UX, illustration alignment, and audio cue alignment.

### `prompts.yaml`
- Defines illustration prompt intent per page/spread (not final image binaries).
- Enables consistent art direction and reproducibility.

### `images/candidates/`
- Stores exploratory options (multiple versions, style experiments, variants).
- Assets in this folder are not publication-final.

### `images/approved/`
- Stores approved publication-bound images.
- Exactly which files are approved should be obvious by presence here.

### `audio/`
- Stores narration assets (full-track and/or page-level clips).
- May include timing map files used for text highlighting or page-turn cues.

### `editorial-notes.md`
- Stores collaborative human context that should not be forced into structured YAML.
- Suitable for revision logs, rationale, checklist items, and handoff notes.

---

## `metadata.yaml` Fields

The following fields are canonical unless explicitly marked optional.

```yaml
slug: how-the-skunk-demanded-respect
title: How the Skunk Demanded Respect
status: draft
version: 1
language: en
age_range:
  min: 6
  max: 9
reading_level: "Grades 1-3"
tags:
  - folktale
  - animal
  - confidence
authors:
  - name: "Kipling Adaptation Team"
illustrators: []
created_at: "2026-05-23"
updated_at: "2026-05-23"
source_text_file: story.md
license: "TBD"
summary: "A short synopsis used for cataloging and editorial review."
```

### Field definitions

| Field | Required? | Type | Description |
|---|---|---|---|
| `slug` | Required | string | Directory-safe unique story identifier; must match `{story-slug}` folder name. |
| `title` | Required | string | Human-facing story title. |
| `status` | Required | enum string | Lifecycle state (see [Story lifecycle statuses](#story-lifecycle-statuses)). |
| `version` | Required | integer | Incrementing package revision for editorial tracking. |
| `language` | Required | string | Primary language code (e.g., `en`). |
| `age_range.min` | Optional | integer | Suggested minimum reader/listener age. |
| `age_range.max` | Optional | integer | Suggested maximum reader/listener age. |
| `reading_level` | Optional | string | Reading complexity label. |
| `tags` | Optional | list[string] | Discovery and thematic labels. |
| `authors` | Optional | list[object] | Writing/adaptation credit entries. |
| `illustrators` | Optional | list[object or string] | Illustration credit entries. |
| `created_at` | Required | date string (`YYYY-MM-DD`) | Package creation date. |
| `updated_at` | Required | date string (`YYYY-MM-DD`) | Last substantive edit date. |
| `source_text_file` | Required | string | Usually `story.md`; allows explicit linkage. |
| `license` | Optional | string | Rights/license label for internal governance (use `TBD` until finalized). |
| `summary` | Optional | string | Brief synopsis for indexing and review contexts. |

---

## `pages.yaml` Purpose and Structure

`pages.yaml` is the canonical display-unit document. It maps story content into ordered display units (pages and/or spreads).

### Goals
- Keep display-unit sequencing explicit.
- Preserve stable display-unit IDs for image and audio references.
- Allow light presentational metadata without polluting `story.md`.

### Example

```yaml
page_set_version: 1
derived_from: story.md
display_units:
  - id: spread_001
    type: spread
    sequence: 1
    text_position: bottom_panel
    text: "Skunk wanted to be taken seriously by every animal in the valley."
    illustration_focus: "Skunk standing tall while larger animals laugh in the background."
    notes: "Opening tone: playful but sympathetic."
  - id: page_002
    type: page
    sequence: 2
    text_position: full_width_bottom
    text: "He made a plan that would leave a strong impression no one could ignore."
    illustration_focus: "Skunk sneaking away with a determined expression at dusk."
```

### Canonical keys

| Key | Required? | Type | Description |
|---|---|---|---|
| `page_set_version` | Required | integer | Revision of pagination structure. |
| `derived_from` | Required | string | Source text reference, typically `story.md`. |
| `display_units` | Required | list[object] | Ordered display-unit entries (page and/or spread). |
| `display_units[].id` | Required | string | Stable ID (e.g., `spread_001`, `page_002`) used by prompts/audio references. |
| `display_units[].type` | Required | enum string | `page` or `spread`. |
| `display_units[].sequence` | Required | integer | Human-facing sequence index in reading order. |
| `display_units[].text` | Required | string | Text shown/read for that display unit. |
| `display_units[].text_position` | Optional | string | Layout hint for text placement. |
| `display_units[].illustration_focus` | Optional | string | Art-direction intent for illustrators/prompt authors. |
| `display_units[].notes` | Optional | string | Editorial or layout comments specific to unit. |

In early drafts, this file may use “page” and “spread” loosely. Later layout rules should define the exact distinction. Stable IDs should work for either page-level or spread-level display units.

---

## `prompts.yaml` Purpose and Structure

`prompts.yaml` is the canonical prompt-planning document for visual generation or commissioned illustration guidance.

### Goals
- Keep art direction structured and reviewable.
- Tie prompts directly to display-unit IDs.
- Track candidate/approved image references without storing binary content in YAML.

### Example

```yaml
prompt_set_version: 1
style_guide:
  medium: "storybook illustration"
  palette: "warm earth tones with twilight blues"
  character_consistency_notes: "Skunk has white stripe from forehead to tail"
prompts:
  - display_unit_id: spread_001
    status: draft
    prompt: "A confident skunk in a forest clearing, storybook style, expressive faces, soft lighting"
    negative_prompt: "photorealistic, horror, text watermark"
    candidates:
      - images/candidates/p01-v1.png
      - images/candidates/p01-v2.png
    approved: images/approved/p01.png
    approval_notes: "Chosen for clear silhouette and correct character expression."
  - display_unit_id: page_002
    status: ready_to_generate
    prompt: "Skunk moving quietly at dusk, determined expression, painterly children's book style"
    candidates:
      - images/candidates/p02-v1.png
    approved: images/approved/p02.png
```

### Canonical keys

| Key | Required? | Type | Description |
|---|---|---|---|
| `prompt_set_version` | Required | integer | Revision of prompt-planning structure. |
| `style_guide` | Optional | object | Shared art-direction defaults across pages. |
| `prompts` | Required | list[object] | Page-level prompt definitions. |
| `prompts[].display_unit_id` | Required | string | Must match `display_units[].id`. |
| `prompts[].status` | Required | enum string | `draft`, `ready_to_generate`, `generated`, `needs_revision`, or `approved`. |
| `prompts[].prompt` | Required | string | Primary generation/brief prompt text. |
| `prompts[].negative_prompt` | Optional | string | Exclusions and quality constraints. |
| `prompts[].candidates` | Optional | list[string] | Relative paths to candidate images. |
| `prompts[].approved` | Optional | string | Relative path to approved final image. |
| `prompts[].approval_notes` | Optional | string | Human rationale for why an approved image was selected. |

---

## Image Approval Workflow

Recommended workflow:

1. **Generate or collect candidates** into `images/candidates/`.
2. **Review candidates** against page intent (`pages.yaml`) and style direction (`prompts.yaml`).
3. **Select approved image(s)** and place final versions in `images/approved/`.
4. **Record approved path(s)** in `prompts.yaml` under each corresponding `display_unit_id`.
5. **Proof visually** for sequence coherence and character consistency before marking story `illustrated`.

Conventions:
- Candidate naming can include iterations (`p03-v1.png`, `p03-v2.png`).
- Approved naming should be stable and page-linked (`p03.png`).
- Approval is represented by both file placement in `approved/` and path reference in `prompts.yaml`.

---

## Audio Timing Support Goals

The `audio/` directory supports future read-aloud and accessibility workflows.

Recommended goals:
- Support a **full narration track** (e.g., `narration-full.wav` or `.mp3`).
- Support **display-unit-level clips** aligned to `display_units[].id` (e.g., `spread_001.wav`, `page_002.wav`).
- Support optional **timing maps** (e.g., `timings.yaml`) that can enable:
  - word/sentence highlighting,
  - page-turn cueing,
  - synchronization QA.

Suggested timing map shape (optional):

```yaml
version: 1
units: seconds
display_unit_timings:
  - display_unit_id: spread_001
    start: 0.0
    end: 8.4
  - display_unit_id: page_002
    start: 8.4
    end: 15.1
```

This is a support goal, not a parser contract in this issue.

---

## Story Lifecycle Statuses

Canonical status progression:

1. `draft` — Initial text and concept development in progress.
2. `text_final` — Story prose editorially approved.
3. `paged` — `pages.yaml` complete and reviewed.
4. `prompts_ready` — `prompts.yaml` complete and ready for image production.
5. `illustrated` — Approved images exist for required pages.
6. `proofed` — End-to-end QA complete (text, images, sequencing, metadata, optional audio checks).
7. `published` — Package released to target channel.

Usage notes:
- `metadata.yaml.status` should reflect the current state.
- Teams may add internal sub-status notes in `editorial-notes.md`, but should keep `status` within canonical values.

---

## Non-Goals for Issue #5

This schema document intentionally does **not**:
- define parser implementations,
- prescribe build tooling,
- embed story prose examples as canonical content,
- alter existing story files.

It only defines the documentation contract for a human-readable, machine-friendly story package.
