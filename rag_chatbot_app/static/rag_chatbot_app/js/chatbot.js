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