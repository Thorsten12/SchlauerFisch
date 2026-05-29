// script.js

const fishFrame  = document.getElementById('fishFrame');
const idleWrap   = document.getElementById('idleWrap');
const dot        = document.getElementById('dot');
const statusTxt  = document.getElementById('statusTxt');
const sendBtn    = document.getElementById('sendBtn');
const userInput  = document.getElementById('userInput');

const divider    = document.getElementById('divider');
const replyLabel = document.getElementById('replyLabel');
const replyText  = document.getElementById('replyText');

function setState(state) {
  fishFrame.className =
    'fish-frame' + (state === 'loading' ? ' loading' : '');

  idleWrap.className =
    'idle-wrap' + (state === 'talking' ? ' talking' : '');

  dot.className =
    'dot' + (state === 'loading' ? ' pulse' : '');

  statusTxt.textContent = {
    idle: 'bereit',
    loading: 'verarbeite…',
    talking: 'spricht'
  }[state];

  sendBtn.disabled = state === 'loading';

  sendBtn.textContent =
    state === 'loading'
      ? '...'
      : 'Senden';
}

async function handleSend() {
  const msg = userInput.value.trim();

  if (!msg) return;

  setState('loading');

  [divider, replyLabel, replyText]
    .forEach(el => el.classList.remove('visible'));

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json'
      },

      body: JSON.stringify({
        message: msg
      })
    });

    if (!res.ok) {
      throw new Error('HTTP ' + res.status);
    }

    const data = await res.json();

    replyText.textContent =
      data.reply ?? JSON.stringify(data);

    [divider, replyLabel, replyText]
      .forEach(el => el.classList.add('visible'));

    userInput.value = '';

    setState('talking');

    setTimeout(() => {
      setState('idle');
    }, 4500);

  } catch (err) {
    statusTxt.textContent =
      'fehler: ' + err.message;

    dot.className = 'dot';

    sendBtn.disabled = false;
    sendBtn.textContent = 'Senden';
  }
}

sendBtn.addEventListener('click', handleSend);

userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    handleSend();
  }
});