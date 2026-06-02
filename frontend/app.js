// Generate a unique session ID for the current conversation
const sessionId = 'session_' + Math.random().toString(36).substring(2, 15);

// DOM Elements
const micBtn = document.getElementById('mic-btn');
const audioWave = document.getElementById('audio-wave');
const voiceStatus = document.getElementById('voice-status');
const statusBanner = document.getElementById('status-banner');
const statusText = document.getElementById('status-text');
const chatMessages = document.getElementById('chat-messages');
const audioPlayer = document.getElementById('audio-player');
const playPauseBtn = document.getElementById('audio-play-pause-btn');
const miniWave = document.getElementById('mini-wave');
const reingestBtn = document.getElementById('reingest-btn');
const clearBtn = document.getElementById('clear-btn');
const playIcon = document.getElementById('play-icon');
const pauseIcon = document.getElementById('pause-icon');
const toast = document.getElementById('toast');

// Recording State Variables
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    setupMicEvents();
    setupAudioPlayerEvents();
    setupUtilityEvents();
});

// Setup Microphone events
function setupMicEvents() {
    micBtn.addEventListener('click', async () => {
        if (isRecording) {
            stopRecording();
        } else {
            await startRecording();
        }
    });
}

// Request permissions and start recording
async function startRecording() {
    audioChunks = [];

    // Stop audio player if it is currently playing
    if (!audioPlayer.paused) {
        audioPlayer.pause();
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Use standard webm if supported, fallback to default
        const options = MediaRecorder.isTypeSupported('audio/webm')
            ? { mimeType: 'audio/webm' }
            : {};

        mediaRecorder = new MediaRecorder(stream, options);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
            stream.getTracks().forEach(track => track.stop()); // Release mic
            await processAudio(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;

        // Update UI for recording state
        micBtn.classList.add('recording');
        audioWave.classList.add('active', 'recording');
        voiceStatus.textContent = 'Listening...';
        showStatus('Listening to your voice...', 'purple');

    } catch (err) {
        console.error('Error accessing microphone:', err);
        showToast('Microphone access denied or not supported.', true);
        resetUI();
    }
}

// Stop recording
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    isRecording = false;

    // Update UI for processing state
    micBtn.classList.remove('recording');
    micBtn.classList.add('processing');
    audioWave.classList.remove('recording');
    voiceStatus.textContent = 'Processing...';
}

// Process recorded audio
async function processAudio(audioBlob) {
    showStatus('Transcribing voice response...', 'purple');

    try {
        // 1. Transcribe the audio via backend
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio-record.webm');

        const transcribeResponse = await fetch('http://127.0.0.1:8001/api/transcribe', {
            method: 'POST',
            body: formData
        });

        if (!transcribeResponse.ok) {
            throw new Error('Transcription failed');
        }

        const transcribeData = await transcribeResponse.json();
        const transcript = transcribeData.transcript;

        if (!transcript || transcript.trim() === '') {
            showToast('Could not hear anything. Please try again.', true);
            resetUI();
            return;
        }

        // Add user transcript to the chat log
        appendMessage('user', 'You', transcript);

        // 2. Query the Chat Persona with the transcript
        showStatus('Thinking...', 'purple');
        voiceStatus.textContent = 'Thinking...';

        const chatResponse = await fetch('http://127.0.0.1:8001/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: transcript,
                session_id: sessionId
            })
        });

        if (!chatResponse.ok) {
            throw new Error('Chat generation failed');
        }

        const chatData = await chatResponse.json();

        // Add Persona response to the chat log
        appendMessage('assistant', 'Vinit', chatData.response);

        // 3. Play generated TTS response
        playAudioResponse(chatData.audio_url);

    } catch (err) {
        console.error('Processing error:', err);
        showToast('Error communicating with backend.', true);
        resetUI();
    }
}

// Play audio response
function playAudioResponse(audioUrl) {
    showStatus('Speaking...', 'pink');
    voiceStatus.textContent = 'Speaking...';

    audioPlayer.src = audioUrl;
    audioPlayer.load();

    audioPlayer.play()
        .then(() => {
            playPauseBtn.disabled = false;
            playIcon.classList.add('hidden');
            pauseIcon.classList.remove('hidden');
            miniWave.classList.add('playing');
        })
        .catch(err => {
            console.error('Audio playback failed:', err);
            showToast('Unable to autoplay response audio. Press Play.', false);
            playPauseBtn.disabled = false;
            playIcon.classList.remove('hidden');
            pauseIcon.classList.add('hidden');
            miniWave.classList.remove('playing');
        });
}

// Setup Audio Player UI Controls
function setupAudioPlayerEvents() {
    playPauseBtn.addEventListener('click', () => {
        if (audioPlayer.paused) {
            audioPlayer.play();
            playIcon.classList.add('hidden');
            pauseIcon.classList.remove('hidden');
            miniWave.classList.add('playing');
            showStatus('Speaking...', 'pink');
        } else {
            audioPlayer.pause();
            playIcon.classList.remove('hidden');
            pauseIcon.classList.add('hidden');
            miniWave.classList.remove('playing');
            showStatus('Playback paused', 'purple');
        }
    });

    audioPlayer.addEventListener('ended', () => {
        resetUI();
    });
}

// Setup Indexing & Clear Memory utilities
function setupUtilityEvents() {
    reingestBtn.addEventListener('click', async () => {
        reingestBtn.disabled = true;
        showToast('Re-indexing knowledge base...');

        try {
            const response = await fetch('http://127.0.0.1:8001/api/ingest', { method: 'POST' });
            if (response.ok) {
                showToast('Knowledge base successfully indexed!');
            } else {
                showToast('Failed to index documents.', true);
            }
        } catch (err) {
            showToast('Error connecting to backend.', true);
        } finally {
            reingestBtn.disabled = false;
        }
    });

    clearBtn.addEventListener('click', async () => {
        clearBtn.disabled = true;
        try {
            const response = await fetch('http://127.0.0.1:8001/api/clear', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });

            if (response.ok) {
                // Clear UI chat messages (except the first welcome message)
                const messages = Array.from(chatMessages.children);
                messages.slice(1).forEach(m => m.remove());
                showToast('Conversation memory cleared!');
            } else {
                showToast('Failed to clear memory.', true);
            }
        } catch (err) {
            showToast('Error connecting to backend.', true);
        } finally {
            clearBtn.disabled = false;
        }
    });
}

// Helper to Append a Chat Message
function appendMessage(role, sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', role);

    const avatar = document.createElement('div');
    avatar.classList.add('message-avatar');
    avatar.textContent = role === 'user' ? 'U' : 'V';

    const wrapper = document.createElement('div');
    wrapper.classList.add('message-bubble-wrapper');

    const senderSpan = document.createElement('div');
    senderSpan.classList.add('message-sender');
    senderSpan.textContent = sender;

    const bubble = document.createElement('div');
    bubble.classList.add('message-bubble');
    bubble.textContent = text;

    wrapper.appendChild(senderSpan);
    wrapper.appendChild(bubble);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(wrapper);

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
}

// Reset Control states to idle
function resetUI() {
    isRecording = false;
    micBtn.classList.remove('recording', 'processing');
    audioWave.classList.remove('active', 'recording');
    voiceStatus.textContent = 'Ready to Record';
    hideStatus();

    playPauseBtn.disabled = true;
    playIcon.classList.remove('hidden');
    pauseIcon.classList.add('hidden');
    miniWave.classList.remove('playing');
}

// Show Status banner
function showStatus(text, type = 'purple') {
    statusBanner.classList.remove('hidden');
    statusText.textContent = text;
}

// Hide Status banner
function hideStatus() {
    statusBanner.classList.add('hidden');
}

// Show Alert Toast
function showToast(message, isError = false) {
    toast.textContent = message;
    toast.className = 'toast show';
    if (isError) {
        toast.classList.add('error');
    }

    setTimeout(() => {
        toast.classList.remove('show', 'error');
    }, 3000);
}
