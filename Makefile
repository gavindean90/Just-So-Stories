PYTHON ?= python3
PANDOC ?= pandoc
EPUB := dist/just-so-stories-volume-1.epub

.PHONY: setup build check epubcheck clean

setup:
	$(PYTHON) -m pip install -r requirements.txt

build:
	$(PYTHON) scripts/build.py --pandoc "$(PANDOC)"

check: build
	$(PYTHON) scripts/validate.py

epubcheck: check
	epubcheck "$(EPUB)"

clean:
	rm -rf build dist output
