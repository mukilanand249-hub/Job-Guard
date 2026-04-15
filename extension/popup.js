document.getElementById('scanBtn').addEventListener('click', async () => {
    const btn = document.getElementById('scanBtn');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');

    btn.disabled = true;
    btn.innerText = 'Scanning...';
    resultDiv.style.display = 'none';
    errorDiv.innerText = '';

    try {
        // Get current tab URL
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab.url || tab.url.startsWith('chrome://') || tab.url.startsWith('edge://') || tab.url.startsWith('about:')) {
            throw new Error('Cannot scan system or browser settings pages. Please navigate to a real job posting.');
        }

        // Extract text from the page explicitly using chrome.scripting
        const executionResults = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => document.body.innerText
        });

        if (!executionResults || !executionResults[0] || !executionResults[0].result) {
            throw new Error('Could not extract text from this page.');
        }

        const extractedText = executionResults[0].result;

        // Call local API sending BOTH the url for history and text for processing
        let response;
        try {
            response = await fetch('http://127.0.0.1:8000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: tab.url, text: extractedText })
            });
        } catch (fetchErr) {
            throw new Error('Could not connect to AI server. Is the Django backend running on port 8000?');
        }

        const data = await response.json();

        if (data.error) throw new Error(data.error);

        // Render results
        resultDiv.style.display = 'block';

        const verdictBadge = document.getElementById('verdictBadge');
        verdictBadge.innerText = data.verdict;
        verdictBadge.className = `verdict ${data.verdict}`;

        document.getElementById('trustScore').innerText = `${data.trust_score}/100`;
        document.getElementById('summary').innerText = data.analysis_summary;

    } catch (e) {
        errorDiv.innerText = 'Error: ' + e.message;
    } finally {
        btn.disabled = false;
        btn.innerText = 'Scan This Page';
    }
});
