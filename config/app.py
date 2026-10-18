"""Centralized application configuration and constants."""

from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT_DIR / "knowledge"
STORAGE_DIR = ROOT_DIR / "storage"
CACHE_DIR = STORAGE_DIR / "cache"
LOGS_DIR = STORAGE_DIR / "logs"

# Application Metadata
APP_NAME = "gnosidex"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Gnosidex: Enterprise Git-Based Knowledge Base & Hermetic Execution Starter Kit"

# Directories to prune during scanner traversal (O(V) pruning)
DEFAULT_IGNORED_DIRS = {
    ".git",
    ".githooks",
    ".github",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".cache",
    ".pytest_cache",
    "storage",
    "scratch",
    "dist",
    "build",
}

# Standard POSIX / BSD exit codes (sysexits.h)
EX_OK = 0
EX_USAGE = 2
EX_DATAERR = 65
EX_NOINPUT = 66
EX_SOFTWARE = 70
EX_CONFIG = 78
