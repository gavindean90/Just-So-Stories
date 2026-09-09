#!/usr/bin/env python3
"""Validate manifest, editions, accessibility structure, and text integrity."""

from __future__ import annotations

import argparse
from collections import Counter
import html
import os
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

from build import (
    DEFAULT_MANIFEST,
    DEFAULT_OUTPUT,
    DEFAULT_PDF_OUTPUT,
    ROOT,
    load_manifest,
    source_units,
)


APPROVED_ORDER = [
    "How the Coyote Found His Moon-Calling Voice.txt",
    "How the Raccoon Got Her Thieving Thumbs.txt",
    "How the Skunk Demanded Respect.txt",
    "How the Seagull Snatched the Golden Fry.txt",
    "How the Opossum Cheated the Hound.txt",
    "How the Black Widow Wove the Red Warning.txt",
]


class StoryTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.units: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._capture = False
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "p" and "story-text" in attributes.get("class", "").split():
            self._capture = True
            self._text = []
        if tag == "a" and attributes.get("href"):
            self.links.append((attributes["href"] or "", attributes.get("rel", "") or ""))

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self._capture:
            self.units.append(html.unescape("".join(self._text)))
            self._capture = False


def validate_manifest(manifest: dict) -> None:
    actual_order = [story["source"] for story in manifest["stories"]]
    if actual_order != APPROVED_ORDER:
        raise ValueError(
            "Manifest story order does not match the approved six-story collection order"
        )
    if set(manifest["formats"]) != {"web", "epub", "pdf"}:
        raise ValueError("Manifest formats must declare web, epub, and pdf")


def validate_release_ref(manifest: dict) -> None:
    if os.environ.get("GITHUB_REF_TYPE") != "tag":
        return
    expected_tag = f'v{manifest["version"]}'
    actual_tag = os.environ.get("GITHUB_REF_NAME")
    if actual_tag != expected_tag:
        raise ValueError(
            f"Release tag {actual_tag!r} does not match manifest version {expected_tag!r}"
        )


def validate_site(manifest: dict, output_dir: Path) -> None:
    site_dir = output_dir / "site"
    index_path = site_dir / "index.html"
    if not index_path.is_file():
        raise ValueError("Static reader landing page was not generated")
    index = index_path.read_text(encoding="utf-8")
    positions = [index.find(f'stories/{story["id"]}.html') for story in manifest["stories"]]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        raise ValueError("Landing page table of contents is missing or out of order")

    for index, story in enumerate(manifest["stories"]):
        story_path = site_dir / "stories" / f'{story["id"]}.html'
        if not story_path.is_file():
            raise ValueError(f"Story page was not generated: {story['id']}")
        parser = StoryTextParser()
        parser.feed(story_path.read_text(encoding="utf-8"))
        canonical = source_units(ROOT / story["source"])
        if parser.units != canonical:
            raise ValueError(f"HTML text-integrity failure: {story['source']}")

        hrefs = [href for href, _ in parser.links]
        expected_previous = (
            f'{manifest["stories"][index - 1]["id"]}.html' if index else "../index.html"
        )
        expected_next = (
            f'{manifest["stories"][index + 1]["id"]}.html'
            if index + 1 < len(manifest["stories"])
            else "../index.html"
        )
        if expected_previous not in hrefs or expected_next not in hrefs:
            raise ValueError(f"Previous/next navigation failure: {story['id']}")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def epub_story_units(data: bytes) -> list[str]:
    root = ElementTree.fromstring(data)
    for section in root.iter():
        classes = section.attrib.get("class", "").split()
        if local_name(section.tag) == "section" and "story" in classes:
            return [
                "".join(element.itertext())
                for element in section.iter()
                if local_name(element.tag) == "p"
            ]
    return []


def validate_epub(manifest: dict, output_dir: Path) -> None:
    epub_path = output_dir / f'{manifest["id"]}.epub'
    if not epub_path.is_file():
        raise ValueError("EPUB was not generated")
    if not zipfile.is_zipfile(epub_path):
        raise ValueError("EPUB is not a ZIP container")

    with zipfile.ZipFile(epub_path) as archive:
        names = archive.namelist()
        if not names or names[0] != "mimetype":
            raise ValueError("EPUB mimetype must be the first container entry")
        if archive.read("mimetype") != b"application/epub+zip":
            raise ValueError("EPUB has an invalid mimetype")
        container = ElementTree.fromstring(archive.read("META-INF/container.xml"))
        package_paths = [
            node.attrib["full-path"]
            for node in container.iter()
            if local_name(node.tag) == "rootfile"
        ]
        if len(package_paths) != 1:
            raise ValueError("EPUB must identify exactly one package document")
        package_path = package_paths[0]
        package = ElementTree.fromstring(archive.read(package_path))
        metadata_text = {
            local_name(node.tag): "".join(node.itertext())
            for node in package.iter()
            if local_name(node.tag) in {"title", "creator", "language", "identifier"}
        }
        expected_metadata = {
            "title": manifest["title"],
            "creator": manifest["author"],
            "language": manifest["language"],
            "identifier": manifest["identifier"],
        }
        for key, expected in expected_metadata.items():
            if metadata_text.get(key) != expected:
                raise ValueError(f"EPUB metadata mismatch for {key}")

        base = Path(package_path).parent
        package_items = {
            item.attrib["id"]: item.attrib["href"]
            for item in package.iter()
            if local_name(item.tag) == "item"
        }
        spine_paths = [
            (base / package_items[itemref.attrib["idref"]]).as_posix()
            for itemref in package.iter()
            if local_name(itemref.tag) == "itemref"
        ]
        all_units: list[str] = []
        for name in spine_paths:
            all_units.extend(epub_story_units(archive.read(name)))
        canonical_units = [
            unit
            for story in manifest["stories"]
            for unit in source_units(ROOT / story["source"])
        ]
        if all_units != canonical_units:
            raise ValueError("EPUB text-integrity or story-order failure")

        nav_items = [
            item
            for item in package.iter()
            if local_name(item.tag) == "item"
            and "nav" in item.attrib.get("properties", "").split()
        ]
        if len(nav_items) != 1:
            raise ValueError("EPUB must contain exactly one navigation document")
        nav_path = (base / nav_items[0].attrib["href"]).as_posix()
        if nav_path not in names:
            raise ValueError("EPUB navigation document is missing")
        nav = ElementTree.fromstring(archive.read(nav_path))
        nav_titles = [
            "".join(element.itertext())
            for element in nav.iter()
            if local_name(element.tag) == "a"
            and "text/ch" in element.attrib.get("href", "")
        ]
        expected_titles = [story["title"] for story in manifest["stories"]]
        if nav_titles != expected_titles:
            raise ValueError("EPUB table of contents is missing or out of order")


def flatten_outline(items: list) -> list:
    flattened = []
    for item in items:
        if isinstance(item, list):
            flattened.extend(flatten_outline(item))
        else:
            flattened.append(item)
    return flattened


def normalize_pdf_text(text: str) -> str:
    text = re.sub(r"\n\s*\d+\s*(?=\n|$)", "\n", text)
    text = re.sub(r"-\s+", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def pdf_structure_counts(structure_root, indirect_object_type) -> Counter:
    counts: Counter = Counter()
    visited: set[tuple[int, int]] = set()

    def walk(value) -> None:
        if isinstance(value, indirect_object_type):
            reference = (value.idnum, value.generation)
            if reference in visited:
                return
            visited.add(reference)
            value = value.get_object()
        if isinstance(value, dict):
            if "/S" in value:
                counts[str(value["/S"])] += 1
            if "/K" in value:
                walk(value["/K"])
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(structure_root)
    return counts


def validate_pdf(manifest: dict, pdf_output_dir: Path) -> None:
    try:
        from pypdf import PdfReader
        from pypdf.generic import IndirectObject
    except ImportError as exc:
        raise RuntimeError(
            "pypdf is required for PDF validation; run: python3 -m pip install -r requirements.txt"
        ) from exc

    pdf_path = pdf_output_dir / f'{manifest["id"]}.pdf'
    if not pdf_path.is_file():
        raise ValueError("PDF was not generated")
    reader = PdfReader(pdf_path)
    if not reader.pages:
        raise ValueError("PDF has no pages")
    if reader.is_encrypted:
        raise ValueError("PDF must not be encrypted")

    metadata = reader.metadata or {}
    expected_metadata = {
        "/Title": manifest["title"],
        "/Author": manifest["author"],
        "/Subject": manifest["description"],
    }
    for key, expected in expected_metadata.items():
        if metadata.get(key) != expected:
            raise ValueError(f"PDF metadata mismatch for {key}")

    root = reader.root_object
    if root.get("/Lang") != manifest["language"]:
        raise ValueError("PDF document language is missing or incorrect")
    if not root.get("/MarkInfo", {}).get("/Marked"):
        raise ValueError("PDF is not marked as tagged")
    if not root.get("/ViewerPreferences", {}).get("/DisplayDocTitle"):
        raise ValueError("PDF viewer is not configured to display the document title")
    if "/StructTreeRoot" not in root:
        raise ValueError("PDF structure tree is missing")
    xmp = root.get("/Metadata").get_object().get_data()
    if b'pdfuaid:part="1"' not in xmp:
        raise ValueError("PDF/UA-1 identification metadata is missing")

    expected_unit_count = sum(
        len(source_units(ROOT / story["source"])) for story in manifest["stories"]
    )
    structure_counts = pdf_structure_counts(root["/StructTreeRoot"], IndirectObject)
    if structure_counts["/Document"] != 1:
        raise ValueError("PDF must have exactly one tagged document root")
    if structure_counts["/H1"] < 1 or structure_counts["/H2"] < len(manifest["stories"]):
        raise ValueError("PDF heading tags are incomplete")
    if structure_counts["/P"] < expected_unit_count:
        raise ValueError("PDF paragraph tags are incomplete")
    if structure_counts["/L"] < 1 or structure_counts["/Link"] < len(manifest["stories"]):
        raise ValueError("PDF contents list or link tags are incomplete")

    destinations = {
        item.title: reader.get_destination_page_number(item)
        for item in flatten_outline(reader.outline)
    }
    expected_titles = [story["title"] for story in manifest["stories"]]
    if any(title not in destinations for title in expected_titles):
        raise ValueError("PDF chapter bookmarks are incomplete")
    chapter_pages = [destinations[title] for title in expected_titles]
    if chapter_pages != sorted(set(chapter_pages)):
        raise ValueError("PDF chapter bookmarks are out of order")

    for index, story in enumerate(manifest["stories"]):
        start_page = chapter_pages[index]
        end_page = (
            chapter_pages[index + 1]
            if index + 1 < len(chapter_pages)
            else len(reader.pages)
        )
        extracted = normalize_pdf_text(
            "\n".join(
                reader.pages[page].extract_text() or ""
                for page in range(start_page, end_page)
            )
        )
        title = normalize_pdf_text(story["title"])
        if not extracted.startswith(title):
            raise ValueError(f"PDF chapter heading mismatch: {story['title']}")
        extracted_story = extracted[len(title):].strip()
        canonical_story = normalize_pdf_text(
            " ".join(source_units(ROOT / story["source"]))
        )
        if extracted_story != canonical_story:
            raise ValueError(f"PDF text-integrity failure: {story['source']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pdf-output", type=Path, default=DEFAULT_PDF_OUTPUT)
    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_args()
        collection = load_manifest(args.manifest.resolve())
        validate_manifest(collection)
        validate_release_ref(collection)
        validate_site(collection, args.output.resolve())
        validate_epub(collection, args.output.resolve())
        validate_pdf(collection, args.pdf_output.resolve())
        print(
            "Validated manifest, order, navigation, accessibility structure, "
            "and exact HTML/EPUB/PDF text integrity."
        )
    except (
        ValueError,
        RuntimeError,
        OSError,
        ElementTree.ParseError,
        zipfile.BadZipFile,
    ) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
