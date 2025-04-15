function sendMessage() {
    var userMsg = document.getElementById('user-input').value;
    var chatBox = document.getElementById('chat-box');

    chatBox.innerHTML += '<p><strong>You:</strong> ' + userMsg + '</p>';
    document.getElementById('user-input').value = '';

    fetch('/ask_chatbot/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({'message': userMsg})
    })
    .then(response => response.json())
    .then(data => {
        var formattedRes = marked.parse(data.response);
        chatBox.innerHTML += '<p><strong>Bot:</strong> ' + formattedRes + '</p>';
    })
    .catch(error => {
        chatBox.innerHTML += '<p><strong>Bot:</strong> Error processing your request.</p>';
        console.error('Error:', error); 
    });
}

function startVoiceInput() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Your browser does not support voice input.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    const micButton = document.querySelector(".voice-button");

    recognition.onstart = () => {
        console.log("Listening");
        micButton.classList.add("listening");
    }

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('user-input').value = transcript;
        sendMessage();
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error', event.error);
    };

    recognition.onend = function() {
        micButton.classList.remove("listening");
    }

    recognition.start();
}