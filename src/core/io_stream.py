"""Streaming I/O and atomic filesystem mutation operations."""

import os
from pathlib import Path
import tempfile
from typing import Any, Dict, Tuple
from .yaml_parser import parse_restricted_yaml


def read_frontmatter_streaming(filepath: Path, max_lines: int = 100) -> Tuple[Dict[str, Any], int, str]:
    """Extract YAML frontmatter in O(K) space and time without loading full file body.

    Returns:
        Tuple of (metadata_dict, end_line_number, raw_frontmatter_string).
    """
    metadata_lines = []
    in_frontmatter = False
    delimiter_count = 0
    end_line = 0

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for idx, line in enumerate(f, start=1):
                stripped = line.strip()
                if stripped == "---":
                    delimiter_count += 1
                    if delimiter_count == 1:
                        in_frontmatter = True
                        continue
                    if delimiter_count == 2:
                        end_line = idx
                        break
                elif in_frontmatter:
                    metadata_lines.append(line)

                if idx > max_lines and delimiter_count < 2:
                    break
    except OSError:
        return {}, 0, ""

    if delimiter_count == 2:
        raw_text = "".join(metadata_lines)
        return parse_restricted_yaml(raw_text), end_line, raw_text
    return {}, 0, ""


def atomic_write_text(filepath: Path, content: str) -> None:
    """Atomically write text to prevent corrupt files if agent execution terminates."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = filepath.parent

    with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
        tf.write(content)
        temp_name = tf.name

    os.replace(temp_name, filepath)
