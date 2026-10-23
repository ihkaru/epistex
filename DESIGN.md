# Epistex System Design & Architecture (DESIGN.md)

## 1. High-Level Architecture
**Epistex** couples **Domain-Driven Content Organization** with an **Event-Driven CLI Engine** and **Hermetic Code Execution Runner**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        ep / gx / epistex CLI                           │
│            (Agent-First Stream Purity / POSIX Exit Codes)              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
[Commands Layer]            [Event Dispatcher]              [Core Engine]
 • cmd_doctor                • Pub / Sub Bus                 • Fast Pruned Scanner O(V)
 • cmd_map                   • Pipeline Pattern              • Streaming Frontmatter O(K)
 • cmd_create                • Domain Events                 • Bounded Min-Heap O(M log k)
 • cmd_schedule              • Audit / Telemetry             • Inverted Link Index O(N + R)
 • cmd_run                          │
 • cmd_secrets                      │
    │                               │
    ▼                               ▼
[Contracts & Providers (DIP)]
 • SecretProviderInterface ──► [InfisicalProvider] (First-party TLS injection)
                           ──► [EnvSecretProvider] (Process / .env fallback)
                           ──► [MemorySecretProvider] (Hermetic testing)
 • CodeRunnerInterface     ──► [HermeticCodeRunner] (Stripped env + runtime secrets)
                           ──► [DryCodeRunner] (Simulation mode)
```

## 2. SOLID & Clean Architecture
- **Single Responsibility Principle (SRP)**:
  - Each module handles one concern: scanner discovers files, reader parses frontmatter, validator checks schemas, runners execute processes.
  - Enforced by deterministic AST check: functions $\le 50$ lines, classes $\le 180$ lines.
- **Open/Closed Principle (OCP)**:
  - New commands can be added to `src/commands/` without modifying core traversal or validation logic.
  - New lifecycle listeners can subscribe to `EventDispatcher` without changing command handlers.
- **Liskov Substitution Principle (LSP)**:
  - `InfisicalSecretProvider` and `EnvSecretProvider` implement `SecretProviderInterface` interchangeably.
- **Interface Segregation Principle (ISP)**:
  - Dedicated contracts (`SecretProviderInterface`, `CodeRunnerInterface`, `EventDispatcherInterface`, `SchemaValidatorInterface`).
- **Dependency Inversion Principle (DIP)**:
  - Core runners and CLI commands depend strictly on abstract contracts defined in `src/contracts/`.

## 3. Algorithmic Complexity Comparison
| Operational Task | Naive Implementation | Optimized Starter Kit Engine | Complexity Improvement |
|---|---|---|---|
| **Filesystem Discovery** | Full `glob` / `os.walk` ($O(D_{\text{total}} \times F)$) | Pruned `os.scandir` iterator ($O(V)$) | Instantly skips `.git`, `node_modules`, `storage` without `os.stat`. |
| **Frontmatter Parsing** | Full file read into memory ($O(L)$ space & time) | Streaming line reader with early exit ($O(K)$) | Halts at second `---` delimiter ($K \le 30$ lines). $O(1)$ memory. |
| **Schedule / Deadline Sorting** | Collect all $M$ items and full array sort ($O(M \log M)$) | Bounded min-heap via `heapq` ($O(M \log k)$) | Sub-millisecond top-$k$ query for large knowledge bases. |
| **Link Integrity Audit** | Repeated disk lookups ($O(R \times \text{disk\_lookup})$) | Single-pass inverted index ($O(N + R)$) | Zero repeated disk stat operations. |
| **Repository Map** | Unbounded recursive directory listing | Token-budget bounded depth pruning ($O(d)$) | Guarantees small, predictable token payload for AI agents. |

## 4. Hermetic Execution & Secret Injection Model
- **Zero-Disk Invariant**: Injected secrets are never written to disk (`.env`, temporary files, or cache).
- **Environment Sanitization**: Child processes inherit only a safe allowlist of host environment variables (`PATH`, `TERM`, `LANG`, etc.), preventing host variable pollution.
- **First-Party Infisical Provider**: Direct extraction from Infisical CLI over TLS.
- **Universal Auth Integration**: Machine-to-machine authentication via Infisical Universal Auth (`client-id` and `client-secret`).
- **Graceful Zero-Crash Fallback**: Automatically degrades to `EnvSecretProvider` when Infisical is unconfigured.

## 5. Cloud Asset Offloading & Tiered Discovery (Git Bloat Prevention)
Storing large binary assets (PDFs, images, datasets, archives) directly in Git causes repository bloat and slows down clones and AI context loading.

### A. Companion Markdown Pointer Pattern
- **Git Repository**: Stores lightweight companion markdown files (`category: asset-companion`) containing frontmatter metadata (`remote_key`, `sha256`, `size_bytes`, `mime_type`, `storage_backend`).
- **Remote Cloud / Local Cache**: Heavy binary payloads live in S3-compatible cloud storage (or local offline cache).
- **Zero Vendor Lock-In**: Interface-first `AssetStorageInterface` decouples the codebase from any cloud provider. Standard SigV4 S3 provider works seamlessly across AWS S3, Cloudflare R2, MinIO, Ceph, Backblaze B2, and Coolify S3 using pure Python standard library.

### B. Tiered Discovery Architecture
- **Tier 1: Local Offline Git Discovery (Default)**:
  - Commands like `gx map` and `gx doctor` only inspect local markdown files and pointers.
  - Zero network overhead, instant execution, 100% offline-ready.
- **Tier 2: On-Demand Remote Verification & Hydration (Opt-In)**:
  - `gx asset check <key>`: Verifies remote asset existence without downloading the blob.
  - `gx asset pull <key>`: Streams and verifies SHA-256 checksum on-demand.
  - `gx doctor --check-assets`: Verifies whether remote assets referenced in companion documents actually exist in cloud storage.
  - `gx map --with-assets`: Embeds remote asset metadata into the repository tree.

### C. Cloud Authentication Modes (Opt-In & Hermetic)
To guarantee security and flexibility across CI/CD, local dev, and enterprise agent environments, cloud storage authentication supports three distinct modes via `--cloud-auth` or `KB_CLOUD_AUTH`:
- **`hermetic` (Hermetic Secret Injection)**:
  - Completely bypasses ambient host `os.environ`.
  - Credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_ENDPOINT_URL`, etc.) are resolved strictly in memory from `SecretProviderInterface` (e.g., Infisical Vault).
  - If keys are missing in the vault, raises `VaultError` with an actionable fix hint. Zero credentials touch the disk.
- **`env` (Environment-Only)**:
  - Resolves credentials strictly from host environment variables (`os.environ`).
  - Useful for traditional container setups or standard CI runners.
- **`auto` (Hybrid Default)**:
  - Attempts secret retrieval from the active `SecretProviderInterface` first.
  - Falls back gracefully to host environment variables if vault values are not present.

