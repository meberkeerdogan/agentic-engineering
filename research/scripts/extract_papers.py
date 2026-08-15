"""Validate research PDFs and extract text plus machine-readable metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


def extract_paper(
    path: Path, output_directory: Path | None = None
) -> dict[str, object]:
    data = path.read_bytes()
    if not data.startswith(b"%PDF-"):
        raise ValueError(f"Not a PDF: {path}")

    reader = PdfReader(path)
    text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
    if output_directory is not None:
        output_directory.mkdir(parents=True, exist_ok=True)
        (output_directory / f"{path.stem}.txt").write_text(text, encoding="utf-8")

    metadata = reader.metadata
    return {
        "file": path.name,
        "pages": len(reader.pages),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "title": metadata.title if metadata else None,
        "text_chars": len(text),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paper_directory", type=Path)
    parser.add_argument(
        "output_directory",
        type=Path,
        nargs="?",
        help="Optional directory for extracted page text",
    )
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    records = [
        extract_paper(path, args.output_directory)
        for path in sorted(args.paper_directory.glob("*.pdf"))
    ]
    payload = json.dumps(records, indent=2, ensure_ascii=False) + "\n"

    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
