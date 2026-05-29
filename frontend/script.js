// =========================================
// 1. DOM-Elemente (nur EINMAL deklarieren)
// =========================================
const fishFrame  = document.getElementById('fishFrame');
const idleWrap   = document.getElementById('idleWrap');
const dot        = document.getElementById('dot');
const statusTxt  = document.getElementById('statusTxt');
const sendBtn    = document.getElementById('sendBtn');
const userInput  = document.getElementById('userInput');
const divider    = document.getElementById('divider');
const replyLabel = document.getElementById('replyLabel');
const replyText  = document.getElementById('replyText');
const appContainer = document.getElementById("app");
const audioBtn   = document.getElementById("audioBtn");

// =========================================
// 2. Zentrales State-Management
// =========================================
function setState(state) {
  fishFrame.className = 'fish-frame' + (state === 'loading' ? ' loading' : '');
  idleWrap.className  = 'idle-wrap' + (state === 'talking' ? ' talking' : '');
  dot.className       = 'dot' + (state === 'loading' ? ' pulse' : '');

  statusTxt.textContent = {
    idle: 'bereit',
    loading: 'verarbeite…',
    talking: 'spricht'
  }[state];

  sendBtn.disabled = state === 'loading';
  sendBtn.textContent = state === 'loading' ? '...' : 'Senden';
  
  // Audio-Button während des Ladens ebenfalls deaktivieren
  audioBtn.disabled = true; //state === 'loading';
}

// =========================================
// 3. Text-Logik
// =========================================
async function handleSend() {
  const msg = userInput.value.trim();
  if (!msg) return;

  setState('loading');
  [divider, replyLabel, replyText].forEach(el => el.classList.remove('visible'));

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });

    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();

    replyText.textContent = data.reply ?? JSON.stringify(data);
    [divider, replyLabel, replyText].forEach(el => el.classList.add('visible'));
    userInput.value = '';

    setState('talking');
    setTimeout(() => setState('idle'), 4500);

  } catch (err) {
    setState('idle'); // Setzt alles sauber zurück (versteckt das Lade-GIF)
    statusTxt.textContent = 'fehler: ' + err.message; // Zeigt den Fehler an
  }
}

sendBtn.addEventListener('click', handleSend);
userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') handleSend();
});

// =========================================
// 4. Audio-Logik
// =========================================
let mediaRecorder;
let audioChunks = [];

// Neue Variablen für den Timer
let recordTimerInterval;
let recordSeconds = 0;
const audioBtnText = document.getElementById("audioBtnText"); 
audioBtn.disabled = true;
audioBtn.addEventListener("click", async () => {
  const isRecording = appContainer.classList.contains("recording");

  if (!isRecording) {
    // ---> AUFNAHME STARTEN
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.addEventListener("dataavailable", event => {
        if (event.data.size > 0) audioChunks.push(event.data);
      });

      mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        sendAudioToServer(audioBlob);
        stream.getTracks().forEach(track => track.stop()); // Hardware freigeben
      });

      mediaRecorder.start();
      appContainer.classList.add("recording");

      // Timer starten und UI sofort aktualisieren
      recordSeconds = 0;
      audioBtnText.textContent = `Stoppen (${recordSeconds}s)`;
      
      recordTimerInterval = setInterval(() => {
        recordSeconds++;
        audioBtnText.textContent = `Stoppen (${recordSeconds}s)`;
      }, 1000);

    } catch (error) {
      console.error("Mikrofon-Zugriff fehlgeschlagen:", error);
      alert("Bitte erlaube den Mikrofon-Zugriff im Browser, um diese Funktion zu nutzen.");
    }

  } else {
    // ---> AUFNAHME STOPPEN
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop(); 
    }
    appContainer.classList.remove("recording");
    
    // Timer stoppen und Text zurücksetzen
    clearInterval(recordTimerInterval);
    audioBtnText.textContent = "Audio senden";
  }
});

async function sendAudioToServer(audioBlob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");

  setState('loading');
  [divider, replyLabel, replyText].forEach(el => el.classList.remove('visible'));

  try {
    const response = await fetch("/api/upload-audio", {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const data = await response.json(); 
    
    replyText.textContent = data.text || "Der Server hat keine Textantwort gesendet."; 
    [divider, replyLabel, replyText].forEach(el => el.classList.add('visible'));

    setState('talking');
    setTimeout(() => setState('idle'), 4500);

  } catch (error) {
    console.error("Netzwerkfehler beim Senden:", error);
    setState('idle'); // Setzt alles sauber zurück (versteckt das Lade-GIF)
    statusTxt.textContent = 'fehler: ' + error.message; // Zeigt den Fehler an
  }
}