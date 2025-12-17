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
    
    let html = `<div style="margin-top: 30px;">`;
    
    html += `<h3 style="color:rgb(10, 2, 67); margin-bottom: 20px;">Response to: "${data.query}"</h3>`;
    
    if (data.generated_answer) {
        // Split by double newlines but render with single line breaks
        const paragraphs = data.generated_answer.split('\n\n').filter(p => p.trim());
        
        html += `<div style="background: linear-gradient(135deg,rgb(142, 225, 255) 0%,rgb(160, 212, 247) 100%); 
                        padding: 25px; 
                        margin: 20px 0; 
                        border-left: 5px solid rgb(10, 2, 67); 
                        border-radius: 8px;
                        box-shadow: 0 2px 8px rgba(9, 9, 9, 0.2);
                        font-size: 1.05em; 
                        line-height: 1.7;
                        color: #333;">`;
        
        paragraphs.forEach((para, i) => {
            // Add spacing between paragraphs but not excessive breaks
            const marginTop = i > 0 ? 'margin-top: 15px;' : '';
            html += `<p style="${marginTop} margin-bottom: 0;">${para}</p>`;
        });
        
        html += `</div>`;
    }
    
    // Collapsible sources 
    html += `<details style="margin: 25px 0; 
                            border: 2px solidrgb(3, 164, 119); 
                            border-radius: 8px; 
                            padding: 10px;
                            background:rgb(46, 184, 124);">
        <summary style="cursor: pointer; 
                       font-weight: bold; 
                       padding: 10px; 
                       color:rgb(234, 255, 234);
                       font-size: 1.05em;">
            Explore My Source Materials (${data.dialogic_sources.length + data.intellectual_sources.length} sources)
        </summary>
        <div style="padding: 15px;">`;
    
    // Dialogic sources
    html += `<I style="color:rgb(255, 255, 255); margin-top: 10px;">from my gpt conversations</I>`;
    data.dialogic_sources.forEach((source, i) => {
        html += `
        <div style="background:rgb(230, 229, 245); 
                    padding: 12px; 
                    margin: 10px 0; 
                    border-left: 3px solidrgb(127, 82, 135); 
                    border-radius: 4px;
                    font-size: 0.9em;">
            <strong style="color:rgb(48, 94, 163);">${source.metadata.conversation_title}</strong> 
            <span style="color: #888; font-size: 0.85em;">(${source.metadata.timestamp.split(' ')[0]})</span><br>
            <p style="margin-top: 8px; color: #555;">${source.content.substring(0, 200)}...</p>
        </div>`;
    });
    
    // Intellectual sources
    html += `<I style="color:rgb(255, 255, 255); margin-top: 20px;">from semester notes</I>`;
    data.intellectual_sources.forEach((source, i) => {
        html += `
        <div style="background: rgb(230, 229, 245); 
                    padding: 12px; 
                    margin: 10px 0; 
                    border-left: 3px solid rgb(53, 49, 102); 
                    border-radius: 4px;
                    font-size: 0.9em;">
            <p style="color: #555;">${source.content.substring(0, 200)}...</p>
        </div>`;
    });
    
    html += `</div></details></div>`;
    
    outputDiv.innerHTML = html;
}