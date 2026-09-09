#!/usr/bin/env python3
"""Build the static reader, EPUB, and PDF from canonical root-level text files."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from string import Template


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "collections" / "just-so-stories-volume-1.json"
DEFAULT_OUTPUT = ROOT / "dist"
DEFAULT_PDF_OUTPUT = ROOT / "output" / "pdf"


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "id", "title", "subtitle", "author", "language", "version",
        "publication_date", "identifier", "description", "formats", "stories",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        raise ValueError(f"Manifest is missing required keys: {', '.join(missing)}")
    if not manifest["stories"]:
        raise ValueError("Manifest must contain at least one story")

    seen_ids: set[str] = set()
    seen_sources: set[str] = set()
    for story in manifest["stories"]:
        story_missing = {"id", "title", "source"} - story.keys()
        if story_missing:
            raise ValueError(f"Story entry is missing: {', '.join(sorted(story_missing))}")
        if story["id"] in seen_ids or story["source"] in seen_sources:
            raise ValueError(f"Duplicate story id or source: {story['id']}")
        if Path(story["source"]).name != story["source"] or not story["source"].endswith(".txt"):
            raise ValueError(f"Story source must be a root-level .txt filename: {story['source']}")
        source_path = ROOT / story["source"]
        if not source_path.is_file():
            raise ValueError(f"Canonical source does not exist: {story['source']}")
        seen_ids.add(story["id"])
        seen_sources.add(story["source"])
    return manifest


def source_units(source_path: Path) -> list[str]:
    """Return canonical semantic text units: each nonblank physical source line."""
    text = source_path.read_text(encoding="utf-8")
    if "\r" in text:
        raise ValueError(f"Canonical source must use LF line endings: {source_path.name}")
    units = [line.strip() for line in text.splitlines() if line.strip()]
    if not units:
        raise ValueError(f"Canonical source is empty: {source_path.name}")
    return units


def render_text_units(units: list[str], indent: str = "    ") -> str:
    return "\n".join(
        f'{indent}<p class="story-text" data-source-unit="{index}">{html.escape(text)}</p>'
        for index, text in enumerate(units, start=1)
    )


def render_page(template: Template, manifest: dict, **values: str) -> str:
    defaults = {
        "language": html.escape(manifest["language"], quote=True),
        "description": html.escape(manifest["description"], quote=True),
        "collection_title": html.escape(manifest["title"]),
        "author": html.escape(manifest["author"]),
        "version": html.escape(manifest["version"]),
        "story_id": "",
        "story_title": "",
        "story_url": "",
    }
    defaults.update(values)
    return template.substitute(defaults)


def build_site(manifest: dict, output_dir: Path) -> None:
    site_dir = output_dir / "site"
    stories_dir = site_dir / "stories"
    assets_dir = site_dir / "assets"
    stories_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(ROOT / "assets" / "reader.css", assets_dir / "reader.css")
    shutil.copy2(ROOT / "assets" / "reader.js", assets_dir / "reader.js")
    page_template = Template((ROOT / "templates" / "page.html").read_text(encoding="utf-8"))

    items = []
    for index, story in enumerate(manifest["stories"], start=1):
        items.append(
            "      <li>"
            f'<a href="stories/{html.escape(story["id"], quote=True)}.html">'
            f'<span class="story-number">{index:02}</span>'
            f'<span>{html.escape(story["title"])}</span></a></li>'
        )
    landing_content = f'''    <section class="hero" aria-labelledby="collection-title">
      <p class="eyebrow">A collection by {html.escape(manifest["author"])}</p>
      <h1 id="collection-title">{html.escape(manifest["title"])}</h1>
      <p class="subtitle">{html.escape(manifest["subtitle"])}</p>
      <p class="description">{html.escape(manifest["description"])}</p>
      <a class="continue-link" data-continue-reading hidden href="#">Continue reading</a>
    </section>
    <nav class="contents" aria-labelledby="contents-heading">
      <h2 id="contents-heading">Contents</h2>
      <ol class="story-list">
{chr(10).join(items)}
      </ol>
    </nav>'''
    index_html = render_page(
        page_template,
        manifest,
        page_title=html.escape(f'{manifest["title"]} — {manifest["subtitle"]}'),
        asset_prefix=".",
        home_url="index.html",
        main_class="landing",
        content=landing_content,
        story_url="",
    )
    (site_dir / "index.html").write_text(index_html, encoding="utf-8", newline="\n")

    for index, story in enumerate(manifest["stories"]):
        units = source_units(ROOT / story["source"])
        previous_story = manifest["stories"][index - 1] if index else None
        next_story = manifest["stories"][index + 1] if index + 1 < len(manifest["stories"]) else None
        links = []
        if previous_story:
            links.append(
                f'<a rel="prev" href="{html.escape(previous_story["id"], quote=True)}.html">'
                f'<span>Previous</span>{html.escape(previous_story["title"])}</a>'
            )
        else:
            links.append('<a href="../index.html"><span>Contents</span>All stories</a>')
        if next_story:
            links.append(
                f'<a rel="next" href="{html.escape(next_story["id"], quote=True)}.html">'
                f'<span>Next</span>{html.escape(next_story["title"])}</a>'
            )
        else:
            links.append('<a href="../index.html"><span>Finished</span>Back to contents</a>')

        content = f'''    <header class="story-header">
      <p class="eyebrow">Story {index + 1} of {len(manifest["stories"])}</p>
      <h1>{html.escape(story["title"])}</h1>
    </header>
    <article class="story" aria-label="Story text">
{render_text_units(units)}
    </article>
    <nav class="chapter-nav" aria-label="Story navigation">
      {links[0]}
      {links[1]}
    </nav>'''
        story_html = render_page(
            page_template,
            manifest,
            page_title=html.escape(f'{story["title"]} — {manifest["title"]}'),
            asset_prefix="..",
            home_url="../index.html",
            main_class="story-shell",
            content=content,
            story_id=html.escape(story["id"], quote=True),
            story_title=html.escape(story["title"], quote=True),
            story_url=html.escape(f'stories/{story["id"]}.html', quote=True),
        )
        (stories_dir / f'{story["id"]}.html').write_text(story_html, encoding="utf-8", newline="\n")


def build_epub(manifest: dict, output_dir: Path, pandoc: str) -> None:
    work_dir = output_dir.parent / "build" / "epub"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    chapter_paths = []
    for story in manifest["stories"]:
        units = source_units(ROOT / story["source"])
        chapter_path = work_dir / f'{story["id"]}.html'
        chapter = f'''<!doctype html>
<html lang="{html.escape(manifest["language"], quote=True)}">
<head><meta charset="utf-8"><title>{html.escape(story["title"])}</title></head>
<body>
<section class="story" data-story-id="{html.escape(story["id"], quote=True)}">
  <h1>{html.escape(story["title"])}</h1>
{render_text_units(units, indent="  ")}
</section>
</body>
</html>'''
        chapter_path.write_text(chapter, encoding="utf-8", newline="\n")
        chapter_paths.append(chapter_path)

    epub_path = output_dir / f'{manifest["id"]}.epub'
    command = [
        pandoc,
        "--from=html",
        "--to=epub3",
        "--standalone",
        "--toc",
        "--split-level=1",
        f'--css={ROOT / "templates" / "epub.css"}',
        "--metadata", f'title={manifest["title"]}',
        "--metadata", f'subtitle={manifest["subtitle"]}',
        "--metadata", f'author={manifest["author"]}',
        "--metadata", f'lang={manifest["language"]}',
        "--metadata", f'date={manifest["publication_date"]}',
        "--metadata", f'identifier={manifest["identifier"]}',
        "--output", str(epub_path),
        *map(str, chapter_paths),
    ]
    environment = os.environ.copy()
    environment.setdefault("SOURCE_DATE_EPOCH", "1788912000")
    try:
        subprocess.run(command, cwd=ROOT, env=environment, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Pandoc executable not found: {pandoc}") from exc


def build_pdf(manifest: dict, pdf_output_dir: Path) -> str:
    try:
        import weasyprint
        from weasyprint import CSS, HTML
    except ImportError as exc:
        raise RuntimeError(
            "WeasyPrint is required for PDF output; run: python3 -m pip install -r requirements.txt"
        ) from exc

    if pdf_output_dir.exists():
        shutil.rmtree(pdf_output_dir)
    pdf_output_dir.mkdir(parents=True)

    template = Template((ROOT / "templates" / "pdf.html").read_text(encoding="utf-8"))
    toc = "\n".join(
        f'      <li><a href="#{html.escape(story["id"], quote=True)}">'
        f'{html.escape(story["title"])}</a></li>'
        for story in manifest["stories"]
    )
    stories = []
    for story in manifest["stories"]:
        units = source_units(ROOT / story["source"])
        stories.append(
            f'    <section class="story" id="{html.escape(story["id"], quote=True)}" '
            f'aria-labelledby="{html.escape(story["id"], quote=True)}-title">\n'
            f'      <h2 id="{html.escape(story["id"], quote=True)}-title">'
            f'{html.escape(story["title"])}</h2>\n'
            f'{render_text_units(units, indent="      ")}\n'
            "    </section>"
        )

    document = template.substitute(
        language=html.escape(manifest["language"], quote=True),
        author=html.escape(manifest["author"], quote=True),
        description=html.escape(manifest["description"], quote=True),
        publication_date=html.escape(manifest["publication_date"], quote=True),
        collection_title=html.escape(manifest["title"]),
        subtitle=html.escape(manifest["subtitle"]),
        toc=toc,
        stories="\n".join(stories),
    )
    pdf_path = pdf_output_dir / f'{manifest["id"]}.pdf'
    HTML(string=document, base_url=str(ROOT)).write_pdf(
        pdf_path,
        stylesheets=[CSS(filename=ROOT / "templates" / "pdf.css")],
        pdf_variant="pdf/ua-1",
        pdf_tags=True,
    )
    return weasyprint.__version__


def write_build_info(
    manifest: dict, output_dir: Path, pandoc: str, weasyprint_version: str
) -> None:
    sources = {}
    for story in manifest["stories"]:
        data = (ROOT / story["source"]).read_bytes()
        sources[story["source"]] = hashlib.sha256(data).hexdigest()
    pandoc_version = subprocess.run(
        [pandoc, "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]
    info = {
        "collection": manifest["id"],
        "version": manifest["version"],
        "pandoc": pandoc_version,
        "weasyprint": f"WeasyPrint {weasyprint_version}",
        "source_sha256": sources,
    }
    (output_dir / "build-info.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )


def build(
    manifest_path: Path, output_dir: Path, pdf_output_dir: Path, pandoc: str
) -> None:
    manifest = load_manifest(manifest_path)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    build_site(manifest, output_dir)
    build_epub(manifest, output_dir, pandoc)
    weasyprint_version = build_pdf(manifest, pdf_output_dir)
    write_build_info(manifest, output_dir, pandoc, weasyprint_version)
    print(f"Built web reader: {output_dir / 'site' / 'index.html'}")
    print(f"Built EPUB: {output_dir / (manifest['id'] + '.epub')}")
    print(f"Built accessible PDF: {pdf_output_dir / (manifest['id'] + '.pdf')}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pdf-output", type=Path, default=DEFAULT_PDF_OUTPUT)
    parser.add_argument("--pandoc", default=os.environ.get("PANDOC", "pandoc"))
    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_args()
        build(
            args.manifest.resolve(),
            args.output.resolve(),
            args.pdf_output.resolve(),
            args.pandoc,
        )
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"build failed: {error}", file=sys.stderr)
        raise SystemExit(1)
