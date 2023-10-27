document.addEventListener('DOMContentLoaded', function () {
    // Function to create and embed the chatbot iframe
    function embedChatbot() {
        const chatbotContainer = document.getElementById('chatbot-container');
        
        if (!chatbotContainer) return;  // Check if the container exists

        const iframe = document.createElement('iframe');
        let availableSpace = window.innerHeight - chatbotContainer.getBoundingClientRect().top;
        let iframeHeight = availableSpace;
        iframe.src = '/chatbot';
        iframe.frameBorder = 0;
        iframe.width = '100%';
        iframe.height = iframeHeight + 'px'; 
        chatbotContainer.appendChild(iframe);
    }

    embedChatbot();  // Call the function to embed the chatbot

    // Add styles
    ['h2', 'p', 'ul', 'li'].forEach(tag => {
        document.querySelectorAll(tag).forEach(el => {
            el.classList.add(`custom-${tag}`);
        });
    });
});
