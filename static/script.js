const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const status = document.getElementById('status');

// Initialize variables
let audioStream;
let mediaRecorder;
let chunks = [];

// Handle start recording button click event
startBtn.addEventListener('click', async () => {
    try {
        // Request access to the user's microphone
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Create a MediaRecorder instance to record audio
        mediaRecorder = new MediaRecorder(audioStream);

        // Clear any existing data in chunks array
        chunks = [];

        // Start recording
        mediaRecorder.start();

        // Update UI
        status.textContent = 'Recording...';
    } catch (error) {
        console.error('Error accessing microphone:', error);
    }
});

// Handle stop recording button click event
stopBtn.addEventListener('click', () => {
    // Stop recording
    mediaRecorder.stop();
});

// Listen for data available event to collect audio data
mediaRecorder.addEventListener('dataavailable', (event) => {
    chunks.push(event.data);
});

// Listen for recording stopped event to process the recorded audio
mediaRecorder.addEventListener('stop', () => {
    // Combine the recorded audio chunks into a single Blob
    const recordedBlob = new Blob(chunks, { type: 'audio/webm' });

    // store into a variable to send to server
    const reader = new FileReader();
    reader.onloadend = () => {
        // Transmit the binary data to the backend
        transmitAudio(reader.result);
    };
    reader.readAsArrayBuffer(recordedBlob);
    
});
function transmitAudio(audioData) {
    fetch('/process-audio', {
        method: 'POST',
        body: audioData,
        headers: {
            'Content-Type': 'audio/webm' // Set the appropriate content type
        }
    })
    .then(response => response.text())
    .then(data => {
        console.log('Server response:', data);
    })
    .catch(error => {
        console.error('Error transmitting audio:', error);
    });
}