// --- Main Extension Logic ---
document.addEventListener('DOMContentLoaded', () => {
    // --- Tab Elements ---
    const urlTabButton = document.getElementById('urlTabButton');
    const textTabButton = document.getElementById('textTabButton');
    const urlTabContent = document.getElementById('URL_Analysis');
    const textTabContent = document.getElementById('Text_Analysis');

    // --- URL Analysis Elements ---
    const analyzeButton = document.getElementById('analyze-button');
    // ... (rest of your element selectors are the same)
    const resultContainer = document.getElementById('result-container');
    const statusEl = document.getElementById('status');
    const messageEl = document.getElementById('message');
    const reasonsContainer = document.getElementById('reasons-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const currentUrlEl = document.getElementById('current-url');
    const urlDisplayBox = document.getElementById('url-display-box');

    // --- Text Analysis Elements ---
    const analyzeTextButton = document.getElementById('analyze-text-button');
    // ... (rest of your element selectors are the same)
    const textInput = document.getElementById('text-input');
    const textResultContainer = document.getElementById('text-result-container');
    const textStatusEl = document.getElementById('text-status');
    const textExplanationEl = document.getElementById('text-explanation');
    const textLoadingSpinner = document.getElementById('text-loading-spinner');

    // --- Tab Switching Logic ---
    urlTabButton.addEventListener('click', () => {
        urlTabContent.style.display = 'block';
        textTabContent.style.display = 'none';
        urlTabButton.classList.add('active');
        textTabButton.classList.remove('active');
    });

    textTabButton.addEventListener('click', () => {
        textTabContent.style.display = 'block';
        urlTabContent.style.display = 'none';
        textTabButton.classList.add('active');
        urlTabButton.classList.remove('active');
    });

    // --- Initial Setup for URL Tab ---
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs && tabs[0] && tabs[0].url) {
            const url = tabs[0].url;
            const displayUrl = url.match(/^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)/im);
            currentUrlEl.textContent = displayUrl ? displayUrl[1] : "Cannot get URL";
        } else {
            currentUrlEl.textContent = "Cannot access tab URL.";
        }
    });

    // --- Event Listener for URL Analysis Button ---
    analyzeButton.addEventListener('click', () => {
        // ... (Your existing analyzeButton logic is correct and stays the same)
        analyzeButton.disabled = true;
        resultContainer.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');

        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const url = tabs[0].url;
            fetch('http://127.0.0.1:5000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url }),
            })
            .then(response => {
                if (!response.ok) { throw new Error('Network response was not ok.'); }
                return response.json();
            })
            .then(data => { displayResult(data); })
            .catch(error => {
                console.error('URL Analysis Error:', error);
                displayError("Could not connect. Check the server terminal for errors.", "url");
            })
            .finally(() => {
                analyzeButton.disabled = false;
                loadingSpinner.classList.add('hidden');
            });
        });
    });

    // --- Event Listener for Text Analysis Button ---
    analyzeTextButton.addEventListener('click', () => {
        // ... (Your existing analyzeTextButton logic is correct and stays the same)
        const textToAnalyze = textInput.value;
        if (!textToAnalyze) return;

        analyzeTextButton.disabled = true;
        textResultContainer.classList.add('hidden');
        textLoadingSpinner.classList.remove('hidden');

        fetch('http://127.0.0.1:5000/analyze-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: textToAnalyze }),
        })
        .then(response => {
            if (!response.ok) { throw new Error('Network response was not ok.'); }
            return response.json();
        })
        .then(data => {
            textStatusEl.textContent = data.verdict;
            textExplanationEl.textContent = data.explanation;
            textStatusEl.className = data.verdict === "High Risk" ? 'status-high-risk' : 'status-safe';
            textResultContainer.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Text Analysis Error:', error);
            displayError("Could not connect. Is the server running and API key set?", "text");
        })
        .finally(() => {
            analyzeTextButton.disabled = false;
            textLoadingSpinner.classList.add('hidden');
        });
    });

    // --- Display Functions ---
    // ... (Your existing displayResult and displayError functions are correct and stay the same)
    function displayResult(data) {
        statusEl.textContent = data.status;
        messageEl.textContent = data.message;
        reasonsContainer.innerHTML = ''; 

        if (data.reasons && data.reasons.length > 0) {
            const ul = document.createElement('ul');
            data.reasons.forEach(reason => {
                const li = document.createElement('li');
                li.textContent = reason;
                ul.appendChild(li);
            });
            reasonsContainer.appendChild(ul);
        }

        if (data.status === 'Phishing') {
            statusEl.className = 'status-phishing';
            urlDisplayBox.className = 'url-display url-phishing';
        } else {
            statusEl.className = 'status-legitimate';
            urlDisplayBox.className = 'url-display url-legitimate';
        }
        resultContainer.classList.remove('hidden');
    }

    function displayError(errorMessage, type) {
        if (type === "url") {
            statusEl.textContent = 'Error';
            messageEl.textContent = errorMessage;
            statusEl.className = 'status-phishing';
            resultContainer.classList.remove('hidden');
        } else if (type === "text") {
            textStatusEl.textContent = 'Error';
            textExplanationEl.textContent = errorMessage;
            textStatusEl.className = 'status-high-risk';
            textResultContainer.classList.remove('hidden');
        }
    }
});