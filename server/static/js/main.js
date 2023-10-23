document.addEventListener('DOMContentLoaded', function () {
    // Function to create and embed the chatbot iframe
    function embedChatbot() {
        const chatbotContainer = document.getElementById('chatbot-container');
        const iframe = document.createElement('iframe');
        
        // Calculate the available space for the iframe, considering the container's offset
        let availableSpace = window.innerHeight - chatbotContainer.getBoundingClientRect().top;
        
        // Set the iframe height to the available space
        let iframeHeight = availableSpace;  // Use all available space for the iframe
        
        iframe.src = '/chatbot'; // URL of the chatbot.html page
        iframe.frameBorder = 0;
        iframe.width = '100%';
        iframe.height = iframeHeight + 'px';  // Dynamically set the height
        
        chatbotContainer.appendChild(iframe);
    }
    
    // Call the function to embed the chatbot when the page loads
    embedChatbot();
});
document.addEventListener('DOMContentLoaded', function () {
    // 为 <h2> 添加样式
    let h2Elements = document.querySelectorAll('h2');
    h2Elements.forEach(function(h2) {
        h2.classList.add('custom-h2');
    });

    // 为 <p> 添加样式
    let pElements = document.querySelectorAll('p');
    pElements.forEach(function(p) {
        p.classList.add('custom-p');
    });

    // 为 <ul> 添加样式
    let ulElements = document.querySelectorAll('ul');
    ulElements.forEach(function(ul) {
        ul.classList.add('custom-ul');
    });

    // 为 <li> 添加样式
    let liElements = document.querySelectorAll('li');
    liElements.forEach(function(li) {
        li.classList.add('custom-li');
    });
});