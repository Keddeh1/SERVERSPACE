# Public source gate

`Keddeh1/SERVERSPACE` is public. A website may enter `web-estate/sites/` only when all of the following are true:

- the source is obtained from an owner-controlled Sites/Git repository, not scraped from a public URL;
- credentials, cookies, bearer values, private keys, environment values, personal allowlists and database state are absent;
- owner-only control paths and security-relevant runtime material have been reviewed for public disclosure;
- generated artifacts are either reproducible or explicitly identified;
- the native source revision and deployment binding are recorded;
- the import is isolated in its own commit and reviewed before merge.

A failing site remains in the registry with `source_import_status: BLOCKED`; its source is not weakened, redacted ad hoc, or silently omitted while claiming a complete import.
