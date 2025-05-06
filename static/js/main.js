function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();

    recognition.onresult = function(event) {
        const command = event.results[0][0].transcript;
        document.getElementById('voice-result').innerText = "You said: " + command;

        fetch('/process_voice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('voice-result').innerText = data.result;
        });
    }
}

function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (!userInput.trim()) return;

    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML += `<div><b>You:</b> ${userInput}</div>`;

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        chatMessages.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;
        document.getElementById('user-input').value = '';
    });
}
