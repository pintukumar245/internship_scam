document.addEventListener('DOMContentLoaded', () => {
    // 1. Loading Screen Messages Cycling
    const searchForm = document.getElementById('search-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message');
    
    const loadingSteps = [
        "Analyzing company digital footprint...",
        "Scanning database for known internship flags...",
        "Checking DuckDuckGo Instant Answer databases...",
        "Searching web indices for student scam complaints...",
        "Evaluating fee demands and certificate legitimacy...",
        "Calculating safety index score..."
    ];
    
    if (searchForm && loadingOverlay && loadingMessage) {
        searchForm.addEventListener('submit', () => {
            loadingOverlay.style.display = 'flex';
            let stepIndex = 0;
            
            // Cycle through messages every 1.5 seconds
            const interval = setInterval(() => {
                stepIndex = (stepIndex + 1) % loadingSteps.length;
                loadingMessage.textContent = loadingSteps[stepIndex];
            }, 1500);
            
            // Store interval ID on window to clean up if needed
            window.loadingInterval = interval;
        });
    }

    // 2. Scam Meter SVG Progress Animation
    const radialBar = document.getElementById('radial-bar');
    const scoreVal = document.getElementById('score-value');
    
    if (radialBar && scoreVal) {
        // Read baseline score
        const baselineScore = parseInt(scoreVal.getAttribute('data-score')) || 0;
        updateRadialScore(baselineScore);
        
        // 3. Interactive Checklist Recalculations
        const checkboxes = document.querySelectorAll('.checklist-item input[type="checkbox"]');
        const statusText = document.getElementById('trust-status-text');
        
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                let currentScore = baselineScore;
                
                // Add values based on checklist audit selection
                checkboxes.forEach(cb => {
                    if (cb.checked) {
                        currentScore += parseInt(cb.getAttribute('data-weight')) || 0;
                    }
                });
                
                // Clamp between 0 and 100
                currentScore = Math.min(100, Math.max(0, currentScore));
                
                // Update score display
                scoreVal.textContent = currentScore + '%';
                scoreVal.setAttribute('data-score-current', currentScore);
                
                // Update radial progress circle
                updateRadialScore(currentScore);
                
                // Update status label & class
                updateStatusText(currentScore);
            });
        });
    }
    
    function updateRadialScore(score) {
        if (!radialBar) return;
        
        // Total circumference of circle is 2 * PI * r = 2 * 3.14159 * 70 = 439.82 (~440)
        const circumference = 440;
        const offset = circumference - (score / 100) * circumference;
        radialBar.style.strokeDashoffset = offset;
        
        // Update bar color class
        radialBar.className.baseVal = "radial-bar";
        if (score <= 35) {
            radialBar.classList.add('safe');
        } else if (score <= 70) {
            radialBar.classList.add('warning');
        } else {
            radialBar.classList.add('danger');
        }
    }
    
    function updateStatusText(score) {
        const statusText = document.getElementById('trust-status-text');
        if (!statusText) return;
        
        statusText.className = 'trust-status-text';
        
        if (score <= 35) {
            statusText.textContent = "SAFE / TRUSTWORTHY";
            statusText.classList.add('safe');
        } else if (score <= 70) {
            statusText.textContent = "WARNING / SUSPICIOUS";
            statusText.classList.add('warning');
        } else {
            statusText.textContent = "CRITICAL / SCAM RISK";
            statusText.classList.add('danger');
        }
    }
});
