const sendBtn = document.getElementById('sendBtn');
const userInput = document.getElementById('userInput');
const messages = document.getElementById('messages');
const userId = "ahad";

function addMessage(sender, text) {
  const msg = document.createElement('div');
  msg.className = 'message ' + sender;
  msg.innerText = `${sender === 'user' ? 'You' : 'HAL 9000'}: ${text}`;
  messages.appendChild(msg);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  addMessage('user', text);
  userInput.value = '';

  try {
    const res = await fetch('http://127.0.0.1:5000/api/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ user_id: userId, message: text })
    });

    const data = await res.json();
    if (data.response) {
      addMessage('hal', data.response);
      speakText(data.response);
    } else {
      addMessage('hal', "Error: Could not process your request.");
    }
  } catch (err) {
    addMessage('hal', "Error: Could not reach server.");
  }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') sendMessage();
});

function speakText(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.voice = speechSynthesis.getVoices().find(voice => voice.lang.startsWith('en'));
  speechSynthesis.speak(utterance);
}
