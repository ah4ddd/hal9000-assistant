const chat = document.getElementById('chat');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');

let conversation = [];
let halVoice = null;

// ✅ Load voices once they're available
function loadVoices() {
  const voices = window.speechSynthesis.getVoices();

  // Try to pick a HAL-like voice (male / English / robotic)
  halVoice = voices.find(v =>
    v.lang.toLowerCase().includes('en') &&
    (v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('robot'))
  )
  || voices.find(v => v.lang.toLowerCase().includes('en'))
  || voices[0];

  console.log("Chosen voice:", halVoice);
}

window.speechSynthesis.onvoiceschanged = loadVoices;
loadVoices();

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
  if (halVoice) {
    utterance.voice = halVoice;
  }
  utterance.rate = 0.95;
  utterance.pitch = 0.9;
  utterance.volume = 1;
  speechSynthesis.speak(utterance);
}

async function sendMessage() {
  const userMessage = input.value.trim();
  if (!userMessage) return;

  appendMessage('You', userMessage);
  conversation.push({ role: 'user', content: userMessage });
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
      conversation.push({ role: 'assistant', content: data.response });
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

