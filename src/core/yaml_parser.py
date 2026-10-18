"""Safe zero-dependency restricted YAML parser for frontmatter metadata."""

from typing import Any, Dict, List, Tuple


def _parse_scalar(val: str) -> Any:
    """Parse scalar string into bool, int, float, or stripped string."""
    clean = val.strip().strip("'\"")
    if clean.lower() == "true":
        return True
    if clean.lower() == "false":
        return False
    if clean.lower() in ("null", "none", "~", ""):
        return None
    try:
        return int(clean)
    except ValueError:
        pass
    try:
        return float(clean)
    except ValueError:
        pass
    return clean


def _parse_inline_list(val: str) -> List[Any]:
    """Parse inline YAML list format, e.g. [a, b, c]."""
    inner = val.strip()[1:-1].strip()
    if not inner:
        return []
    items = [item.strip() for item in inner.split(",")]
    return [_parse_scalar(item) for item in items if item]


def _parse_block_list(lines: List[str], start_idx: int) -> Tuple[List[Any], int]:
    """Parse indented or block list of scalars or single-level dicts."""
    items: List[Any] = []
    i = start_idx
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if not (line.startswith("  ") or line.startswith("\t") or stripped.startswith("-")):
            break

        if stripped.startswith("-"):
            raw_item = stripped[1:].strip()
            if ":" in raw_item:
                sub_k, sub_v = raw_item.split(":", 1)
                item_dict = {sub_k.strip(): _parse_scalar(sub_v)}
                i += 1
                while i < len(lines) and lines[i].startswith("    ") and not lines[i].strip().startswith("-"):
                    child = lines[i].strip()
                    if ":" in child:
                        ck, cv = child.split(":", 1)
                        item_dict[ck.strip()] = _parse_scalar(cv)
                    i += 1
                items.append(item_dict)
                continue
            items.append(_parse_scalar(raw_item))
        i += 1
    return items, i


def parse_restricted_yaml(yaml_text: str) -> Dict[str, Any]:
    """Parse safe subset of YAML (scalars, lists, inline lists, dicts)."""
    result: Dict[str, Any] = {}
    lines = yaml_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val_clean = val.strip()

            if val_clean.startswith("[") and val_clean.endswith("]"):
                result[key] = _parse_inline_list(val_clean)
            elif not val_clean and (i + 1 < len(lines)) and lines[i + 1].strip().startswith("-"):
                items, next_i = _parse_block_list(lines, i + 1)
                result[key] = items
                i = next_i
                continue
            else:
                result[key] = _parse_scalar(val_clean)
        i += 1
    return result
