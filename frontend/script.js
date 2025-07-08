const chat = document.getElementById('chat');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');
const voiceSelect = document.getElementById('voiceSelect');

let voices = [];
let selectedVoiceName = localStorage.getItem('halSelectedVoice') || '';

function populateVoiceList() {
  voices = speechSynthesis.getVoices();
  voiceSelect.innerHTML = '';
  voices.forEach((voice) => {
    const option = document.createElement('option');
    option.value = voice.name;
    option.textContent = `${voice.name} (${voice.lang})`;
    if (voice.name === selectedVoiceName) {
      option.selected = true;
    }
    voiceSelect.appendChild(option);
  });
}

populateVoiceList();
speechSynthesis.onvoiceschanged = populateVoiceList;

voiceSelect.addEventListener('change', () => {
  selectedVoiceName = voiceSelect.value;
  localStorage.setItem('halSelectedVoice', selectedVoiceName);
});

function appendMessage(speaker, text) {
  const msg = document.createElement('div');
  msg.classList.add('message');
  msg.classList.add(speaker === 'You' ? 'user' : 'bot');
  msg.textContent = `${speaker}: ${text}`;
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}

function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95;
  utterance.pitch = 0.9;
  utterance.volume = 1;

  const chosenVoice = voices.find(v => v.name === selectedVoiceName);
  if (chosenVoice) {
    utterance.voice = chosenVoice;
  }

  speechSynthesis.speak(utterance);
}

async function sendMessage() {
  const userMessage = input.value.trim();
  if (!userMessage) return;

  appendMessage('You', userMessage);
  input.value = '';

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMessage, user_id: "browser-user" })
    });
    const data = await res.json();

    if (data.response) {
      appendMessage('HAL 9000', data.response);
      speak(data.response);
    } else {
      appendMessage('HAL 9000', 'Error: No response from server');
    }
  } catch (e) {
    appendMessage('HAL 9000', 'Error: Could not reach server');
  }
}

sendBtn.addEventListener('click', sendMessage);
input.addEventListener('keydown', e => {
  if (e.key === 'Enter') sendMessage();
});
