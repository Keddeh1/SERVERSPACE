#!/usr/bin/env bash
set -eu

RUNTIME_ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$RUNTIME_ROOT/.." && pwd)"

mkdir -p "$REPO_ROOT/runtime/.state"
mkdir -p "$REPO_ROOT/runtime/logs"
mkdir -p "$REPO_ROOT/runtime/dns"
mkdir -p "$REPO_ROOT/runtime/boot"
mkdir -p "$REPO_ROOT/runtime/packages"
mkdir -p "$REPO_ROOT/sites/keddeh.com"
mkdir -p "$REPO_ROOT/packages/html"
mkdir -p "$REPO_ROOT/dns"

cat > "$REPO_ROOT/runtime/config/custom-runtime.json" <<'EOF'
{
  "runtime_name": "KEDDEH_CUSTOM_RUNTIME",
  "version": "0.1.0",
  "owner": "Keddeh1",
  "repository": "SERVERSPACE",
  "branch": "codex",
  "runtime_mode": "local_custom",
  "dependency_policy": "no_github_runtime_dependencies",
  "package_sources": [
    "runtime/packages",
    "packages/html",
    "sites/keddeh.com",
    "dns"
  ],
  "dns": {
    "resolver_root": "runtime/dns",
    "resolver_mode": "html_package_runtime",
    "allow_local_only": true
  },
  "web": {
    "site_root": "sites/keddeh.com",
    "served_files": [
      "index.html",
      "assets",
      "config"
    ]
  }
}
EOF

cat > "$REPO_ROOT/sites/keddeh.com/index.html" <<'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>KEDDEH.COM</title>
    <style>
      :root {
        --bg: #07111d;
        --panel: #0d1d2d;
        --line: #214a6d;
        --text: #dfefff;
        --muted: #9bb7d1;
        --accent: #5ec5ff;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        background: linear-gradient(180deg, #07111d, #0b1c2a 40%, #091722);
        color: var(--text);
        font-family: Arial, Helvetica, sans-serif;
      }
      .wrap {
        max-width: 980px;
        margin: 0 auto;
        padding: 56px 24px 80px;
      }
      .panel {
        background: rgba(13, 29, 45, 0.9);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 16px 38px rgba(0,0,0,0.25);
      }
      h1 {
        margin: 0 0 16px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: clamp(2rem, 4vw, 4rem);
      }
      p {
        color: var(--muted);
        line-height: 1.8;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 18px;
        margin-top: 32px;
      }
      .card {
        background: rgba(255,255,255,0.02);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 18px;
      }
      .label {
        color: var(--accent);
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: 0.72rem;
      }
    </style>
  </head>
  <body>
    <div class="wrap">
      <div class="panel">
        <div class="label">KEDDEH SYSTEMS</div>
        <h1>KEDDEH.COM</h1>
        <p>
          Custom runtime environment for sovereign, self-hosted infrastructure. This repository contains the
          active development branch for KEDDEH.COM, DNS runtime services, and local HTML package modules.
        </p>

        <div class="grid">
          <div class="card">
            <div class="label">Runtime</div>
            <p>Local-only runtime stack with custom boot logic and explicit file-based configuration.</p>
          </div>
          <div class="card">
            <div class="label">DNS</div>
            <p>Resolver and DNS runtime modules built from local HTML and runtime package files.</p>
          </div>
          <div class="card">
            <div class="label">Packages</div>
            <p>HTML packages are stored locally and loaded without GitHub runtime dependencies.</p>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>
EOF

cat > "$REPO_ROOT/runtime/dns/README.md" <<'EOF'
# DNS Runtime

This directory is the runtime hold for custom DNS server modules and local resolver packages.

The DNS service model is built around local runtime files and HTML package execution, not GitHub-managed dependencies.

## Structure

- `resolver.html` - local HTML-based runtime endpoint
- `records/` - DNS record definitions
- `zones/` - local zone files
EOF

cat > "$REPO_ROOT/runtime/dns/resolver.html" <<'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>KEDDEH DNS Resolver</title>
    <style>
      body {
        margin: 0;
        font-family: Arial, Helvetica, sans-serif;
        background: #0d1722;
        color: #e8f7ff;
      }
      .wrap {
        max-width: 760px;
        margin: 80px auto;
        background: #111f2b;
        border: 1px solid #24486b;
        border-radius: 12px;
        padding: 28px;
      }
      h1 { margin-top: 0; }
      code {
        background: #07111b;
        padding: 2px 6px;
        border-radius: 4px;
      }
    </style>
  </head>
  <body>
    <div class="wrap">
      <h1>KEDDEH DNS Resolver</h1>
      <p>Local custom DNS runtime module loaded from the repository's own runtime files.</p>
      <p><strong>Runtime mode:</strong> <code>local_custom</code></p>
      <p><strong>Dependency policy:</strong> <code>no_github_runtime_dependencies</code></p>
      <p><strong>Resolver root:</strong> <code>runtime/dns</code></p>
    </div>
  </body>
</html>
EOF

cat > "$REPO_ROOT/packages/html/README.md" <<'EOF'
# HTML Packages

This directory stores local HTML packages for runtime modules and service interfaces.

These packages are not pulled from GitHub-hosted dependency registries. They live in the repository and can be executed or served from a local runtime host.
EOF

cat > "$REPO_ROOT/packages/html/keddeh-runtime.html" <<'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>KEDDEH Runtime Package</title>
    <style>
      body {
        font-family: Arial, Helvetica, sans-serif;
        background: #0b1420;
        color: #ebf7ff;
        padding: 24px;
      }
      .box {
        max-width: 780px;
        margin: 0 auto;
        background: #102334;
        border: 1px solid #27547e;
        border-radius: 10px;
        padding: 22px;
      }
      code { background: #09151d; padding: 2px 6px; border-radius: 4px; }
    </style>
  </head>
  <body>
    <div class="box">
      <h1>KEDDEH Runtime Package</h1>
      <p>This package is part of the repository-owned runtime environment and is not linked to GitHub dependency managers.</p>
      <p>Runtime target: <code>codex</code></p>
      <p>Package source: <code>packages/html</code></p>
    </div>
  </body>
</html>
EOF

cat > "$REPO_ROOT/dns/zone.example" <<'EOF'
# Example local DNS zone definitions
# This file is intentionally runtime-local and can be extended by custom DNS packages.

example.com. IN A 192.168.1.10
api.example.com. IN A 192.168.1.11
www.example.com. IN CNAME example.com.
EOF

cat > "$REPO_ROOT/runtime/notes.txt" <<'EOF'
KEDDEH CUSTOM RUNTIME

- Repository: SERVERSPACE
- Branch: codex
- Runtime policy: local custom runtime only
- Dependency policy: NO GITHUB DEPENDENCIES
- Website root: sites/keddeh.com
- DNS root: runtime/dns
- HTML packages root: packages/html
EOF

echo "KEDDEH custom runtime initialized."
