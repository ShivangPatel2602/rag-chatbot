function sendMessage() {
    var userMsg = document.getElementById('user-input').value.trim();
    var chatBox = document.getElementById('chat-box');

    if (!userMsg) return;

    chatBox.innerHTML += '<p><strong>You:</strong> ' + userMsg + '</p>';
    chatBox.scrollTop = chatBox.scrollHeight; 

    document.getElementById('user-input').value = '';

    fetch('/ask_chatbot/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        credentials: 'include',
        body: JSON.stringify({'message': userMsg})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        var formattedRes = marked.parse(data.response);
        chatBox.innerHTML += '<p><strong>Bot:</strong> ' + formattedRes + '</p>';
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        chatBox.innerHTML += '<p><strong>Bot:</strong> Error processing your request.</p>';
        console.error('Error:', error); 
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let recognition;

function startVoiceInput() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Your browser does not support voice input.");
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    document.getElementById('recording-modal').style.display = "block";
    recognition.start();

    recognition.onresult = event => {
        const transcript = event.results[0][0].transcript
        console.log("Transcript: ", transcript);
        
        document.getElementById('user-input').value = transcript;
        document.getElementById('recording-modal').style.display = "none";
    }

    recognition.onerror = event => {
        console.error("Error occurred in recognition: ", event.error);
        alert("Speech recognition error: " + event.error);
        document.getElementById('recording-modal').style.display = "none";
    }

    recognition.onend = () => {
        console.log("Speech recognition ended.");
        document.getElementById('recording-modal').style.display = "none";
    }
}

function stopVoiceInput() {
    if (recognition) {
        recognition.stop();
        document.getElementById('recording-modal').style.display = "none";
    }
}

// let recorder, audioStream;

// function startVoiceInput() {
//     navigator.mediaDevices.getUserMedia({ audio: true })
//         .then(stream => {
//             audioStream = stream;
//             const audioContext = new AudioContext();
//             const input = audioContext.createMediaStreamSource(stream);
//             recorder = new Recorder(input, {
//                 numChannels: 1
//             })
//             recorder.record();
//             document.getElementById('recording-modal').style.display = "block";
//         })
//         .catch(error => {
//             alert("Mic access error: " + err);
//         });
// }

// function stopVoiceInput() {
//     if (recorder) {
//         recorder.stop();
//         audioStream.getAudioTracks().forEach(track => track.stop());

//         document.getElementById('recording-modal').style.display = "none";

//         recorder.exportWAV(blob => {
//             const formData = new FormData();
//             formData.append('audio', blob, 'recording.wav');

//             fetch('/transcribe_audio/', {
//                 method: 'POST',
//                 headers: {
//                     'X-CSRFToken': csrfToken
//                 },
//                 body: formData
//             })
//             .then(response => response.json())
//             .then(data => {
//                 console.log(data);
//                 if (data.transcription) {
//                     document.getElementById("user-input").value = data.transcription;
//                 } else {
//                     alert("Transcription error: " + data.error);
//                 }
//             })
//             .catch(error => {
//                 alert("Transcription error: " + error);
//             });
//         })
//     }
// }