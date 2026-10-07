# Bound personal Site development

Target: `appgprj_6ab6a8a830d8819184bb86039a5ca309`, Aboudy Keddeh — Systems Architect.
Existing source: `988804e539ae9b08f8741430643f7985d203d410`, imported through owner
SERVERSPACE revision `735f5c4924ba46d7f271110e6afb1ff78ca61387`.
The original `SOURCE.json` remains historical custody evidence. `.openai/hosting.json`
retains the exact project ID and static hosting contract. Recorded custom audience
revision 1 is preserved; native current permissions and deployment have not been
queried because the integration is not exposed in this session.

## Build and review

```sh
python3 build.py
npm ci --ignore-scripts --no-audit --no-fund
python3 -B -m unittest discover -s tests -p test_runtime.py -v
CHROMIUM_PATH=/usr/bin/chromium npm run test:dom
python3 runtime/server.py --database /private-runtime/enquiries.sqlite --port 18766
```

Python 3.12+ and OpenSSL are used for qualification. The Node dependency lock
pins Playwright 1.55.1 and axe-core 4.10.3. In this cloud host, the SUID sandbox
helper is unavailable; only local first-party fixture qualification uses the
explicit `SITE_BROWSER_SANDBOX=0` profile. It does not establish browser isolation.
No public preview or production endpoint is created by these commands.

Run `npm run test:engine` for compiler/assembler/loader conformance and rejection
checks, and `npm run test:wrapper` for ES5 syntax and the 64 KiB per-route transfer
budget. `npm run test:runtime` exercises all fifteen Python runtime/resource/
failover tests. The browser runner uses the same engine package through
`KEXSite.runPackage`; no parallel page-specific compiler is created.

`--enable-capture` activates the loopback review form. Use fixture data for tests;
owner approval of notice, operator handling and storage is required for production
activation. The database must remain outside the source tree. No Google OAuth,
Drive binding, email delivery or production tenant membership is fabricated.
Optional `--tls-cert` and `--tls-key` enable TLS with minimum version 1.2 and a
Secure session cookie. Keys must remain private and outside Git. The TLS test
uses an explicitly trusted fixture certificate and also checks rejection by a
client that has not trusted it; verification is not disabled. This is distinct
from publicly trusted certificate issuance or native Site HTTPS publication.

## Top-down pages and interactions

The home page leads to Work, Approach, Evidence, Compatibility, Foundry and
Contact. Work links BRAINK, IL-LLM, KEX, KEX DNA and Engines. CasePath is a bounded
internal brief; its historical external address is no longer represented as
verified availability. Privacy and Contact are linked throughout the build.
Fourteen routes have substantive goal, responsibility, evidence and next-step
content. Each route is generated from reviewable `content.json` by `build.py`.
The claim register includes each section verbatim. The interaction register
includes every anchor, button, input, select and textarea with its DOM attributes
and required name, keyboard access, action boundary and readback.

Actual DOM tests navigate every local anchor and test all route destinations and
fragments. Mailto and GitHub actions are inspected and activated with external
effects prevented; remote destinations are not declared live. Tests exercise all
form fields, consent, validation, pending submission, retained-data failure,
retry and persisted fixture confirmation. The wrapper tests mode selection,
bounded jobs, queue rejection, keyboard/remote navigation and degraded features.
Automated axe checks cover every page. Manual screen-reader and physical TV,
Android and 32-bit hardware assessments remain distinct outstanding checks.

## HTML KEX wrapper and original engines

`KEXSite` is an ES5-compatible Site adapter with no Worker, BigInt, WebAssembly or
SharedArrayBuffer requirement. It does not claim to be the complete owner KEX
virtual machine or R36 multiplexer. `enqueue` admits at most eight jobs; each job
must return `true` when complete and has at most 512 steps. Lightweight slices
have a two-millisecond target budget; standard slices four. A single callback
cannot be pre-empted, so every supplied step must itself be bounded. Hidden pages
pause work. No boot loop, mesh polling, owner shell or private resident workbook
is automatically exposed to portfolio visitors.

The original HTML carrier, terminal, resident VM and R36 archive are indexed by
exact SHA-256 in `research/kex-artifact-index.json`. Static observations identify
userspace/mesh and software ISA markers; those artifacts were not executed by
this Site build. Mounting a host or multiplexer requires an admitted adapter,
separate owner authority and target-specific observations. Supporting 32-bit
processors is an explicit owner requirement, not a result of emulating a narrow
desktop viewport or removing modern browser globals.

`kex-engine.js` adapts the resident P03 chain into a bounded ES5 package. Its
conformance fixture preserves the exact original compiler script and source
custody hash. KEX instruction lines are the admitted frontend in this portable
package; other source languages require separately qualified frontends. Opcode
and word format match the owner model. Numerical operands exceeding 24 bits are
rejected rather than silently truncated. Loader input is bounded to 256 words
and validated before dispatch. Each operation requires an explicit handler;
host actuation is not granted by loading a package. The FNV-compatible checksum
is an integrity check, not an authentication or persistence mechanism.

## Foundry and namespace requirements

Two address routes are preserved: public-domain registration and owner-operated
namespace/authoritative service. `VisitUsAt.<full-business-name>`,
`TellMeAbout.<name>`, `WhatIs.<name>` and `WhoIs.<name>` are owner-proposed patterns.
The complete display name and wire-format encoding are separate contracts.
Resolver discovery, client configuration, delegation and certificate trust must
be documented for each route. Namespace control is not asserted as proof of
exclusive trademark rights or inclusion in the public DNS root.

The sector-foundry flow covers template selection, customer/admin separation,
Google identity, separately consented Drive/VFS access, project-scoped cache and
cookies, admitted nodes, lineage and publishing readback. Its enquiry topic is
working locally; the enterprise provisioning adapters remain to be implemented
and qualified. The Google primary client documentation is retrieved and hashed
in the source register. Cryptography superiority claims require an exact
protocol, threat model, test vectors, comparative measurements and independent
analysis; no unverified superiority claim is placed in the portfolio.

## Attribution and release boundaries

Original portfolio design/content retains `web-estate/LICENSE.md`; no new public
licence is invented. The bounded interest/record modules are reused from the
owner's queue implementation revision `cf99a2191db4d5a1708972e2ab41abb6b90220d7`.
The only interest-module change adds the website-foundry topic. Primary WCAG and
GOV.UK sources inform labels, visible focus, error summaries and inline errors.
Their copied research text is reference material, not authored by this project.

Git delivery, static build, local runtime/TLS, independently assessed release and
native publication are separate statuses. Native publish must use this exact
Site, verify its audience, build/router/DOM checks and obtain actual deployment
readback. A Git branch or passing fixture test is not a published Site.

## Physical memory and failover requirements

The owner confirmed **100 TB physical RAM per server**, not a sparse VFS capacity.
`resource_grid.py` validates parent/service allocations, separates observed
capacity from provisioning and maps large extents into bounded process windows.
It is allocation planning, not a kernel quota enforcer or physical resource
provisioner. The development container exposes a 32 GiB cgroup limit; this is
not a 100 TB server. Host procurement/admission remains an external dependency.

`failover.py` supplies read-only templates for DNS, namespace, VFS, website and
cache. Plans reject stale/unhealthy/unadmitted nodes, source/generation mismatch,
shared failure domains and missing previous-writer fencing. Caller-supplied
observations do not themselves establish cryptographic identity or independent
assessment. No server promotion is executed by the planner.

The owner specifies transmission, TOT, failover and 0.297 resonance as persistence
mechanisms. Their authoritative protocol and recovery tests must be mapped before
claiming all-replica loss recovery. The indexed terminal's four `0.297` matches
occur in `6.0.297` version identifiers; that source inspection does not establish
a resonance persistence implementation. In-memory VFS replicas can preserve
continuity across covered node failures; source lineage is not by itself proof
of survival after every copy of state loses memory.
