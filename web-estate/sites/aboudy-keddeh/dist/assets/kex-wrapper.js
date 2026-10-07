/* HTML KEX Site adapter v1. ES5 syntax; no native multiplexer authority. */
(function (window, document) {
  'use strict';
  var preference = 'auto', queue = [], timer = null, serial = 0;
  function matches(query) {
    try { return !!window.matchMedia && window.matchMedia(query).matches; } catch (ignore) { return false; }
  }
  function light() {
    return preference === 'light' || (preference === 'auto' &&
      (matches('(prefers-reduced-motion: reduce)') || matches('(prefers-reduced-data: reduce)') ||
       (window.navigator.connection && window.navigator.connection.saveData) ||
       (window.navigator.deviceMemory && window.navigator.deviceMemory <= 2) || window.innerWidth < 480));
  }
  function apply() {
    document.documentElement.setAttribute('data-kex-mode', light() ? 'light' : 'standard');
    var status = document.getElementById('kex-status');
    if (status) status.textContent = (light() ? 'Lightweight' : 'Standard') + ' mode active. No background polling.';
  }
  function setMode(value) {
    if (value !== 'auto' && value !== 'light' && value !== 'standard') throw new Error('Unsupported KEX mode');
    preference = value;
    try { window.localStorage.setItem('kex-site-mode', value); } catch (ignore) { /* preference remains session-local */ }
    apply();
  }
  function schedule() {
    if (timer === null && queue.length && !document.hidden) timer = window.setTimeout(tick, 16);
  }
  function tick() {
    timer = null;
    if (document.hidden) return;
    var start = new Date().getTime(), budget = light() ? 2 : 4, turns = 0;
    while (queue.length && turns < 8 && new Date().getTime() - start < budget) {
      var job = queue.shift(); turns += 1;
      try {
        job.steps += 1;
        var done = job.step() === true;
        if (!done && job.steps < 512) queue.push(job);
        else if (!done && job.error) job.error(new Error('KEX job step limit reached'));
      } catch (error) { if (job.error) { try { job.error(error); } catch (ignore) {} } }
    }
    schedule();
  }
  window.KEXSite = {
    version: '1.0.0',
    runPackage: function (executable, handlers, error) {
      if (!window.KEXEngine) throw new Error('KEX engine package unavailable');
      var runner = window.KEXEngine.runner(executable, handlers);
      return window.KEXSite.enqueue(runner.step, error);
    },
    setMode: setMode,
    capabilities: function () {
      return { profile: light() ? 'light' : 'standard', fetch: typeof window.fetch === 'function',
        workers: typeof window.Worker === 'function', queueLimit: 8, stepLimit: 512,
        hardwareArchitectureVerified: false, multiplexerConnected: false };
    },
    enqueue: function (step, error) {
      if (typeof step !== 'function' || (error && typeof error !== 'function')) throw new Error('Invalid KEX job');
      if (queue.length >= 8) throw new Error('KEX queue capacity reached');
      serial += 1; queue.push({ id: serial, step: step, error: error, steps: 0 }); schedule(); return serial;
    },
    cancel: function (id) {
      for (var index = queue.length - 1; index >= 0; index -= 1) if (queue[index].id === id) queue.splice(index, 1);
      if (!queue.length && timer !== null) { window.clearTimeout(timer); timer = null; }
    }
  };
  try {
    var saved = window.localStorage.getItem('kex-site-mode');
    if (saved === 'light' || saved === 'standard') preference = saved;
  } catch (ignore) {}
  var control = document.getElementById('kex-mode');
  if (control) { control.value = preference; control.addEventListener('change', function () { setMode(control.value); }); }
  var nav = document.querySelector('nav[aria-label="Main navigation"]');
  if (nav) nav.addEventListener('keydown', function (event) {
    if (event.target.tagName !== 'A') return;
    var links = nav.querySelectorAll('a'), current = -1, key = event.key || event.keyCode;
    for (var i = 0; i < links.length; i += 1) if (links[i] === event.target) current = i;
    var next = current;
    if (key === 'ArrowRight' || key === 39) next = Math.min(links.length - 1, current + 1);
    else if (key === 'ArrowLeft' || key === 37) next = Math.max(0, current - 1);
    else if (key === 'Home' || key === 36) next = 0;
    else if (key === 'End' || key === 35) next = links.length - 1;
    else return;
    event.preventDefault(); links[next].focus();
  });
  document.addEventListener('visibilitychange', function () {
    if (document.hidden && timer !== null) { window.clearTimeout(timer); timer = null; }
    else schedule();
  });
  apply();
}(window, document));
