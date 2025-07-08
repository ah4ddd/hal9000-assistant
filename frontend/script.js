// Wait for the DOM to load before accessing elements
document.addEventListener("DOMContentLoaded", () => {
  const chat = document.getElementById('chat');
  const input = document.getElementById('input');
  const sendBtn = document.getElementById('send');

  let conversation = [];

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
      } else if (data.error) {
        appendMessage('HAL 9000', `Error: ${data.error}`);
      } else {
        appendMessage('HAL 9000', 'Unknown error.');
      }
    } catch (e) {
      appendMessage('HAL 9000', 'Error: Could not reach server.');
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMessage();
  });
});
