# Just-So Stories

*Tales from the Very-Near-Now* is a collection of six animal tales by Gavin
Dean. This repository publishes the collection as a responsive static reader
and a reflowable EPUB.

## Canonical text

The six root-level `.txt` files are the sole source of truth for story prose.
The publishing code reads them directly: do not copy their text into templates,
the collection manifest, HTML, Markdown, or story-package files. Each nonblank
physical line becomes one semantic paragraph so standalone lines and the oral
score survive in every edition.

Collection metadata and the approved reading order live in
`collections/just-so-stories-volume-1.json`.

## Build locally

Requirements:

- Python 3.12
- Pandoc 3.1.3
- EPUBCheck 5.2.1 (optional locally, required in CI)

Build both editions and run the repository's structural and exact-text checks:

```sh
make check
```

The web reader is written to `dist/site/`, and the ebook is written to
`dist/just-so-stories-volume-1.epub`. These generated files are deliberately
ignored by Git. Preview the reader at `http://localhost:8000` with:

```sh
python3 -m http.server --directory dist/site 8000
```

To run the external EPUB standards validator as well:

```sh
make epubcheck
```

The internal validator checks required sources, the fixed collection order,
generated pages, previous/next links, EPUB metadata/navigation and exact story
text in both output formats. `dist/build-info.json` records the Pandoc version
and SHA-256 digest of each source used in a build.

## Publishing

`.github/workflows/publish.yml` builds and validates every pull request, push to
`main`, and manual run. A successful `main` build uploads the static site with
GitHub's official Pages artifact and deployment actions. The repository's Pages
source must be set to **GitHub Actions** once by a repository administrator.

Tags beginning with `v` run the same checks and create a GitHub Release with the
EPUB attached. The tag should match the manifest version, for example:

```sh
git tag v0.1.0
git push origin v0.1.0
```

## Future artwork and narration

Artwork and audio can be added without moving or rewriting the prose. Add
optional asset references to the relevant story object in the collection
manifest, keep publication-ready files under `assets/`, then teach the two
renderers to consume those references. For example, a future story entry may
gain an `artwork` object with ordered image paths or a `narration` object with an
audio path and timing-map path. The source filename remains unchanged and all
text-integrity checks continue to compare output against that root `.txt` file.

The larger package concepts in `docs/story-package-schema.md` remain useful for
future illustrated production, but the first text-only edition intentionally
does not duplicate prose into that aspirational structure.
