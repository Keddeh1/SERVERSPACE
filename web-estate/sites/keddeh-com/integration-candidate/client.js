'use strict';
// Public customer journeys never load owner actuator credentials.
for (const link of document.querySelectorAll('header nav a, .mobile-nav a')) {
  const path = new URL(link.href).pathname;
  if (path === location.pathname || (path !== '/' && location.pathname.startsWith(path + '/'))) link.setAttribute('aria-current', path === location.pathname ? 'page' : 'location');
}
const menu = document.querySelector('.mobile-nav');
if (menu) menu.addEventListener('keydown', event => {
  if (event.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); }
});
document.querySelector('.skip')?.addEventListener('click', () => document.querySelector('main').focus());
async function requestJSON(url, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(url, {...options, signal: controller.signal});
    let data;
    try { data = await response.json(); }
    catch { throw new Error('The service returned an unreadable response. Please retry.'); }
    if (!response.ok) throw new Error(data.error || 'The service is temporarily unavailable. Please retry.');
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('The service did not respond in time. Please retry to confirm the result.');
    throw error;
  } finally { clearTimeout(timer); }
}
const claims = document.getElementById('claim-register');
if (claims) {
  claims.setAttribute('aria-busy', 'true');
  requestJSON('/api/claims').then(data => {
    if (!Array.isArray(data.claims)) throw new Error('The claim register is unavailable.');
    claims.replaceChildren();
    for (const item of data.claims) {
      const article = document.createElement('article'); article.className = 'claim';
      const heading = document.createElement('h3'); heading.textContent = item.claim;
      const status = document.createElement('p'); status.className = 'eyebrow'; status.textContent = item.id + ' · ' + item.status;
      const scope = document.createElement('p'); scope.className = 'scope'; scope.textContent = item.scope;
      const source = document.createElement('a'); source.href = item.source; source.textContent = 'Read the supporting source';
      article.append(status, heading, scope, source); claims.append(article);
    }
  }).catch(() => {
    claims.replaceChildren();
    const message = document.createElement('p'); message.textContent = 'The live claim register is temporarily unavailable. The retained review remains available.';
    const source = document.createElement('a'); source.href = '/research/claim-review'; source.textContent = 'Read the retained claim review';
    claims.append(message, source);
  }).finally(() => claims.setAttribute('aria-busy', 'false'));
}
const live = document.getElementById('live-refresh');
if (live) live.addEventListener('click', async () => {
  const result = document.getElementById('live-readback');
  live.disabled = true; result.setAttribute('aria-busy', 'true'); result.textContent = 'Reading the current family state…';
  try { result.textContent = JSON.stringify(await requestJSON('/api/runtime'), null, 2); }
  catch { result.textContent = 'The runtime readback is currently unavailable. Please retry; the retained evidence remains available below.'; }
  finally { live.disabled = false; result.setAttribute('aria-busy', 'false'); }
});
const form = document.getElementById('interest-form');
if (form) {
  let requestId = crypto.randomUUID();
  const parameters = new URLSearchParams(location.search), topic = parameters.get('topic');
  if ([...form.elements.interest.options].some(option => option.value === topic)) form.elements.interest.value = topic;
  const context = parameters.get('context'), contextLabel = document.getElementById('enquiry-context');
  if (contextLabel && context && /^\/[a-z0-9/-]*$/.test(context) && context.length <= 120) {
    contextLabel.hidden = false; contextLabel.textContent = 'You arrived from ' + context + '. Your selected topic is ' + form.elements.interest.value + '. Include that page in your message if it helps explain your enquiry.';
  }
  const message = form.elements.message;
  const validate = () => message.setCustomValidity(message.value.trim().length < 10 ? 'Please describe your use case in at least 10 characters.' : '');
  message.addEventListener('input', validate);
  form.addEventListener('submit', async event => {
    event.preventDefault(); validate(); if (!form.reportValidity()) return;
    const button = form.querySelector('button[type=submit]'), result = document.getElementById('form-result');
    button.disabled = true; form.setAttribute('aria-busy', 'true'); result.className = ''; result.textContent = 'Recording your enquiry…';
    try {
      const data = Object.fromEntries(new FormData(form)); data.consent = form.elements.consent.checked; data.request_id = requestId;
      const receipt = await requestJSON('/api/interest', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)});
      if (receipt.status !== 'registered' || !/^KEDDEH-[A-F0-9]{24}$/.test(receipt.receipt)) throw new Error('The registration receipt could not be confirmed. Retry with the same details.');
      result.className = 'success'; result.textContent = receipt.message + ' Registration reference: ' + receipt.receipt;
      form.reset(); message.setCustomValidity(''); requestId = crypto.randomUUID(); result.focus();
    } catch (error) {
      result.className = 'error'; result.textContent = 'Registration could not be confirmed. Your entries remain available. Retry with the same details to recover the same submission identity. ' + error.message; result.focus();
    } finally { button.disabled = false; form.setAttribute('aria-busy', 'false'); }
  });
}
