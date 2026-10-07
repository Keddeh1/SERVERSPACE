# Keddeh APEX website design and intake workflow

Status: INTEGRATION_CANDIDATE  
Version: 1.0.0  
KEX seed: 9B33129A9B59C739ED67D85679B9ACD8E0FD28711492AD10C2CA2BCBAE316DB1  
Created: 2026-10-07T02:15:00Z

## What APEX means here

**APEX is a Keddeh Systems delivery workflow, not an external standard, certification or compliance mark.** It operationalises current Human–Computer Interaction, user experience, user-interface, accessibility, privacy, consumer-protection, performance and experimental-design sources listed in the source register.

A product may be described as **evaluated against** a named source only when its evidence record exists. It must not be described as ISO certified, ISO compliant, Web Content Accessibility Guidelines conformant, or legally compliant merely because this workflow was followed.

## Preserved system boundaries

| System | Accountable result | Must not absorb |
| --- | --- | --- |
| Frontage Foundry | market proposition, information architecture, customer journey, content hierarchy, art direction and conversion hypothesis | implementation, deployment or domain authority |
| Website Foundry | semantic implementation, responsive behaviour, forms, instrumentation, automated tests, accessibility and performance engineering | proposition ownership or publication authority |
| Publishing Foundry | promotion of an exact tested build and deployment record | source design or domain ownership |
| Domain Foundry | domain and route binding | application runtime |
| Server Foundry | runtime, storage, submission processing, security and operational health | public claims or visual design |
| Foundry Fabric | coordinates contracts, evidence and gates across systems | ownership of any bounded system |

A front-end appearance can change without collapsing these authorities. Every handoff names the source commit, built artifact, test evidence, deployment version and independent readback separately.

## Definition of elite

Elite means that representative people can complete the intended task accurately, efficiently and with confidence in their real context of use. It does not mean visual excess, forced urgency, maximal animation or a higher raw form-submit count.

A release is judged across five outcomes:

1. **Task success** — the right visitor can understand the offer, decide whether it fits and complete the next useful action.
2. **Trust** — material claims, prices, limitations, response times and evidence are accurate and reviewable.
3. **Inclusion** — the complete journey works with keyboard input, assistive technology, zoom, reflow, reduced motion and constrained networks.
4. **Operational quality** — submissions are recoverable, traceable, secure and handed to a responsible human or system.
5. **Sustainable conversion** — qualified completions improve without degrading accessibility, privacy, complaint rate, lead quality or downstream fulfilment.

## The APEX cycle

### Gate 0 — authority, risk and evidence boundary

Required inputs:

- exact site and route scope;
- Frontage Foundry and Website Foundry owners;
- audience and jurisdiction;
- public, private or owner-admin access class;
- source ownership and asset rights;
- claim register with evidence owner and expiry/review date;
- personal-information classes and receiving system;
- safety, legal, financial or other high-impact risk.

Block release when ownership is unresolved, a material claim lacks evidence, a secret is present in client source, or a collection destination is not approved.

### Gate 1 — context of use

Create a context record before producing polished screens. It identifies:

- primary and secondary user groups;
- their goal and the whole problem surrounding it;
- prior knowledge, language and decision anxiety;
- devices, viewport ranges, input modes and network constraints;
- assistive technologies and access needs;
- physical and social environment;
- failure consequences and human support route;
- existing evidence from support requests, analytics, interviews or usability sessions.

State assumptions as UNTESTED. Do not invent research findings, personas or customer quotes.

### Gate 2 — service and task model

Define one primary visitor task per route. For every offering, record:

- customer problem and observable outcome;
- included capability, exclusions and prerequisites;
- proof supporting each performance or benefit claim;
- price or the reason price cannot yet be stated;
- next action, response owner and expected response window;
- alternate route when the offering is unsuitable.

The frontage must explain the system estate without making every system look like one product. A capability may be shared; its owner remains explicit.

### Gate 3 — customer-intake architecture

Design the intake as a service, not a contact-data trap.

1. Explain what the intake does, who it is for, what the user needs and how long it is expected to take.
2. Ask suitability or routing questions before requesting identity and contact details.
3. Ask one coherent question or tightly related group per step.
4. For every collected field, record purpose, necessity, sensitivity, retention class and expected disclosure.
5. Provide a collection notice at or before collection, with identity, purpose, consequences of not providing data, usual disclosures, privacy-policy access and likely overseas disclosure.
6. Keep marketing permission separate, optional and unselected by default. Record when and how consent was given.
7. Preserve answers during validation. Put a linked error summary at the top and a matching error beside each invalid answer.
8. Let the user review and change answers before final submission.
9. Confirm receipt with a reference, next step, response window, edit/correction route and human contact.
10. Provide a non-digital or human-assisted route when the context requires one.

Never request government identifiers, payment data, health information, legal evidence or other sensitive material through a generic enquiry form.

### Gate 4 — art direction and creative production

Art is part of the information system. Every visual has a job.

The art-direction brief must contain:

- brand invariants, including the exact system name and approved Keddeh Systems language;
- the intended perception and user decision the art supports;
- at least two meaningfully different concepts before selection;
- composition rules for small, medium and large viewports;
- colour, typography, density, rhythm, icon and motion rules;
- a provenance record for every image, illustration, icon, font, audio and video asset;
- licence, consent or model-release state where applicable;
- classification as informative, functional, text-equivalent, complex or decorative;
- text alternative, caption or long-description strategy;
- focal point and crop-safe coordinates for responsive variants;
- intrinsic dimensions and encoded-size budget;
- reduced-motion behaviour and a non-motion equivalent;
- evidence for any visual that implies a product result, customer, location or capability.

Generated or synthetic visuals must not be presented as documentary proof. Decorative images use an empty text alternative. Informative images require an equivalent that communicates their purpose in context.

### Gate 5 — information and interaction design

Produce, in order:

1. task flow and failure flow;
2. content hierarchy and claim/evidence matrix;
3. low-fidelity interaction prototype;
4. visual system and responsive compositions;
5. coded semantic prototype;
6. complete intake, confirmation and recovery states.

Use familiar controls and native semantics before custom widgets. Every state must remain understandable without colour alone. Focus order follows task order. Touch and pointer targets, keyboard operation, visible focus, labels, instructions, status messages and error recovery are tested as behaviours, not inferred from screenshots.

### Gate 6 — evaluation with people

Run formative evaluation with representative users early enough to change the design. Cover the primary task, at least one recovery path and the complete intake. Include people with disabilities and assistive-technology users when the product context calls for them.

Record:

- scenario and success definition;
- participant characteristics relevant to the context, without unnecessary identity data;
- completion, error and recovery observations;
- time on task where meaningful;
- confidence or satisfaction measure and method;
- severity, evidence and disposition of each finding.

Do not report a success percentage without the numerator, denominator and sampling context.

### Gate 7 — implementation quality

Website Foundry produces the deployable implementation and verifies:

- semantic document structure and native control use;
- responsive layout from 320 CSS pixels through large desktop without loss of content or operation;
- keyboard-only completion and logical focus;
- screen-reader names, descriptions, errors and status changes;
- 200 percent zoom and 400 percent reflow where applicable;
- reduced motion and animation controls;
- meaningful alternatives for media;
- field autocomplete and input purpose where applicable;
- no secrets, private allowlists or production credentials in client assets;
- input validation on both client and server;
- rate limiting, abuse handling and safe file-upload controls where applicable;
- Core Web Vitals field targets at the 75th percentile: Largest Contentful Paint at or below 2.5 seconds, Interaction to Next Paint at or below 200 milliseconds, and Cumulative Layout Shift at or below 0.1.

Laboratory performance results are release signals, not substitutes for field measurement.

### Gate 8 — accessibility evaluation

Set the intended target, normally Web Content Accessibility Guidelines 2.2 Level AA, before testing.

Use the current Website Accessibility Conformance Evaluation Methodology 2.0 process to:

- define the product boundary and accessibility-support baseline;
- identify common views, technologies and essential functionality;
- include complete processes;
- select structured and random samples when the product is large;
- evaluate and report every sampled state.

Automated checks are necessary but not sufficient. A sample-based evaluation must not be represented as a whole-site conformance claim.

For owner authoring interfaces, also evaluate whether the tool is accessible to authors and whether it enables, supports and promotes accessible output, using Authoring Tool Accessibility Guidelines 2.0 as the reference.

### Gate 9 — conversion experiment

Experiment only after the baseline journey is usable and truthful.

Pre-register:

- user problem and causal hypothesis;
- one primary metric;
- segment and allocation unit;
- control and treatment;
- minimum detectable effect or practically meaningful effect;
- significance level, power assumption and sample-size method;
- minimum runtime and stopping rule;
- accessibility, privacy, complaint, lead-quality and fulfilment guardrails;
- instrumentation version and data dictionary;
- decision rule for adopt, reject, extend or inconclusive.

Randomise at the declared unit. Do not stop when a preferred result first appears. Do not run simultaneous experiments that contaminate the same decision unless their interaction is part of the design. Correct for multiple comparisons when testing multiple outcomes or variants.

A conversion win is invalid when a guardrail materially worsens.

### Gate 10 — promotion and outside-in readback

Promotion requires:

- exact source commit;
- reproducible build result;
- completed control matrix;
- open blocker count of zero;
- accessibility and usability evaluation evidence;
- approved claims and asset rights;
- submission endpoint test including failure recovery;
- saved deployment version;
- deployment result;
- outside-in route, form, asset, header and accessibility readback.

Publishing Foundry promotes the build. It does not create missing evidence.

## Customer-intake measurement

Use a qualified journey model:

- eligible starts;
- scope completion;
- contact-step arrival;
- valid review arrival;
- confirmed submissions;
- qualified submissions accepted downstream;
- time to first human response;
- resolution or booked next action.

Also measure step exits, validation errors, recovery, duplicate submissions, abandoned uploads, spam, complaints and human handoff. Raw submit rate alone is not an elite conversion measure.

Do not collect analytics identifiers or marketing consent merely because they may be useful. Each event and field requires a documented purpose and retention rule.

## Prohibited conversion patterns

The following are release blockers:

- preselected marketing consent;
- fabricated scarcity, urgency, testimonials or results;
- hidden material price, fee, eligibility or limitation information;
- confirmshaming;
- an easy opt-in paired with an obstructed opt-out;
- disguised advertising or navigation;
- changing answers or adding extras without explicit user action;
- repeated prompts after refusal;
- inaccessible alternatives presented as optional support;
- claiming certification or conformance without the required assessment evidence.

## Evidence states

Use only: OBSERVED, SOURCE_VERIFIED, TESTED, INFERRED, UNTESTED, FAILED, UNSUPPORTED and SUPERSEDED.

A passing schema validation proves contract structure, not the real-world usability, accessibility, legal compliance or commercial performance of a website.
