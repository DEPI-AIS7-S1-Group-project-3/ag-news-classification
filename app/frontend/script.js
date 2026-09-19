// AG Wire — classification console
// Talks to the FastAPI /predict endpoint and renders the result.

const SEGMENTS = 10;

const SLUG = {
  'World': 'world',
  'Sports': 'sports',
  'Business': 'business',
  'Sci/Tech': 'scitech',
};

const els = {
  text: document.getElementById('text'),
  counter: document.getElementById('counter'),
  send: document.getElementById('send'),
  error: document.getElementById('error'),
  result: document.getElementById('result'),
  category: document.getElementById('category'),
  signalMeter: document.getElementById('signalMeter'),
  signalValue: document.getElementById('signalValue'),
  flag: document.getElementById('flag'),
  timing: document.getElementById('timing'),
  lamps: document.getElementById('lamps'),
  apiUrl: document.getElementById('apiUrl'),
  log: document.getElementById('log'),
  logItems: document.getElementById('logItems'),
};

const history = [];

// Build the segmented meter once.
for (let i = 0; i < SEGMENTS; i++) {
  const seg = document.createElement('span');
  els.signalMeter.appendChild(seg);
}

els.text.addEventListener('input', () => {
  els.counter.textContent = `${els.text.value.length} characters`;
});

els.text.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) classify();
});

els.send.addEventListener('click', classify);

function setLamp(category) {
  [...els.lamps.children].forEach((lamp) => {
    lamp.classList.toggle('active', lamp.dataset.desk === category);
  });
}

function setMeter(confidence, category) {
  const filled = Math.round((confidence || 0) * SEGMENTS);
  const color = getCategoryColor(category);
  [...els.signalMeter.children].forEach((seg, i) => {
    seg.classList.toggle('lit', i < filled);
    seg.style.setProperty('--seg-color', color);
  });
  els.signalValue.textContent = `${Math.round((confidence || 0) * 100)}%`;
}

function getCategoryColor(category) {
  const styles = getComputedStyle(document.documentElement);
  const slug = SLUG[category];
  return styles.getPropertyValue(`--${slug}`).trim() || styles.getPropertyValue('--ink');
}

function addToLog(text, category, confidence) {
  history.unshift({ text, category, confidence });
  if (history.length > 5) history.pop();

  els.log.classList.add('show');
  els.logItems.innerHTML = history.map((h) => `
    <li>
      <span class="l-cat ${SLUG[h.category]}">${h.category}</span>
      <span class="l-text">${escapeHtml(h.text)}</span>
      <span class="l-conf">${Math.round(h.confidence * 100)}%</span>
    </li>
  `).join('');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

async function classify() {
  const text = els.text.value.trim();
  if (!text) {
    els.text.focus();
    return;
  }

  els.send.disabled = true;
  els.send.textContent = 'Routing…';
  els.error.classList.remove('show');
  els.result.classList.remove('show');

  const started = performance.now();

  try {
    const response = await fetch(els.apiUrl.value, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`HTTP ${response.status} — ${body.slice(0, 160)}`);
    }

    const data = await response.json();
    const elapsed = ((performance.now() - started) / 1000).toFixed(2);
    const confidence = data.confidence ?? 0;

    els.category.textContent = data.category;
    els.category.dataset.cat = data.category;
    setMeter(confidence, data.category);
    setLamp(data.category);

    els.flag.textContent = data.used_fallback
      ? 'Fallback used — the model was unreachable, this is a keyword guess.'
      : 'Routed by the model. No fallback used.';
    els.flag.classList.toggle('fallback', Boolean(data.used_fallback));

    els.timing.textContent = `${elapsed}s`;
    els.result.classList.add('show');
    addToLog(text, data.category, confidence);

  } catch (err) {
    els.error.textContent = `Could not reach the desk — ${err.message}`;
    els.error.classList.add('show');
  } finally {
    els.send.disabled = false;
    els.send.textContent = 'Classify';
  }
}
