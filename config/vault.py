"""Secret management and vault configuration."""

import os
from typing import Set

# Default backend: "infisical", "env", or "auto"
VAULT_BACKEND = os.getenv("EPISTEX_VAULT_BACKEND", "auto")

# Infisical configuration defaults
INFISICAL_API_URL = os.getenv("INFISICAL_API_URL", "https://secrets.dvlpid.my.id/api")
INFISICAL_PROJECT_ID = os.getenv("INFISICAL_PROJECT_ID", "f13379e0-9661-4f8e-81ef-0e81d1502da1")
INFISICAL_ENVIRONMENT = os.getenv("INFISICAL_ENV", "dev")
INFISICAL_SECRET_PATH = os.getenv("INFISICAL_PATH", "/")

# Universal Auth environment variables
INFISICAL_CLIENT_ID = os.getenv("INFISICAL_CLIENT_ID", "")
INFISICAL_CLIENT_SECRET = os.getenv("INFISICAL_CLIENT_SECRET", "")

# Hermetic runner environment sanitization
# Variables preserved from host during hermetic execution
SAFE_HOST_ENV_VARS: Set[str] = {
    "PATH",
    "SYSTEMROOT",
    "TERM",
    "LANG",
    "LC_ALL",
    "TZ",
    "PYTHONPATH",
    "HOME",
    "USER",
    "SHELL",
}
