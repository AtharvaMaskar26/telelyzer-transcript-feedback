// Global variables to store state
let audioId = '';
let transcriptions = [];

// Function to fetch transcriptions
async function fetchTranscriptions() {
  try {

    const sanitizedAudioId = audioId.replace(/-/g, "");
    const response = await fetch(`http://localhost:8000/api/transcriptions/${sanitizedAudioId}`);
    const data = await response.json();
    transcriptions = data;
    renderTranscriptions();
  } catch (error) {
    console.error('Error fetching transcriptions:', error);
  }
}

// Function to update transcription
async function updateTranscription(chunkId, newTranscript, originalTranscript) {
  try {
    const response = await fetch(`http://localhost:8000/api/transcriptions/${audioId}/${chunkId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        transcript: newTranscript,
        original_transcript: originalTranscript
      }),
    });
    if (response.ok) {
      console.log('Transcription updated successfully');
      // Update the local state to reflect the change
      transcriptions = transcriptions.map(t => 
        t.chunk_id === chunkId ? { ...t, transcript: newTranscript } : t
      );
      renderTranscriptions();
    } else {
      console.error('Failed to update transcription');
    }
  } catch (error) {
    console.error('Error updating transcription:', error);
  }
}

// Function to render transcriptions
function renderTranscriptions() {
  const transcriptionList = document.getElementById('transcriptionList');
  transcriptionList.innerHTML = '';

  transcriptions.forEach(({ chunk_id, transcript, original_transcript }) => {
    const item = document.createElement('div');
    item.className = 'transcription-item';
    
    const audio = document.createElement('audio');
    audio.controls = true;
    audio.src = `/data/audio_chunks/${audioId}-${chunk_id}.wav`;
    
    const textarea = document.createElement('textarea');
    textarea.value = transcript;
    
    const originalTranscriptDiv = document.createElement('div');
    originalTranscriptDiv.className = 'original-transcript';
    originalTranscriptDiv.textContent = `Original: ${original_transcript}`;
    
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.className = 'save-button';
    saveButton.addEventListener('click', () => updateTranscription(chunk_id, textarea.value, original_transcript));
    
    item.appendChild(audio);
    item.appendChild(textarea);
    item.appendChild(originalTranscriptDiv);
    item.appendChild(saveButton);
    transcriptionList.appendChild(item);
  });
}

// Function to initialize the app
function initApp() {
  const audioIdInput = document.getElementById('audioIdInput');
  const fetchButton = document.getElementById('fetchButton');

  audioIdInput.addEventListener('input', (e) => {
    audioId = e.target.value;
  });

  fetchButton.addEventListener('click', fetchTranscriptions);
}

// Initialize the app when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initApp);