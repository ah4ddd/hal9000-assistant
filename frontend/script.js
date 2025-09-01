const chat = document.getElementById('chat-area');
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

function appendMessage(text, sender = 'bot') {
    const msg = document.createElement('div');
    msg.classList.add('msg-bubble');
    msg.classList.add(sender === 'user' ? 'msg-client' : 'msg-system');
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;

    if (sender === 'bot') {
        // Convert markdown-style bold (**) to <strong>
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // **bold** -> <strong>bold</strong>
            .replace(/\n/g, '<br>'); // Line breaks

        msg.innerHTML = '';
        let index = 0;
        const interval = setInterval(() => {
            msg.innerHTML = formatted.slice(0, index + 1);
            index++;
            if (index >= formatted.length) clearInterval(interval);
            chat.scrollTop = chat.scrollHeight;
        }, 10); // Adjust speed as you like
    } else {
        msg.textContent = text;
    }
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

async function sendMessage(e) {
    if (e) e.preventDefault();

    const userMessage = input.value.trim();
    if (!userMessage) return;

    appendMessage(userMessage, 'user');
    input.value = '';

    try {
        const res = await fetch('/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMessage, user_id: "browser-user" })
        });
        const data = await res.json();

        if (data.response) {
            appendMessage(data.response, 'bot');
            speak(data.response);
        } else {
            appendMessage('Error: No response from server', 'bot');
        }
    } catch (e) {
        appendMessage('Error: Could not reach server', 'bot');
    }
}

document.getElementById('resetChat').addEventListener('click', async () => {
    try {
        await fetch('/api/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: 'browser-user' })
        });
        chat.innerHTML = '';
        appendMessage('New chat started. How can I help you, Ahad?', 'bot');
    } catch (err) {
        appendMessage('Error: Could not reset chat', 'bot');
    }
});
