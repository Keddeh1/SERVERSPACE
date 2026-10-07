"""Deterministic static build of the bound personal Site; no native publication."""
from pathlib import Path
import html
import json

root = Path(__file__).resolve().parent
pages = json.loads((root / 'content.json').read_text())
esc = html.escape
navigation = [('/', 'Home'), ('/work/', 'Work'), ('/approach/', 'Approach'),
              ('/evidence/', 'Evidence'), ('/foundry/', 'Foundry'), ('/compatibility/', 'Compatibility'), ('/contact/', 'Contact')]
claims, interactions = [], []
source_links = [('source-portfolio', 'Imported owner portfolio', 'https://github.com/Keddeh1/SERVERSPACE/tree/735f5c4924ba46d7f271110e6afb1ff78ca61387/web-estate/sites/aboudy-keddeh'),
                ('source-queue', 'Governed queue source and tests', 'https://github.com/Keddeh1/SYSTEMS-SERVICES-FOR-DEPLOYMENT-QUEUE/tree/cf99a2191db4d5a1708972e2ab41abb6b90220d7'),
                ('source-namespace', 'Namespace source and implementation scope', 'https://github.com/Keddeh1/KEDDEH-SOVEREIGN-NAMESPACE-RUNTIME/tree/3300e02e4c025a167fde414263f5344c5eecd70d')]
form = '''<form id="interest-form" class="form" novalidate>
<div id="form-errors" class="error" tabindex="-1" hidden><h2>Please check your enquiry</h2><ul></ul></div>
<div class="field"><label for="name">Name (required)</label><input id="name" name="name" autocomplete="name" maxlength="120" required></div>
<div class="field"><label for="email">Email (required)</label><input id="email" name="email" type="email" autocomplete="email" maxlength="254" required></div>
<div class="field"><label for="organisation">Organisation (optional)</label><input id="organisation" name="organisation" autocomplete="organization" maxlength="160"></div>
<div class="field"><label for="use_case">Enquiry topic (required)</label><select id="use_case" name="use_case"><option value="deployment-evidence">Deployment evidence</option><option value="runtime-integration">Runtime integration</option><option value="governed-research">Governed research</option><option value="website-foundry">Website foundry</option><option value="other">Other</option></select></div>
<div class="field"><label for="message">Message (optional)</label><p id="message-hint" class="hint">Up to 2,000 characters. Do not include secrets or confidential documents.</p><textarea id="message" name="message" rows="5" maxlength="2000" aria-describedby="message-hint"></textarea></div>
<div class="field check"><input id="privacy_consent" name="privacy_consent" type="checkbox" required><label for="privacy_consent">I have read the <a href="/privacy/">enquiry privacy notice</a> (required).</label></div>
<div class="field check"><input id="marketing_consent" name="marketing_consent" type="checkbox"><label for="marketing_consent">I would like occasional relevant updates (optional).</label></div>
<p id="capture-status" class="status" role="status">Checking enquiry availability…</p>
<button type="submit" class="button" disabled>Register interest</button>
</form><div id="form-success" class="success" tabindex="-1" hidden></div>
<noscript><p>The form needs JavaScript. You can <a href="mailto:aboudy@keddeh.com">send an email enquiry</a> instead.</p></noscript>'''
for route, page in pages.items():
    nav = ''.join('<a href="' + url + '"' + (' aria-current="page"' if route == url else '') + '>' + label + '</a>' for url, label in navigation)
    content = ''
    for key, value in [('hero-heading', page['heading']), ('hero-intro', page['intro'])]:
        claims.append({'id': route + '#' + key, 'statement': value, 'type': 'positioning-or-architecture-scope', 'attribution': ['/evidence/', 'owner-directed-build'], 'production_verified': False})
    for index, (title, text) in enumerate(page['sections'], 1):
        identity = 'section-' + str(index)
        content += '<section class="section prose" aria-labelledby="' + identity + '"><h2 id="' + identity + '">' + esc(title) + '</h2><p>' + esc(text) + '</p></section>'
        claims.append({'id': route + '#' + identity, 'statement': text, 'type': 'architecture-direction-or-review-guidance',
                       'attribution': ['/evidence/', 'owner-directed-build'], 'production_verified': False})
    cards = ''
    for index, (title, url, text) in enumerate(page.get('cards', []), 1):
        identity = 'card-' + str(index)
        cards += '<article class="card" id="' + identity + '"><h2><a href="' + url + '">' + esc(title) + '</a></h2><p>' + esc(text) + '</p></article>'
        claims.append({'id': route + '#' + identity, 'statement': text, 'type': 'navigation-purpose',
                       'attribution': ['/evidence/', 'owner-directed-build'], 'production_verified': False})
    extra = ''
    if route == '/evidence/':
        extra = '<section class="section prose"><h2>Exact source references</h2><ul>' + ''.join('<li id="' + identity + '"><a href="' + url + '">' + label + '</a></li>' for identity, label, url in source_links) + '</ul></section>'
    if route == '/contact/':
        extra = '<section class="section prose" aria-labelledby="enquiry-title"><h2 id="enquiry-title">Register your interest</h2>' + form + '<p><a href="mailto:aboudy@keddeh.com">Email aboudy@keddeh.com</a></p></section>'
    if route == '/compatibility/':
        extra = '<section class="section prose"><h2>Display and compute preference</h2><label for="kex-mode">KEX wrapper mode</label><select id="kex-mode"><option value="auto">Automatic</option><option value="light">Lightweight</option><option value="standard">Standard</option></select><p id="kex-status" role="status">The page remains readable without the wrapper.</p></section>'
    cta = '' if route == '/contact/' else '<aside class="cta" aria-label="Next step"><h2>Define a useful next step.</h2><p>Discuss your requirements and the evidence needed for a bounded evaluation.</p><a class="button" href="/contact/">Discuss your project</a></aside>'
    markup = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#07131e"><meta name="description" content="''' + esc(page['intro'], quote=True) + '''"><title>''' + esc(page['title']) + '''</title><link rel="stylesheet" href="/assets/site.css"><script defer src="/assets/kex-engine.js"></script><script defer src="/assets/kex-wrapper.js"></script><script defer src="/assets/contact.js"></script></head><body id="top"><a class="skip" href="#main">Skip to content</a><header><div class="shell topbar"><a class="identity" href="/" aria-label="Aboudy Keddeh, home"><span class="mark" aria-hidden="true">K</span>Aboudy Keddeh</a><nav aria-label="Main navigation">''' + nav + '''</nav></div></header><main id="main" tabindex="-1"><div class="shell"><div class="crumb"><a href="/">Home</a> / ''' + esc(page['title'].split(' — ')[0]) + '''</div><section class="page-hero"><p class="eyebrow">''' + esc(page['eyebrow']) + '''</p><h1 id="hero-heading">''' + esc(page['heading']) + '''</h1><p class="lede" id="hero-intro">''' + esc(page['intro']) + '''</p></section><div class="grid">''' + cards + '''</div>''' + content + extra + '<p class="prose"><a href="/evidence/">Read the sources and capability scope</a></p>' + cta + '''</div></main><footer><div class="shell"><p>Aboudy Keddeh · Systems Architect</p><nav class="footer-links" aria-label="Footer"><a href="/work/">Work</a><a href="/work/casepath/">CasePath direction</a><a href="/evidence/">Sources and scope</a><a href="/privacy/">Privacy</a><a href="/contact/">Contact</a><a href="#top">Back to top</a></nav></div></footer></body></html>'''
    destination = root / 'dist' / route.strip('/') / 'index.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(markup)
    from html.parser import HTMLParser
    class Inventory(HTMLParser):
        def handle_starttag(self, tag, attributes):
            attrs = dict(attributes)
            if tag in ('a', 'button', 'select', 'input', 'textarea'):
                interactions.append({'route': route, 'element': tag, 'attributes': attrs,
                    'requirements': ['accessible name', 'keyboard access', 'bounded action', 'destination or state readback'],
                    'attribution': ['wcag-labels', 'wcag-focus', 'wcag-errors', 'govuk-errors']})
    Inventory().feed(markup)
for claim in claims:
    claim['review_status'] = 'authored_for_owner_review; independent_assessment_unset'
(root / 'research/claim-register.json').write_text(json.dumps(claims, ensure_ascii=False, indent=2) + '\n')
(root / 'research/interaction-register.json').write_text(json.dumps(interactions, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'routes': len(pages), 'claim_sections': len(claims), 'interactive_elements': len(interactions), 'native_publication': False}))
