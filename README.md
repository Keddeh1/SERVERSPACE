# KEDDEH.COM — Sovereign Runtime Environment

This repository is the custom runtime foundation for KEDDEH.COM, DNS server runtimes, and any auxiliary services needed for autonomous, self-hosted operation.

The design intentionally avoids GitHub-managed runtime dependencies and uses a local runtime model with explicit file-based packages and custom HTML service modules.

## Repository purpose

- KEDDEH.COM website host
- DNS runtime services
- Local runtime packages
- Custom service orchestration
- Self-contained HTML modules and runtime scripts

## Branches

- `main`: default stable branch
- `codex`: active runtime and architecture development branch

## Runtime model

This project uses own local runtime files and custom web packages instead of pulling runtime support from GitHub dependency managers.

Custom runtime paths:

- `runtime/`
- `packages/`
- `sites/`
- `dns/`

## Quick start

```bash
chmod +x runtime/bootstrap.sh
./runtime/bootstrap.sh
```

This creates the working local runtime tree including:

- custom runtime config
- DNS runtime directory
- HTML package staging area
- site root for KEDDEH.COM

## Important

This repository is structured to keep all runtime logic local, portable, and under your control. No GitHub-hosted runtime dependency chain is required.
