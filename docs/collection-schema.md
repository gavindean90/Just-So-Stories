# Collection Schema (Issue #6)

> **First-release implementation:** The text-first publishing pipeline uses
> `collections/just-so-stories-volume-1.json`. Its ordered story objects map
> titles and stable IDs directly to the canonical root-level `.txt` files.
> The YAML/story-package contract below remains an aspirational schema for a
> future illustrated production layer; it does not supersede or duplicate the
> approved prose sources.

This document defines the **collection configuration contract** for grouping multiple story packages into a buildable release unit.

Collection files live at:

```text
collections/{collection-id}.yaml
```

A collection references existing story packages (by story slug) and provides release-level metadata used for future web/PDF/EPUB build targets.

---

## 1) Purpose of a Collection

A collection is a curated set of stories that should ship together as one release concept (for example, a themed volume).

It exists to:
- define release identity (title, version, author/editor attribution),
- define which stories are included and in what order,
- define readiness state and release intent,
- provide build-target hints for downstream publishing workflows.

A collection is **not** a replacement for `stories/{story-slug}/` package metadata. Story packages remain canonical for story-level content and lifecycle details, while collection files govern cross-story assembly.

---

## 2) Required vs Optional Fields

### Required fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique collection ID; should match `{collection-id}` in `collections/{collection-id}.yaml`. |
| `title` | string | Human-facing collection title. |
| `version` | string (semver) | Collection release version (e.g., `0.1.0`, `1.0.0`). |
| `author` | string | Primary release attribution for the collection. |
| `stories` | list[string] | Ordered list of story slugs included in this collection. |

### Optional fields (suggested)

| Field | Type | Description |
|---|---|---|
| `subtitle` | string | Secondary title/tagline. |
| `language` | string | Primary language code for the collection (e.g., `en`). |
| `status` | enum string | Collection lifecycle state. |
| `release_mode` | enum string | Release intent (`draft`, `preview`, `release`). |
| `formats` | list[string] | Intended output formats, such as `web`, `pdf`, `epub`. |
| `description` | string | Brief synopsis of collection theme and scope. |
| `created_at` | date string (`YYYY-MM-DD`) | Initial collection creation date. |
| `updated_at` | date string (`YYYY-MM-DD`) | Last substantive metadata/content edit date. |

---

## 3) Story Ordering Rules

`stories:` is an ordered list. The array order is canonical reading/order-of-appearance order for collection builds.

Rules:
1. Each entry in `stories` must be a story slug string.
2. Each slug should map to an existing story package directory at `stories/{story-slug}/`.
3. Slugs should be unique within a collection file (no duplicates).
4. Reordering stories is a meaningful collection change and should be captured by `version` updates.
5. Collections may include a subset of available story packages.

Example ordering:

```yaml
stories:
  - raccoon-thieving-thumbs
  - opossum-cheated-the-hound
  - skunk-demanded-respect
```

In this example, the raccoon story appears before the opossum story in generated table of contents and reading progression.

---

## 4) Versioning Rules

Use semantic versioning (`MAJOR.MINOR.PATCH`) in `version`.

Recommended interpretation:
- **MAJOR**: breaking collection changes (identity/structure shifts, major lineup restructuring).
- **MINOR**: additive or substantial non-breaking updates (new stories added, major metadata expansion).
- **PATCH**: editorial fixes/metadata corrections that do not materially change collection scope.

Practical guidance:
- Start early planning releases at `0.x.y`.
- Increment version when story order or story inclusion changes.
- Keep version changes intentional and traceable in commit history.

---

## 5) Release Mode Rules

`release_mode` communicates publishing intent and distribution strictness.

Suggested values:
- `draft`: internal working state; incomplete/unstable content acceptable.
- `preview`: externally shareable pre-release for reviewers/test audiences.
- `release`: public/official release candidate.

`release_mode` and `status` are related but distinct:
- `status` describes workflow stage.
- `release_mode` describes outward publishing intent.

Suggested collection statuses:
- `planning`
- `draft`
- `ready_for_build`
- `proofing`
- `released`
- `archived`

Recommended pairing examples:
- `status: planning` with `release_mode: draft`
- `status: proofing` with `release_mode: preview`
- `status: released` with `release_mode: release`

---

## 6) How Collections Reference Story Packages

Collections reference story packages by slug only, via the `stories:` list.

Given this collection entry:

```yaml
stories:
  - raccoon-thieving-thumbs
```

the expected package path is:

```text
stories/raccoon-thieving-thumbs/
```

This aligns with the story package contract in `docs/story-package-schema.md`, where each story package is rooted at `stories/{story-slug}/`.

Important alignment notes:
- Collection slugs should correspond to each story package’s slug identity.
- Collection membership does not override story package lifecycle fields; it assembles already-defined packages into one release unit.
- Collection config should not duplicate story prose or package internals.

---

## 7) Relationship to Future Web/PDF/EPUB Builds

Collections are intended as the future top-level input for build pipelines.

For future build tooling (not implemented in this issue), a collection file can provide:
- ordered story inclusion,
- release metadata to render cover/front-matter/catalog entries,
- format targeting hints (`formats: [web, pdf, epub]`),
- lifecycle/release gates via `status` and `release_mode`.

Expected build behavior conceptually:
1. Read `collections/{collection-id}.yaml`.
2. Resolve each story slug to `stories/{story-slug}/`.
3. Assemble output artifacts in the configured order.
4. Apply format-specific rendering for web/PDF/EPUB.

This document defines only the schema contract and intent, not parser/build implementation.

---

## Required Concrete Example

```yaml
id: night-wanderers-volume-1
title: Just-So Stories: Night-Wanderers
subtitle: Tales from the Very-Near-Now
version: 0.1.0
author: Gavin Dean
stories:
  - raccoon-thieving-thumbs
```

---

## Extended Example (with suggested optional fields)

```yaml
id: night-wanderers-volume-1
title: Just-So Stories: Night-Wanderers
subtitle: Tales from the Very-Near-Now
version: 0.1.0
author: Gavin Dean
language: en
status: draft
release_mode: draft
formats:
  - web
  - pdf
  - epub
description: First themed collection of near-now animal tales.
created_at: "2026-05-23"
updated_at: "2026-05-23"
stories:
  - raccoon-thieving-thumbs
```

---

## Non-Goals for Issue #6

This schema document intentionally does **not**:
- implement collection parsing/validation,
- implement web/PDF/EPUB build tooling,
- create `collections/*.yaml` files in the repository,
- modify story packages or story text.

It defines the documentation contract for collection configuration only.
