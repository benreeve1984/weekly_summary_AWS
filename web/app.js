document.addEventListener('DOMContentLoaded', () => {
    const API_ENDPOINT = 'YOUR_API_GATEWAY_URL';
    
    async function fetchData() {
        try {
            const response = await fetch(`${API_ENDPOINT}/hello`);
            const data = await response.json();
            document.getElementById('response').textContent = data.message;
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('response').textContent = 'Error fetching data';
        }
    }

    fetchData();
}); 