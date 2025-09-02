const chat = document.getElementById('chat-area');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');
const voiceSelect = document.getElementById('voiceSelect');
const chatList = document.getElementById('chat-list');
const newChatBtn = document.getElementById('newChatBtn');
const toggleSidebarBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('chat-sidebar');

let voices = [];
let selectedVoiceName = localStorage.getItem('halSelectedVoice') || '';
let currentChatId = localStorage.getItem('halCurrentChatId') || null;
let isLoading = false;

// Voice setup
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

// Text-to-speech function
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

// Message display function
function appendMessage(text, sender = 'bot') {
    // Remove welcome message when first message is added
    const welcomeMsg = document.getElementById('welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const msg = document.createElement('div');
    msg.classList.add('msg-bubble');
    msg.classList.add(sender === 'user' ? 'msg-client' : 'msg-system');
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;

    if (sender === 'bot') {
        // Convert markdown-style bold (**) to <strong>
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        msg.innerHTML = '';
        let index = 0;
        const interval = setInterval(() => {
            msg.innerHTML = formatted.slice(0, index + 1);
            index++;
            if (index >= formatted.length) clearInterval(interval);
            chat.scrollTop = chat.scrollHeight;
        }, 10);
    } else {
        msg.textContent = text;
    }
}

// Load chat list
async function loadChatList() {
    try {
        const response = await fetch('/api/chats');
        const data = await response.json();

        chatList.innerHTML = '';

        if (data.chats && data.chats.length > 0) {
            data.chats.forEach(chatItem => {
                const chatElement = createChatListItem(chatItem);
                chatList.appendChild(chatElement);
            });
        } else {
            chatList.innerHTML = '<div id="no-chats" style="color: #666; text-align: center; padding: 20px; font-size: 0.9rem;">No chats yet. Start a new conversation!</div>';
        }
    } catch (error) {
        console.error('Error loading chats:', error);
        chatList.innerHTML = '<div style="color: #ff6666; text-align: center; padding: 20px;">Error loading chats</div>';
    }
}

// Create chat list item element
function createChatListItem(chatItem) {
    const div = document.createElement('div');
    div.className = 'chat-item';
    div.dataset.chatId = chatItem.chat_id;

    if (chatItem.chat_id === currentChatId) {
        div.classList.add('active');
    }

    div.innerHTML = `
        <div class="chat-title">${chatItem.title}</div>
        <div class="chat-meta">${chatItem.message_count} messages</div>
        <div class="chat-actions">
            <button class="delete-chat" onclick="deleteChat('${chatItem.chat_id}', event)">×</button>
        </div>
    `;

    div.addEventListener('click', () => loadChat(chatItem.chat_id));

    return div;
}

// Load specific chat
async function loadChat(chatId) {
    if (isLoading || chatId === currentChatId) return;

    isLoading = true;
    sendBtn.disabled = true;

    try {
        const response = await fetch(`/api/chat/${chatId}`);
        const data = await response.json();

        if (data.messages) {
            currentChatId = chatId;
            localStorage.setItem('halCurrentChatId', chatId);

            // Clear chat area
            chat.innerHTML = '';

            // Load messages
            data.messages.forEach(msg => {
                appendMessage(msg.content, msg.role === 'user' ? 'user' : 'bot');
            });

            // Update active chat in sidebar
            document.querySelectorAll('.chat-item').forEach(item => {
                item.classList.remove('active');
                if (item.dataset.chatId === chatId) {
                    item.classList.add('active');
                }
            });
        }
    } catch (error) {
        console.error('Error loading chat:', error);
        appendMessage('Error loading chat history', 'bot');
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
    }
}

// Create new chat
async function createNewChat() {
    if (isLoading) return;

    isLoading = true;
    sendBtn.disabled = true;

    try {
        const response = await fetch('/api/chat/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();

        if (data.chat_id) {
            currentChatId = data.chat_id;
            localStorage.setItem('halCurrentChatId', data.chat_id);

            // Clear chat area and show welcome
            chat.innerHTML = '<div id="welcome-message" class="msg-bubble msg-system">New chat started. How can I assist you, Ahad?</div>';

            // Refresh chat list
            await loadChatList();

            // Set focus to input
            input.focus();
        }
    } catch (error) {
        console.error('Error creating new chat:', error);
        appendMessage('Error creating new chat', 'bot');
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
    }
}

// Delete chat
async function deleteChat(chatId, event) {
    event.stopPropagation();

    if (!confirm('Are you sure you want to delete this chat?')) return;

    try {
        const response = await fetch(`/api/chat/${chatId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            // If this was the current chat, clear it
            if (chatId === currentChatId) {
                currentChatId = null;
                localStorage.removeItem('halCurrentChatId');
                chat.innerHTML = '<div id="welcome-message" class="msg-bubble msg-system">Chat deleted. Select a chat or start a new one.</div>';
            }

            // Refresh chat list
            await loadChatList();
        }
    } catch (error) {
        console.error('Error deleting chat:', error);
    }
}

// Send message
async function sendMessage(e) {
    if (e) e.preventDefault();

    const userMessage = input.value.trim();
    if (!userMessage || isLoading) return;

    // Create new chat if none selected
    if (!currentChatId) {
        await createNewChat();
    }

    appendMessage(userMessage, 'user');
    input.value = '';
    isLoading = true;
    sendBtn.disabled = true;

    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userMessage,
                chat_id: currentChatId
            })
        });
        const data = await response.json();

        if (data.response) {
            appendMessage(data.response, 'bot');
            speak(data.response);

            // Update current chat ID if it was created
            if (data.chat_id && data.chat_id !== currentChatId) {
                currentChatId = data.chat_id;
                localStorage.setItem('halCurrentChatId', data.chat_id);
            }

            // Refresh chat list to show updated message count
            await loadChatList();
        } else {
            appendMessage('Error: No response from server', 'bot');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        appendMessage('Error: Could not reach server', 'bot');
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

// Toggle sidebar (for mobile)
function toggleSidebar() {
    sidebar.classList.toggle('hidden');
}

// Event listeners
newChatBtn.addEventListener('click', createNewChat);
toggleSidebarBtn.addEventListener('click', toggleSidebar);

// Auto-resize on window resize
window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        sidebar.classList.remove('hidden');
    }
});

// Initialize app
async function initializeApp() {
    await loadChatList();

    // Load current chat if exists
    if (currentChatId) {
        await loadChat(currentChatId);
    }

    // Set focus to input
    input.focus();
}

// Load on page ready
document.addEventListener('DOMContentLoaded', initializeApp);

// Handle Enter key in input
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
