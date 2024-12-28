document.addEventListener('DOMContentLoaded', () => {
    const API_ENDPOINT = 'https://vys5g98ar0.execute-api.eu-west-2.amazonaws.com/Prod/get-workouts';
    
    // Get DOM elements
    const form = document.getElementById('workoutForm');
    const retrieveButton = document.getElementById('retrieveButton');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const workoutDisplay = document.getElementById('workoutDisplay');
    const markdownContent = document.getElementById('markdownContent');
    const copyButton = document.getElementById('copyButton');
    const copyTooltip = document.getElementById('copyTooltip');

    // Form submission handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form data
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        // Reset UI state
        errorMessage.classList.add('hidden');
        workoutDisplay.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
        retrieveButton.disabled = true;

        try {
            // Make API request
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to retrieve workouts');
            }

            // Display markdown content
            markdownContent.innerHTML = marked.parse(data.markdown);
            workoutDisplay.classList.remove('hidden');
            form.reset();

        } catch (error) {
            // Handle errors
            errorMessage.textContent = error.message;
            errorMessage.classList.remove('hidden');
        } finally {
            // Reset UI state
            loadingSpinner.classList.add('hidden');
            retrieveButton.disabled = false;
        }
    });

    // Copy markdown button handler
    copyButton.addEventListener('click', async () => {
        try {
            const markdownText = markdownContent.textContent;
            await navigator.clipboard.writeText(markdownText);
            
            // Show success tooltip
            copyTooltip.classList.remove('hidden');
            setTimeout(() => {
                copyTooltip.classList.add('hidden');
            }, 2000);
        } catch (error) {
            console.error('Failed to copy text:', error);
        }
    });

    // Add touch event handling for mobile devices
    if ('ontouchstart' in window) {
        document.body.addEventListener('touchstart', function() {}, {passive: true});
    }
}); 