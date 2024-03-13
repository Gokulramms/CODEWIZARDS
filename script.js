const outputContainer = document.getElementById('output-container');
const output = document.getElementById('output');
const startBtn = document.getElementById('startBtn');
const clearBtn = document.getElementById('clearBtn');
let recognition = null;

// Function to change background color dynamically
function changeBackgroundColor() {
    const colors = ['#F08080', '#90EE90', '#ADD8E6', '#FFD700', '#FFA07A', '#98FB98'];
    const randomIndex = Math.floor(Math.random() * colors.length);
    document.body.style.backgroundColor = colors[randomIndex];
}

setInterval(changeBackgroundColor, 1200); // Change every 5 seconds

function startRecognition() {
    recognition = new webkitSpeechRecognition() || new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US'; // Change the language code as needed

    recognition.onresult = function(event) {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                interimTranscript += event.results[i][0].transcript + ' ';
            }
        }
        if (interimTranscript !== '') {
            output.innerHTML += '<p><strong>Transcribed Text:</strong> ' + interimTranscript + '</p>';
            fetch('/generate_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({transcribedText: interimTranscript})
            })
            .then(response => response.json())
            .then(data => {
                output.innerHTML += '<p><strong>Generated Text:</strong> ' + data.generatedText + '</p>';
                outputContainer.scrollTop = outputContainer.scrollHeight;
            })
            .catch(error => console.error('Error:', error));
        }
    };

    recognition.onstart = function() {
        startBtn.textContent = 'Stop Recording';
    };

    recognition.onend = function() {
        startBtn.textContent = 'Start Recording';
    };

    recognition.start();
}

function stopRecognition() {
    if (recognition) {
        recognition.onend = null; // Prevent restarting
        recognition.stop();
    }
}

function clearText() {
    output.innerHTML = '';
}

startBtn.addEventListener('click', function() {
    if (recognition && recognition.running) {
        stopRecognition();
    } else {
        output.innerHTML = '';
        startRecognition();
    }
});

clearBtn.addEventListener('click', clearText);
