// Home Page Logic

let currentSessionId = null;
let statusCheckInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const uploadArea = document.getElementById('uploadArea');

    // Drag and drop
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#667eea';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '#E2E8F0';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#E2E8F0';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            showFileName(files[0].name);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            showFileName(e.target.files[0].name);
        }
    });

    uploadForm.addEventListener('submit', handleUpload);
});

function showFileName(name) {
    const container = document.getElementById('fileNameContainer');
    const nameSpan = document.getElementById('fileName');
    nameSpan.textContent = `✓ ${name}`;
    container.style.display = 'block';
}

async function handleUpload(e) {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const title = document.getElementById('title').value;
    const domain = document.getElementById('domain').value;
    const minConfidence = parseFloat(document.getElementById('minConfidence').value);

    if (!fileInput.files[0]) {
        showToast('Please select a file', 'error');
        return;
    }

    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Uploading...';

    try {
        const result = await api.uploadRFP(fileInput.files[0], title, domain, minConfidence);
        currentSessionId = result.session_id;

        // Start polling status; page-level handler controls visible state
        pollStatus(result.session_id);

    } catch (error) {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze RFP';
    }
}

async function pollStatus(sessionId) {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }

    statusCheckInterval = setInterval(async () => {
        try {
            const status = await api.getStatus(sessionId);
            
            // Update progress
            document.getElementById('progressFill').style.width = `${status.progress}%`;
            document.getElementById('progressFill').textContent = `${status.progress}%`;
            document.getElementById('progressText').textContent = status.status.toUpperCase();
            document.getElementById('stepText').textContent = status.current_step;

            if (status.status === 'completed') {
                clearInterval(statusCheckInterval);
                showComplete(status.requirements_count);
            } else if (status.status === 'failed') {
                clearInterval(statusCheckInterval);
                showError(status.error);
            }
        } catch (error) {
            clearInterval(statusCheckInterval);
            showError(error.message);
        }
    }, 1000);
}

function showComplete(count) {
    console.log('showComplete in home.js called with count:', count);

    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.classList.remove('show');
    }

    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze RFP';
    }

    showToast(`Analysis complete! ${count} requirements extracted.`, 'success');
}

function showError(message) {
    document.getElementById('progressContainer').classList.remove('show');
    document.getElementById('analyzeBtn').disabled = false;
    document.getElementById('analyzeBtn').textContent = 'Analyze RFP';
    showToast(`Analysis failed: ${message}`, 'error');
}

function goToReview() {
    window.location.href = '/review';
}