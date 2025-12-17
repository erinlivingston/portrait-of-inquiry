// RAG Interface functionality
document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.getElementById('submit-btn');
    const promptInput = document.getElementById('prompt-input');
    const outputDiv = document.getElementById('output-div');
    const loadingDiv = document.getElementById('loading');
    
    console.log("RAG interface initialized");
    
    if (submitBtn && promptInput && outputDiv) {
        submitBtn.addEventListener('click', async () => {
            const userPrompt = promptInput.value.trim();
            
            if (!userPrompt) {
                alert('Please enter a query');
                return;
            }
            
            console.log("Querying:", userPrompt);
            
            // Show loading
            if (loadingDiv) loadingDiv.style.display = 'block';
            outputDiv.innerHTML = '';
            
            try {
                const response = await fetch('/api/query', {  // Changed from http://localhost:5000/query
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        prompt: userPrompt,
                        n_results: 3
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log("Results received:", data);
                
                console.log("Full API response:", data);  // debugging line
                console.log("Generated answer:", data.generated_answer);  // debugging line
                
                // Hide loading
                if (loadingDiv) loadingDiv.style.display = 'none';
                
                // Display results
                displayResults(data);
                
            } catch (error) {
                console.error("Fetch error:", error);
                if (loadingDiv) loadingDiv.style.display = 'none';
                outputDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            }
        });
    } else {
        console.error("Could not find required elements");
    }
});

function displayResults(data) {
    const outputDiv = document.getElementById('output-div');
    
    let html = `<h3>Results for: "${data.query}"</h3>`;
    
    // Show generated answer prominently
    if (data.generated_answer) {
        html += `<div style="background: #fff8e1; padding: 20px; margin: 20px 0; border-left: 4px solid #ffa726; font-size: 1.1em; line-height: 1.6;">
            ${data.generated_answer.replace(/\n/g, '<br><br>')}
        </div>`;
    }
    
    // Add collapsible sources section
    html += `<details style="margin: 20px 0;">
        <summary style="cursor: pointer; font-weight: bold; padding: 10px; background: #f5f5f5;">
            View Source Materials (${data.dialogic_sources.length + data.intellectual_sources.length} sources)
        </summary>
        <div style="padding: 10px;">`;
    
    // Dialogic sources
    html += `<h4>From Your ChatGPT Conversations</h4>`;
    data.dialogic_sources.forEach((source, i) => {
        html += `
        <div style="background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 3px solid #333; font-size: 0.9em;">
            <strong>${source.metadata.conversation_title}</strong> (${source.metadata.timestamp.split(' ')[0]})<br>
            <p style="margin-top: 10px;">${source.content.substring(0, 200)}...</p>
        </div>`;
    });
    
    // Intellectual sources
    html += `<h4>From Your Class Notes</h4>`;
    data.intellectual_sources.forEach((source, i) => {
        html += `
        <div style="background: #f0f8ff; padding: 15px; margin: 10px 0; border-left: 3px solid #4682b4; font-size: 0.9em;">
            <p>${source.content.substring(0, 200)}...</p>
        </div>`;
    });
    
    html += `</div></details>`;
    
    outputDiv.innerHTML = html;
}