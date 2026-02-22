// Debug version - Chat functionality
class ChatBot {
    constructor() {
        console.log('ChatBot constructor called'); // Debug log
        
        // Try to find elements and log their status
        this.chatButton = document.getElementById('chatButton');
        this.chatModal = document.getElementById('chatModal');
        this.chatOverlay = document.getElementById('chatOverlay');
        this.chatClose = document.getElementById('chatClose');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        
        // Debug: Log which elements were found
        console.log('Elements found:', {
            chatButton: !!this.chatButton,
            chatModal: !!this.chatModal,
            chatOverlay: !!this.chatOverlay,
            chatClose: !!this.chatClose,
            chatInput: !!this.chatInput,
            sendButton: !!this.sendButton,
            chatMessages: !!this.chatMessages
        });
        
        // If chatButton is not found, try alternative selectors
        if (!this.chatButton) {
            console.log('chatButton not found, trying alternative selectors...');
            this.chatButton = document.querySelector('.chat-button') || 
                            document.querySelector('[data-chat-button]') ||
                            document.querySelector('.chatbot-button') ||
                            document.querySelector('#chat-button');
            console.log('Alternative chatButton found:', !!this.chatButton);
        }
        
        this.apiUrl = '/api/faq';
        this.isOpen = false;
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        console.log('Initializing event listeners...');
        
        // Open chat
        if (this.chatButton) {
            this.chatButton.addEventListener('click', (e) => {
                console.log('Chat button clicked!');
                e.preventDefault();
                this.openChat();
            });
            console.log('Chat button event listener added');
        } else {
            console.error('Cannot add event listener: chatButton not found');
        }
        
        // Close chat
        if (this.chatClose) {
            this.chatClose.addEventListener('click', () => this.closeChat());
        }
        if (this.chatOverlay) {
            this.chatOverlay.addEventListener('click', () => this.closeChat());
        }
        
        // Send message
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
        if (this.chatInput) {
            this.chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
            
            // Auto-resize input
            this.chatInput.addEventListener('input', () => {
                this.chatInput.style.height = 'auto';
                this.chatInput.style.height = this.chatInput.scrollHeight + 'px';
            });
        }
    }
    
    openChat() {
        console.log('Opening chat...');
        this.isOpen = true;
        
        if (this.chatModal) {
            this.chatModal.classList.add('active');
            console.log('Added active class to chatModal');
        } else {
            console.error('chatModal not found');
        }
        
        if (this.chatOverlay) {
            this.chatOverlay.classList.add('active');
            console.log('Added active class to chatOverlay');
        } else {
            console.error('chatOverlay not found');
        }
        
        if (this.chatInput) {
            this.chatInput.focus();
        }
    }
    
    closeChat() {
        console.log('Closing chat...');
        this.isOpen = false;
        
        if (this.chatModal) {
            this.chatModal.classList.remove('active');
        }
        if (this.chatOverlay) {
            this.chatOverlay.classList.remove('active');
        }
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;
        
        console.log('Sending message:', message);
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        
        // Reset textarea height
        this.chatInput.style.height = 'auto';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to your Python backend
            const response = await this.callAPI(message);
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            this.addMessage(response, 'bot');
        } catch (error) {
            console.error('Error calling API:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again later.', 'bot');
        }
    }
    
    async callAPI(message) {
        try {
            console.log('Sending message to API:', message);
            
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message
                })
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('API Error:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('API Response:', data);
            
            return data.answer || 'No response received';
            
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }
    
    addMessage(content, sender) {
        if (!this.chatMessages) {
            console.error('chatMessages element not found');
            return;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    showTypingIndicator() {
        if (!this.chatMessages) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    hideTypingIndicator() {
        if (!this.chatMessages) return;
        
        const typingIndicator = this.chatMessages.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
}

// Add typing indicator styles
const typingStyles = `
    .typing-indicator .message-content {
        padding: 1rem !important;
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
        align-items: center;
    }
    
    .typing-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #666;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }
`;

// Add typing styles to document
const styleSheet = document.createElement('style');
styleSheet.textContent = typingStyles;
document.head.appendChild(styleSheet);

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing ChatBot...');
    new ChatBot();
});

// Add smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Add click handlers for buttons (you can customize these)
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('btn-secondary')) {
        // Handle "Learn More" button clicks
        console.log('Learn More clicked for:', e.target.closest('.card').querySelector('.card-title').textContent);
        // You can add navigation logic here
    }
    
    if (e.target.classList.contains('btn-primary')) {
        // Handle "Add to Profile" button clicks
        console.log('Add to Profile clicked for:', e.target.closest('.card').querySelector('.card-title').textContent);
        // You can add profile logic here
    }
    
    if (e.target.classList.contains('btn-profile-builder')) {
        // Handle "Go to Profile Builder" button click
        console.log('Go to Profile Builder clicked');
        // You can add navigation logic here
    }
});