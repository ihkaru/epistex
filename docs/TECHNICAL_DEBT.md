# Technical Debt & Architecture Exemptions Ledger

This document tracks intentional architectural exemptions and in-memory test double providers in Epistex.

## Registered Exemptions

- `MemorySecretProvider` (src/providers/secrets/memory_provider.py): In-memory secret dictionary provider for hermetic testing environments [EPI-001]
- `is_available` (src/providers/secrets/memory_provider.py): Memory secret provider availability probe checking dictionary instance [EPI-001]
