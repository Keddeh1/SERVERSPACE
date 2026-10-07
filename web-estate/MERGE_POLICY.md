# Boundary-preserving merge policy

The estate is one GitHub control plane, not one undifferentiated application.

## Paths

- `sites/<site>/` contains one independently buildable website.
- `packages/<capability>/` is permitted only for a tested shared capability with an explicit consumer list.
- `contracts/` contains interfaces between distinct systems.
- `registry/` contains source, access, deployment and public-readback bindings.
- `external/` records owned or related surfaces whose source authority is unresolved.

## Promotion sequence

`captured source → source verified → tests reproduced → import candidate → reviewed pull request → accepted estate module → deployable release`

## Non-collapse rules

- Frontage Foundry and Website Foundry remain distinct.
- BRAINK, IL-LLM, KEX, KEX DNA, engines, products and foundries retain their own identities.
- A route inside KEDDEH.COM is not declared a standalone website.
- A database release pointer is not a native Sites deployment.
- A deployment receipt is not independent assessment.
- A public-page readback is not source provenance.

## First merge gate

No cross-site code is extracted until every imported site builds from its bounded path and its rendered routes are compared against the source deployment. Shared packages are introduced in later pull requests, never during source capture.
