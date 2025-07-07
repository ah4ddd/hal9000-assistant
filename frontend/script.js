const chatWindow = document.getElementById("chat");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

let conversation = [];
console.log("Loaded JS version 2");


sendButton.addEventListener("click", () => {
  userInput.addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    sendButton.click();
  }
});
  const userMessage = userInput.value.trim();
  if (userMessage === "") return;
  userInput.value = "";
  addMessage("You", userMessage);
  fetchResponse(userMessage);
});

function addMessage(sender, message) {
  conversation.push({ sender, message });
  renderChat();
}

function renderChat() {
  chatWindow.innerHTML = "";
  conversation.forEach(entry => {
    chatWindow.innerHTML += `<p><strong>${entry.sender}:</strong> ${entry.message}</p>`;
  });
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function fetchResponse(userMessage) {
fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage })
  })
  .then(res => res.json())
  .then(data => {
    if (data.response) {
      addMessage("HAL 9000", data.response);
    } else if (data.error) {
      addMessage("HAL 9000", "Error: " + data.error);
    } else {
      addMessage("HAL 9000", "Unknown error.");
    }
  })
  .catch(() => {
    addMessage("HAL 9000", "Error: Could not reach server.");
  });
}
