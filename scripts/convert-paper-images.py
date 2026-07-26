#!/usr/bin/env python3
"""Render single-page paper figure PDFs to size-checked PNG previews."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_IMAGE_DIR = ROOT / "images" / "papers"
TEMP_DIR = ROOT / "tmp" / "pdfs"
DEFAULT_MAX_EDGE = 1600
DEFAULT_MAX_BYTES = 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class PaperImageError(RuntimeError):
    pass


@dataclass(frozen=True)
class ImageInfo:
    width: int
    height: int
    size_bytes: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert single-page paper figure PDFs to same-name PNGs and validate "
            "their dimensions and file sizes."
        )
    )
    parser.add_argument(
        "pdfs",
        nargs="*",
        type=Path,
        help="PDFs to process (default: every PDF in images/papers)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate existing PNG counterparts without converting",
    )
    parser.add_argument(
        "--max-edge",
        type=int,
        default=DEFAULT_MAX_EDGE,
        help=f"Maximum output width or height in pixels (default: {DEFAULT_MAX_EDGE})",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=DEFAULT_MAX_BYTES,
        help=f"Maximum PNG file size in bytes (default: {DEFAULT_MAX_BYTES})",
    )
    args = parser.parse_args()

    if args.max_edge <= 0:
        parser.error("--max-edge must be positive")
    if args.max_bytes <= 0:
        parser.error("--max-bytes must be positive")

    return args


def resolve_pdfs(paths: list[Path]) -> list[Path]:
    if not paths:
        return sorted(PAPER_IMAGE_DIR.glob("*.pdf"))

    resolved = []
    for path in paths:
        candidate = path if path.is_absolute() else Path.cwd() / path
        candidate = candidate.resolve()
        if candidate.suffix.lower() != ".pdf":
            raise PaperImageError(f"Expected a PDF: {path}")
        if not candidate.is_file():
            raise PaperImageError(f"PDF not found: {path}")
        resolved.append(candidate)
    return sorted(set(resolved))


def require_tool(name: str) -> str:
    executable = shutil.which(name)
    if executable:
        return executable
    raise PaperImageError(
        f"Missing '{name}'. Install Poppler first (macOS: brew install poppler)."
    )


def page_count(pdf: Path, pdfinfo: str) -> int:
    result = subprocess.run(
        [pdfinfo, str(pdf)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "unknown pdfinfo error"
        raise PaperImageError(f"Could not inspect {pdf.name}: {detail}")

    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        raise PaperImageError(f"Could not read page count from {pdf.name}")
    return int(match.group(1))


def png_info(path: Path) -> ImageInfo:
    try:
        with path.open("rb") as image_file:
            header = image_file.read(24)
    except OSError as error:
        raise PaperImageError(f"Could not read {path}: {error}") from error

    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise PaperImageError(f"Not a valid PNG: {path}")

    width, height = struct.unpack(">II", header[16:24])
    return ImageInfo(width=width, height=height, size_bytes=path.stat().st_size)


def validate_png(path: Path, max_edge: int, max_bytes: int) -> ImageInfo:
    info = png_info(path)
    if max(info.width, info.height) > max_edge:
        raise PaperImageError(
            f"{path.name} is {info.width}x{info.height}; max edge is {max_edge}px"
        )
    if info.size_bytes > max_bytes:
        raise PaperImageError(
            f"{path.name} is {format_bytes(info.size_bytes)}; limit is "
            f"{format_bytes(max_bytes)}"
        )
    return info


def format_bytes(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    return f"{size_bytes / 1024:.1f} KiB"


def display_path(path: Path) -> Path:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def render_pdf(
    pdf: Path,
    output: Path,
    pdftoppm: str,
    pdfinfo: str,
    max_edge: int,
    max_bytes: int,
) -> tuple[ImageInfo, bool]:
    pages = page_count(pdf, pdfinfo)
    if pages != 1:
        raise PaperImageError(
            f"{pdf.name} has {pages} pages; paper figure PDFs must have exactly one"
        )

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{pdf.stem}-", dir=TEMP_DIR) as temp:
        prefix = Path(temp) / pdf.stem
        rendered = prefix.with_suffix(".png")
        result = subprocess.run(
            [
                pdftoppm,
                "-f",
                "1",
                "-l",
                "1",
                "-png",
                "-singlefile",
                "-scale-to",
                str(max_edge),
                str(pdf),
                str(prefix),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0 or not rendered.is_file():
            detail = result.stderr.strip() or "pdftoppm did not create an output file"
            raise PaperImageError(f"Could not convert {pdf.name}: {detail}")

        info = validate_png(rendered, max_edge, max_bytes)
        unchanged = output.is_file() and output.read_bytes() == rendered.read_bytes()
        if not unchanged:
            output.parent.mkdir(parents=True, exist_ok=True)
            os.replace(rendered, output)
        return info, unchanged


def main() -> int:
    args = parse_args()
    try:
        pdfs = resolve_pdfs(args.pdfs)
        if not pdfs:
            raise PaperImageError("No paper figure PDFs found")

        pdftoppm = pdfinfo = ""
        if not args.check:
            pdftoppm = require_tool("pdftoppm")
            pdfinfo = require_tool("pdfinfo")

        failures = []
        for pdf in pdfs:
            output = pdf.with_suffix(".png")
            try:
                if args.check:
                    if not output.is_file():
                        raise PaperImageError(f"Missing generated image: {output}")
                    info = validate_png(output, args.max_edge, args.max_bytes)
                    action = "checked"
                else:
                    info, unchanged = render_pdf(
                        pdf,
                        output,
                        pdftoppm,
                        pdfinfo,
                        args.max_edge,
                        args.max_bytes,
                    )
                    action = "unchanged" if unchanged else "wrote"

                print(
                    f"{action:9} {display_path(output)} "
                    f"({info.width}x{info.height}, {format_bytes(info.size_bytes)})"
                )
            except (OSError, PaperImageError) as error:
                failures.append(str(error))

        if failures:
            for failure in failures:
                print(f"error: {failure}", file=sys.stderr)
            return 1
        return 0
    except PaperImageError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
