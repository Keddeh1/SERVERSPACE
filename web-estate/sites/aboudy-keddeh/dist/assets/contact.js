(function () {
  'use strict';
  var form = document.getElementById('interest-form');
  if (!form) return;
  var status = document.getElementById('capture-status'), button = form.querySelector('button');
  var errors = document.getElementById('form-errors'), capability = null, requestId = null;
  function unavailable() {
    status.textContent = 'Online registration is currently unavailable. Please use the email enquiry link below.';
    button.disabled = true;
  }
  if (!window.fetch || !window.Promise || !window.crypto || !window.crypto.getRandomValues) { unavailable(); return; }
  function identifier() {
    var bytes = new Uint8Array(16); window.crypto.getRandomValues(bytes);
    bytes[6] = (bytes[6] & 15) | 64; bytes[8] = (bytes[8] & 63) | 128;
    var hex = Array.prototype.map.call(bytes, function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
    return hex.slice(0, 8) + '-' + hex.slice(8, 12) + '-' + hex.slice(12, 16) + '-' + hex.slice(16, 20) + '-' + hex.slice(20);
  }
  function refresh() {
    return fetch('/api/capabilities', { credentials: 'same-origin', cache: 'no-store' }).then(function (response) {
      if (!response.ok) throw new Error('Unavailable'); return response.json();
    }).then(function (value) {
      if (!value.capture_enabled || value.notice_revision !== 'portfolio-enquiry-v1') throw new Error('Unavailable');
      capability = value; status.textContent = 'Registration is available. Required fields are marked.'; button.disabled = false;
    }).catch(unavailable);
  }
  function showErrors(items) {
    var list = errors.querySelector('ul'); list.textContent = '';
    items.forEach(function (item) {
      var li = document.createElement('li'), field = document.getElementById(item.field);
      if (field) {
        field.setAttribute('aria-invalid', 'true');
        var inline = document.createElement('p'); inline.className = 'field-error'; inline.id = item.field + '-error'; inline.textContent = item.message;
        field.parentNode.appendChild(inline);
        field.setAttribute('aria-describedby', (field.getAttribute('aria-describedby') || '') + ' ' + inline.id);
        var link = document.createElement('a'); link.href = '#' + item.field; link.textContent = item.message; li.appendChild(link);
      } else li.textContent = item.message;
      list.appendChild(li);
    }); errors.hidden = false; errors.focus();
  }
  form.addEventListener('input', function () { requestId = null; });
  form.addEventListener('submit', function (event) {
    event.preventDefault(); if (!capability || button.disabled) return;
    errors.hidden = true;
    Array.prototype.forEach.call(form.querySelectorAll('.field-error'), function (node) { node.parentNode.removeChild(node); });
    Array.prototype.forEach.call(form.querySelectorAll('[aria-invalid]'), function (field) { field.removeAttribute('aria-invalid'); });
    ['name', 'email', 'privacy_consent'].forEach(function (key) { document.getElementById(key).removeAttribute('aria-describedby'); });
    var payload = {}, fields = ['name', 'email', 'organisation', 'use_case', 'message'];
    fields.forEach(function (key) { payload[key] = document.getElementById(key).value.trim(); });
    payload.privacy_consent = document.getElementById('privacy_consent').checked;
    payload.marketing_consent = document.getElementById('marketing_consent').checked;
    payload.notice_revision = 'portfolio-enquiry-v1';
    var issues = [];
    if (!payload.name) issues.push({ field: 'name', message: 'Enter your name.' });
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(payload.email)) issues.push({ field: 'email', message: 'Enter a valid email address.' });
    if (!payload.privacy_consent) issues.push({ field: 'privacy_consent', message: 'Confirm that you have read the privacy notice.' });
    if (issues.length) { showErrors(issues); return; }
    requestId = requestId || identifier(); button.disabled = true; button.textContent = 'Recording…';
    fetch('/api/interest', { method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': capability.csrf_token, 'Idempotency-Key': requestId },
      body: JSON.stringify(payload)
    }).then(function (response) {
      return response.json().then(function (value) { if (!response.ok) throw new Error(value.error || 'The enquiry could not be recorded.'); return value; });
    }).then(function (receipt) {
      var success = document.getElementById('form-success');
      var heading = document.createElement('h2'); heading.textContent = 'Your interest is recorded.';
      var details = document.createElement('p'); details.textContent = 'Reference: ' + receipt.registration_id + '. No email has been sent. Keep this reference for follow-up or erasure requests.';
      success.textContent = ''; success.appendChild(heading); success.appendChild(details);
      form.hidden = true; success.hidden = false; success.focus();
    }).catch(function (error) {
      showErrors([{ message: error.message + ' Your entries are retained. Retry or use the email link.' }]);
    }).then(function () { button.disabled = false; button.textContent = 'Register interest'; });
  });
  refresh();
}());
