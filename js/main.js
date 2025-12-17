// Load art palettes for dynamic styling
let artPalettes = null;
fetch('/assets/art_palettes.json')
  .then(response => response.json())
  .then(data => {
    artPalettes = data;
    console.log('Art palettes loaded:', artPalettes);
  })
  .catch(err => console.log('Could not load art palettes:', err));

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
                const response = await fetch('/api/query', {
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
    
    // Pick a random drawing's palette if available
    let bgGradient = 'linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)';
    let borderColor = '#9c27b0';
    let textColor = '#222';
    let usedPalette = null;
    
    if (artPalettes) {
        const paletteKeys = Object.keys(artPalettes);
        const randomKey = paletteKeys[Math.floor(Math.random() * paletteKeys.length)];
        const randomPalette = artPalettes[randomKey];
        usedPalette = randomKey;
        
        const colors = randomPalette.hex;
        
        // Use vivid colors for gradient and border
        bgGradient = `linear-gradient(135deg, ${colors[0]}22 0%, ${colors[1]}33 100%)`;
        borderColor = colors[2] || colors[0];
        
        console.log(`Using colors from drawing: ${randomKey}`, colors);
    }
    
    let html = `<div style="margin-top: 30px;">`;
    html += `<h3 style="color: #333; margin-bottom: 10px;">Response to: "${data.query}"</h3>`;
    
    // Show which drawing's colors are being used
    if (usedPalette) {
        html += `<p style="font-size: 0.85em; color: #666; font-style: italic; margin-bottom: 20px;">
            🎨 Styled with colors from drawing: ${usedPalette}
        </p>`;
    }

    // Display unique collage if available
    if (data.collage) {
        html += `<div style="margin: 20px 0; text-align: center;">
            <img src="${data.collage}" 
                 style="max-width: 100%; 
                        border-radius: 8px; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                        border: 3px solid #e0e0e0;" 
                 alt="Unique collage from art therapy drawings">
            <p style="font-size: 0.85em; color: #666; margin-top: 8px; font-style: italic;">
                A unique composition created from fragments of drawings
            </p>
        </div>`;
    }
    //end section of collage code

    
    // Generated answer with dynamic colors from art
    if (data.generated_answer) {
        const paragraphs = data.generated_answer.split('\n\n').filter(p => p.trim());
        
        html += `<div style="background: ${bgGradient}; 
                        padding: 25px; 
                        margin: 20px 0; 
                        border-left: 5px solid ${borderColor}; 
                        border-radius: 8px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                        font-size: 1.05em; 
                        line-height: 1.7;
                        color: ${textColor};">`;
        
        paragraphs.forEach((para, i) => {
            const marginTop = i > 0 ? 'margin-top: 15px;' : '';
            html += `<p style="${marginTop} margin-bottom: 0;">${para}</p>`;
        });
        
        html += `</div>`;
    }
    
    // Collapsible sources
    html += `<details style="margin: 25px 0; 
                            border: 2px solid #ddd; 
                            border-radius: 8px; 
                            padding: 10px;
                            background: #fafafa;">
        <summary style="cursor: pointer; 
                       font-weight: bold; 
                       padding: 10px; 
                       color: #555;
                       font-size: 1.05em;">
            View Materials (${data.dialogic_sources.length + data.intellectual_sources.length} sources)
        </summary>
        <div style="padding: 15px;">`;
    
    // Dialogic sources
    html += `<I style="color: #333; margin-top: 10px;">from my gpt conversations</I>`;
    data.dialogic_sources.forEach((source, i) => {
        html += `
        <div style="background: #f5f5f5; 
                    padding: 12px; 
                    margin: 10px 0; 
                    border-left: 3px solid #888; 
                    border-radius: 4px;
                    font-size: 0.9em;">
            <strong style="color: #333;">${source.metadata.conversation_title}</strong> 
            <span style="color: #888; font-size: 0.85em;">(${source.metadata.timestamp.split(' ')[0]})</span><br>
            <p style="margin-top: 8px; color: #555;">${source.content.substring(0, 200)}...</p>
        </div>`;
    });
    
    // Intellectual sources
    html += `<I style="color: #333; margin-top: 20px;">from semester notes</I>`;
    data.intellectual_sources.forEach((source, i) => {
        html += `
        <div style="background: #f0f0f0; 
                    padding: 12px; 
                    margin: 10px 0; 
                    border-left: 3px solid #666; 
                    border-radius: 4px;
                    font-size: 0.9em;">
            <p style="color: #555;">${source.content.substring(0, 200)}...</p>
        </div>`;
    });
    
    html += `</div></details></div>`;
    
    outputDiv.innerHTML = html;
}