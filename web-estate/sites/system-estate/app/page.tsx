"use client";

import {
  Archive,
  Boxes,
  Braces,
  Check,
  ChevronRight,
  CircuitBoard,
  Database,
  FlaskConical,
  Globe2,
  Network,
  PanelsTopLeft,
  Route,
  Send,
  Server,
  ShieldCheck,
  Workflow,
  X,
  type LucideIcon,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

type Domain = "all" | "experience" | "delivery" | "control" | "evidence";

type EstateSystem = {
  id: string;
  name: string;
  shortName: string;
  domain: Exclude<Domain, "all">;
  icon: LucideIcon;
  role: string;
  summary: string;
  owns: string[];
  excludes: string[];
  interfaces: string[];
  outputs: string[];
  state: "Executable" | "Contracted" | "Mapped";
  note?: string;
};

type Outcome = {
  id: string;
  eyebrow: string;
  title: string;
  description: string;
  systems: string[];
  steps: { system: string; action: string }[];
};

type WebMcpTool = {
  name: string;
  title?: string;
  description: string;
  inputSchema: Record<string, unknown>;
  annotations?: { readOnlyHint?: boolean; untrustedContentHint?: boolean };
  execute(input: unknown): unknown | Promise<unknown>;
};

type WebModelContext = {
  registerTool(tool: WebMcpTool, options?: { signal?: AbortSignal }): void | Promise<void>;
};

declare global {
  interface Document {
    readonly modelContext?: WebModelContext;
  }
}

const systems: EstateSystem[] = [
  {
    id: "foundry-fabric",
    name: "Foundry Fabric",
    shortName: "Fabric",
    domain: "control",
    icon: Network,
    role: "Estate orchestration",
    summary: "Composes independently addressable systems into one undertaking without erasing their ownership boundaries.",
    owns: ["Cross-system composition", "Interface contracts", "Delivery-path coordination"],
    excludes: ["Frontage design", "Website implementation"],
    interfaces: ["Every participating foundry", "KEX control plane"],
    outputs: ["System composition map", "Bounded delivery graph"],
    state: "Mapped",
  },
  {
    id: "frontage-foundry",
    name: "Frontage Foundry",
    shortName: "Frontage",
    domain: "experience",
    icon: PanelsTopLeft,
    role: "Market-facing experience",
    summary: "Defines what a visitor sees, understands and can do across a Keddeh market surface.",
    owns: ["Information architecture", "Interaction model", "Value articulation", "Accessibility intent"],
    excludes: ["Hosting infrastructure", "Domain routing", "Release mutation"],
    interfaces: ["Research Foundry", "Website Foundry", "HCI Foundry"],
    outputs: ["Frontage specification", "Interactive prototype", "Experience acceptance criteria"],
    state: "Executable",
  },
  {
    id: "website-foundry",
    name: "Website Foundry",
    shortName: "Website",
    domain: "delivery",
    icon: Globe2,
    role: "Deployable web system",
    summary: "Turns an approved frontage specification into a working web build with routes, assets and runtime behavior.",
    owns: ["Web implementation", "Responsive behavior", "Route structure", "Build output"],
    excludes: ["Market positioning", "DNS authority", "Publication approval"],
    interfaces: ["Frontage Foundry", "Server Foundry", "Publishing Foundry"],
    outputs: ["Deployable website", "Validated build", "Runtime manifest"],
    state: "Executable",
  },
  {
    id: "research-foundry",
    name: "Research Foundry",
    shortName: "Research",
    domain: "evidence",
    icon: FlaskConical,
    role: "Evidence and discovery",
    summary: "Tests propositions, maps user needs and separates sourced facts from inference before projection.",
    owns: ["Source analysis", "Capability discovery", "Claim classification"],
    excludes: ["Interface implementation", "Production release"],
    interfaces: ["Frontage Foundry", "KEX control plane", "File System Foundry"],
    outputs: ["Evidence map", "Research brief", "Unresolved-claim register"],
    state: "Mapped",
  },
  {
    id: "publishing-foundry",
    name: "Publishing Foundry",
    shortName: "Publishing",
    domain: "delivery",
    icon: Send,
    role: "Controlled release",
    summary: "Moves a versioned build through an authorized release gate and records the exact published state.",
    owns: ["Version promotion", "Audience gate", "Release record"],
    excludes: ["Source authorship", "DNS control", "Synthetic success receipts"],
    interfaces: ["Website Foundry", "Domain Foundry", "File System Foundry"],
    outputs: ["Saved version", "Deployment event", "Release lineage"],
    state: "Executable",
  },
  {
    id: "domain-foundry",
    name: "Domain Foundry",
    shortName: "Domain",
    domain: "delivery",
    icon: Route,
    role: "Address and routing authority",
    summary: "Binds approved public names to the correct deployment target without owning the website itself.",
    owns: ["Domain records", "Route policy", "TLS and edge binding"],
    excludes: ["Page content", "Application logic", "Release approval"],
    interfaces: ["Publishing Foundry", "Server Foundry", "Website Foundry"],
    outputs: ["Verified route", "Domain binding", "Routing evidence"],
    state: "Mapped",
  },
  {
    id: "server-foundry",
    name: "Server Foundry",
    shortName: "Server",
    domain: "control",
    icon: Server,
    role: "Runtime execution",
    summary: "Provides the serving environment, runtime constraints and operational signals used by deployed systems.",
    owns: ["Runtime service", "Origin execution", "Operational telemetry"],
    excludes: ["Experience design", "Domain ownership", "Evidence interpretation"],
    interfaces: ["Website Foundry", "Domain Foundry", "KEX control plane"],
    outputs: ["Serving runtime", "Health signals", "Execution logs"],
    state: "Mapped",
  },
  {
    id: "workspace-foundry",
    name: "Workspace Foundry",
    shortName: "Workspace",
    domain: "control",
    icon: Workflow,
    role: "Operational coordination",
    summary: "Holds typed working state, triggers and human-operable controls around an undertaking.",
    owns: ["Working state", "Trigger surfaces", "Operator views"],
    excludes: ["Public frontage", "Origin hosting", "Domain routing"],
    interfaces: ["Process Foundry", "File System Foundry", "Agentics Foundry"],
    outputs: ["Typed control surface", "State transition", "Operator record"],
    state: "Mapped",
  },
  {
    id: "file-system-foundry",
    name: "File System Foundry",
    shortName: "File system",
    domain: "evidence",
    icon: Archive,
    role: "Artifact and lineage custody",
    summary: "Preserves literal artifacts, hashes, parentage and destinations so claims can be traced to material evidence.",
    owns: ["Artifact identity", "Hash lineage", "Archive structure"],
    excludes: ["Claim acceptance", "Deployment execution", "Interface design"],
    interfaces: ["Research Foundry", "Publishing Foundry", "KEX control plane"],
    outputs: ["Source manifest", "Artifact ledger", "Collision-safe archive"],
    state: "Mapped",
  },
  {
    id: "kex-control-plane",
    name: "KEX Control Plane",
    shortName: "KEX",
    domain: "evidence",
    icon: CircuitBoard,
    role: "Execution and proof contract",
    summary: "Defines deterministic runtime gates for testing, configuration, mutation, writeback, proof commit and rehydration.",
    owns: ["Execution contract", "Proof-before-trust gates", "Deterministic replay model"],
    excludes: ["Proof of a deployment that did not run", "Authorship by implication", "A live endpoint by specification alone"],
    interfaces: ["Foundry Fabric", "Server Foundry", "File System Foundry"],
    outputs: ["Machine-readable control contract", "Proof schema", "Validation sequence"],
    state: "Contracted",
    note: "The supplied KEX v6 OpenAPI file specifies 26 operations. It is treated as a control contract, not evidence that its placeholder production server is live.",
  },
];

const outcomes: Outcome[] = [
  {
    id: "market-frontage",
    eyebrow: "Offering 01",
    title: "Market frontage",
    description: "A focused interactive surface that names the value, exposes the system behind it and gives visitors a clear next action.",
    systems: ["research-foundry", "frontage-foundry", "website-foundry", "publishing-foundry"],
    steps: [
      { system: "Research", action: "Verify claims and visitor need" },
      { system: "Frontage", action: "Define the experience contract" },
      { system: "Website", action: "Implement the working surface" },
      { system: "Publishing", action: "Release with an audience gate" },
    ],
  },
  {
    id: "operational-website",
    eyebrow: "Offering 02",
    title: "Operational website",
    description: "A deployable web implementation with accessible interactions, responsive behavior and an independently verifiable release path.",
    systems: ["website-foundry", "server-foundry", "publishing-foundry", "domain-foundry"],
    steps: [
      { system: "Website", action: "Build routes, assets and behavior" },
      { system: "Server", action: "Execute the validated build" },
      { system: "Publishing", action: "Promote the exact version" },
      { system: "Domain", action: "Bind the approved address" },
    ],
  },
  {
    id: "capability-map",
    eyebrow: "Offering 03",
    title: "Capability + evidence map",
    description: "A boundary-preserving model that links business outcomes to systems, interfaces, evidence states and the next executable step.",
    systems: ["foundry-fabric", "research-foundry", "file-system-foundry", "kex-control-plane"],
    steps: [
      { system: "Fabric", action: "Name every system boundary" },
      { system: "Research", action: "Classify the supporting evidence" },
      { system: "File system", action: "Bind claims to literal artifacts" },
      { system: "KEX", action: "Define the executable proof gates" },
    ],
  },
];

const domains: { id: Domain; label: string }[] = [
  { id: "all", label: "All systems" },
  { id: "experience", label: "Experience" },
  { id: "delivery", label: "Delivery" },
  { id: "control", label: "Control" },
  { id: "evidence", label: "Evidence" },
];

const waitForPaint = () =>
  new Promise<void>((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));

export default function Home() {
  const [domain, setDomain] = useState<Domain>("all");
  const [selectedId, setSelectedId] = useState("frontage-foundry");
  const [outcomeId, setOutcomeId] = useState("market-frontage");

  const filteredSystems = useMemo(
    () => systems.filter((system) => domain === "all" || system.domain === domain),
    [domain],
  );
  const selectedSystem = systems.find((system) => system.id === selectedId) ?? systems[1];
  const activeOutcome = outcomes.find((outcome) => outcome.id === outcomeId) ?? outcomes[0];

  const applyDomain = (nextDomain: Domain) => {
    setDomain(nextDomain);
    const visible = systems.filter((system) => nextDomain === "all" || system.domain === nextDomain);
    if (!visible.some((system) => system.id === selectedId)) setSelectedId(visible[0].id);
  };

  const applyOutcome = (nextOutcomeId: string) => {
    const outcome = outcomes.find((item) => item.id === nextOutcomeId);
    if (!outcome) return;
    setOutcomeId(outcome.id);
    setDomain("all");
    setSelectedId(outcome.systems[0]);
  };

  useEffect(() => {
    const context = document.modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    const report = (error: unknown) => console.warn("WebMCP registration failed", error);

    const registrations = [
      context.registerTool(
        {
          name: "select_estate_system",
          title: "Select estate system",
          description: "Select one named Keddeh estate system and show its ownership boundary, interfaces and outputs.",
          inputSchema: {
            type: "object",
            properties: { systemId: { type: "string", enum: systems.map((system) => system.id) } },
            required: ["systemId"],
            additionalProperties: false,
          },
          annotations: { readOnlyHint: false, untrustedContentHint: false },
          async execute(input) {
            const systemId = (input as { systemId?: unknown })?.systemId;
            const system = systems.find((item) => item.id === systemId);
            if (!system) throw new Error("Unknown systemId");
            setDomain("all");
            setSelectedId(system.id);
            await waitForPaint();
            return { selectedSystem: system.id, name: system.name, domain: system.domain };
          },
        },
        { signal: lifecycle.signal },
      ),
      context.registerTool(
        {
          name: "filter_estate_systems",
          title: "Filter estate systems",
          description: "Filter the visible Keddeh estate map by experience, delivery, control or evidence domain.",
          inputSchema: {
            type: "object",
            properties: { domain: { type: "string", enum: domains.map((item) => item.id) } },
            required: ["domain"],
            additionalProperties: false,
          },
          annotations: { readOnlyHint: false, untrustedContentHint: false },
          async execute(input) {
            const nextDomain = (input as { domain?: unknown })?.domain;
            if (!domains.some((item) => item.id === nextDomain)) throw new Error("Unknown domain");
            setDomain(nextDomain as Domain);
            const visible = systems.filter((system) => nextDomain === "all" || system.domain === nextDomain);
            setSelectedId((current) => visible.some((system) => system.id === current) ? current : visible[0].id);
            await waitForPaint();
            return {
              domain: nextDomain,
              visibleSystems: systems
                .filter((system) => nextDomain === "all" || system.domain === nextDomain)
                .map((system) => system.id),
            };
          },
        },
        { signal: lifecycle.signal },
      ),
    ];

    registrations.forEach((registration) => Promise.resolve(registration).catch(report));
    return () => lifecycle.abort();
  }, []);

  return (
    <>
      <a className="skip-link" href="#estate-explorer">Skip to system estate explorer</a>

      <header className="site-header">
        <a className="brand-lockup" href="#top" aria-label="Keddeh Systems home">
          <span className="brand-mark" aria-hidden="true"><span>K</span></span>
          <span>
            <strong>KEDDEH SYSTEMS</strong>
            <small>ENGINEER · AUTOMATE · SCALE</small>
          </span>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#offerings">Offerings</a>
          <a href="#estate-explorer">System estate</a>
          <a href="#delivery-path">Delivery path</a>
        </nav>
        <span className="private-badge"><ShieldCheck size={15} aria-hidden="true" /> Private prototype</span>
      </header>

      <main id="top">
        <section className="opening" aria-labelledby="opening-title">
          <div className="opening-copy">
            <p className="kicker"><span /> KEDDEH.COM / MARKET FRONTAGE</p>
            <h1 id="opening-title">One estate.<br /><em>Clear system boundaries.</em></h1>
            <p className="opening-lede">
              Explore how Keddeh Systems composes experience, delivery, control and evidence systems into a working undertaking—without collapsing one foundry into another.
            </p>
            <div className="opening-proof" aria-label="Prototype principles">
              <span><Check size={16} aria-hidden="true" /> Concrete outputs</span>
              <span><Check size={16} aria-hidden="true" /> Named ownership</span>
              <span><Check size={16} aria-hidden="true" /> Proof before trust</span>
            </div>
          </div>

          <div className="boundary-plate" aria-label="Frontage Foundry and Website Foundry boundary">
            <div className="plate-head">
              <span>BOUNDARY / 01</span>
              <span>SELECTED SYSTEM PAIR</span>
            </div>
            <div className="plate-systems">
              <button
                type="button"
                className="plate-system"
                onClick={() => {
                  setDomain("all");
                  setSelectedId("frontage-foundry");
                  document.getElementById("estate-explorer")?.scrollIntoView();
                }}
                aria-label="Inspect Frontage Foundry in the system estate"
              >
                <PanelsTopLeft size={23} aria-hidden="true" />
                <small>FRONTAGE FOUNDRY</small>
                <strong>Defines the experience</strong>
                <p>Message, structure, interaction and acceptance intent.</p>
                <span className="plate-action">Inspect boundary <ChevronRight size={15} aria-hidden="true" /></span>
              </button>
              <div className="boundary-seam" aria-hidden="true"><span>≠</span></div>
              <button
                type="button"
                className="plate-system"
                onClick={() => {
                  setDomain("all");
                  setSelectedId("website-foundry");
                  document.getElementById("estate-explorer")?.scrollIntoView();
                }}
                aria-label="Inspect Website Foundry in the system estate"
              >
                <Globe2 size={23} aria-hidden="true" />
                <small>WEBSITE FOUNDRY</small>
                <strong>Builds the web system</strong>
                <p>Routes, components, behavior and deployable output.</p>
                <span className="plate-action">Inspect boundary <ChevronRight size={15} aria-hidden="true" /></span>
              </button>
            </div>
            <p className="plate-rule"><Braces size={16} aria-hidden="true" /> They interface through a contract. Neither is an alias for the other.</p>
          </div>
        </section>

        <section className="offerings" id="offerings" aria-labelledby="offerings-title">
          <div className="section-heading">
            <div><p className="kicker">DELIVERY SLICES</p><h2 id="offerings-title">Choose the outcome</h2></div>
            <p>Each slice activates a different set of systems. Select one to trace its delivery path.</p>
          </div>
          <div className="offering-grid">
            {outcomes.map((outcome) => (
              <button
                key={outcome.id}
                type="button"
                className="offering-card"
                aria-pressed={outcome.id === outcomeId}
                onClick={() => applyOutcome(outcome.id)}
              >
                <span>{outcome.eyebrow}</span>
                <strong>{outcome.title}</strong>
                <p>{outcome.description}</p>
                <span className="card-action">Trace this slice <ChevronRight size={17} aria-hidden="true" /></span>
              </button>
            ))}
          </div>
        </section>

        <section className="estate" id="estate-explorer" aria-labelledby="estate-title">
          <div className="section-heading estate-heading">
            <div><p className="kicker">SELECTED ESTATE MAP</p><h2 id="estate-title">Inspect the system, not just the label</h2></div>
            <p>Every system names what it owns, what it does not own, and the interfaces needed to produce a deliverable.</p>
          </div>

          <div className="domain-filter" role="group" aria-label="Filter systems by domain">
            {domains.map((item) => (
              <button
                type="button"
                key={item.id}
                aria-pressed={domain === item.id}
                onClick={() => applyDomain(item.id)}
              >{item.label}</button>
            ))}
          </div>

          <div className="estate-workbench">
            <div className="system-list" aria-label={`${filteredSystems.length} visible systems`}>
              {filteredSystems.map((system) => {
                const Icon = system.icon;
                const selected = system.id === selectedId;
                const active = activeOutcome.systems.includes(system.id);
                return (
                  <button
                    key={system.id}
                    type="button"
                    className="system-card"
                    data-domain={system.domain}
                    data-outcome={active ? "active" : "inactive"}
                    aria-pressed={selected}
                    onClick={() => setSelectedId(system.id)}
                    aria-label={`Inspect ${system.name}. ${system.role}.`}
                  >
                    <span className="system-icon"><Icon size={19} aria-hidden="true" /></span>
                    <span className="system-copy"><strong>{system.name}</strong><small>{system.role}</small></span>
                    <span className="system-state">{system.state}</span>
                    <ChevronRight className="system-chevron" size={18} aria-hidden="true" />
                  </button>
                );
              })}
            </div>

            <article className="system-detail" aria-live="polite" aria-labelledby="selected-system-name">
              <div className="detail-topline">
                <span>{selectedSystem.domain.toUpperCase()} SYSTEM</span>
                <span className={`state-pill state-${selectedSystem.state.toLowerCase()}`}>{selectedSystem.state}</span>
              </div>
              <h3 id="selected-system-name">{selectedSystem.name}</h3>
              <p className="detail-role">{selectedSystem.role}</p>
              <p className="detail-summary">{selectedSystem.summary}</p>

              <div className="boundary-grid">
                <div className="owns">
                  <h4><Check size={16} aria-hidden="true" /> Owns</h4>
                  <ul>{selectedSystem.owns.map((item) => <li key={item}>{item}</li>)}</ul>
                </div>
                <div className="excludes">
                  <h4><X size={16} aria-hidden="true" /> Does not own</h4>
                  <ul>{selectedSystem.excludes.map((item) => <li key={item}>{item}</li>)}</ul>
                </div>
              </div>

              <div className="detail-columns">
                <div><h4>Interfaces with</h4><p>{selectedSystem.interfaces.join(" · ")}</p></div>
                <div><h4>Concrete outputs</h4><p>{selectedSystem.outputs.join(" · ")}</p></div>
              </div>
              {selectedSystem.note && <p className="evidence-note"><ShieldCheck size={16} aria-hidden="true" /> {selectedSystem.note}</p>}
            </article>
          </div>
        </section>

        <section className="delivery" id="delivery-path" aria-labelledby="delivery-title">
          <div className="delivery-intro">
            <p className="kicker">NEXT EXECUTABLE DELIVERY STEP</p>
            <h2 id="delivery-title">Trace: {activeOutcome.title}</h2>
            <p>{activeOutcome.description}</p>
            <p className="delivery-rule"><ShieldCheck size={17} aria-hidden="true" /> A receipt is emitted by execution and independent readback. It is never added by hand.</p>
          </div>
          <ol className="delivery-steps">
            {activeOutcome.steps.map((step, index) => (
              <li key={`${step.system}-${step.action}`}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div><strong>{step.system}</strong><p>{step.action}</p></div>
              </li>
            ))}
          </ol>
        </section>

        <section className="execution-band" aria-label="KEX execution contract summary">
          <div><Boxes size={22} aria-hidden="true" /><span><small>KEX CONTROL CONTRACT / V6</small><strong>26 specified operations</strong></span></div>
          <div className="execution-flow" aria-label="Execution sequence">
            {["Resolve", "Mutate", "Write back", "Proof commit", "Rehydrate"].map((item, index) => (
              <span key={item}>{index > 0 && <ChevronRight size={14} aria-hidden="true" />}{item}</span>
            ))}
          </div>
          <p><Database size={17} aria-hidden="true" /> Specification is not deployment evidence.</p>
        </section>
      </main>

      <footer>
        <div className="brand-lockup footer-brand">
          <span className="brand-mark" aria-hidden="true"><span>K</span></span>
          <span><strong>KEDDEH SYSTEMS</strong><small>ENGINEER · AUTOMATE · SCALE</small></span>
        </div>
        <p>Private market-frontage prototype · System boundaries preserved</p>
        <p className="source-scope">Source scope: Keddeh Systems vocabulary and supplied KEX contract. Recovered CasePath page design and copy were not used.</p>
      </footer>
    </>
  );
}
