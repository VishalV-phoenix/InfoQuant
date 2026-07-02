// JavaScript controller for InfoQuant AI Learning Assistant

document.addEventListener("DOMContentLoaded", () => {
    const topicInput = document.getElementById("topic-input");
    const explainBtn = document.getElementById("explain-btn");
    const quizBtn = document.getElementById("quiz-btn");
    const clearBtn = document.getElementById("clear-btn");
    const chatContainer = document.getElementById("chat-container");
    const historyList = document.getElementById("history-list");
    const toastContainer = document.getElementById("toast-container");

    let currentTopic = "";

    // Initialize conversation feed and load session history sidebar
    initConversation();
    loadHistorySidebar();

    // Event listener for the "Explain" button click
    explainBtn.addEventListener("click", () => handleExplain());
    topicInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            handleExplain();
        }
    });

    // Event listener for the "Generate Quiz" button click
    quizBtn.addEventListener("click", () => handleQuiz());

    // Event listener for clearing history
    clearBtn.addEventListener("click", () => handleClear());

    async function handleExplain(prefilledQuery = null) {
        const query = prefilledQuery || (topicInput.value.strip ? topicInput.value.strip() : topicInput.value.trim());
        if (!query) return;

        topicInput.value = "";
        currentTopic = query;
        
        // Hide welcome/startup screen if present
        const welcome = document.querySelector(".welcome-container");
        if (welcome) {
            welcome.style.display = "none";
        }

        // Disable input buttons during load
        explainBtn.disabled = true;
        quizBtn.disabled = true;

        // Append temporary loading bubble at the bottom of chat feed
        const loadBubble = document.createElement("div");
        loadBubble.className = "message-bubble temp-loader-bubble";
        loadBubble.innerHTML = `
            <div class="spinner" style="width: 20px; height: 20px; display: inline-block; margin-right: 10px; border-top-color: #3b82f6; vertical-align: middle;"></div>
            <span style="color: #94a3b8; font-size: 0.9rem; font-style: italic; vertical-align: middle;">Querying Google Developer Knowledge MCP and building explanation...</span>
        `;
        chatContainer.appendChild(loadBubble);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const response = await fetch("/explain", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query })
            });
            const data = await response.json();

            explainBtn.disabled = false;

            if (data.safe === false) {
                // Prompt injection blocked - remove temp loader, append security alert card
                loadBubble.remove();
                
                const securityCard = document.createElement("div");
                securityCard.className = "message-bubble security-card";
                securityCard.innerHTML = `
                    <div class="card-header-decorator">
                        <i class="fa-solid fa-shield-halved"></i> Security Guardrail Alert
                    </div>
                    <h3>Instruction Intercepted</h3>
                    <p>${data.response}</p>
                `;
                chatContainer.appendChild(securityCard);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                showToast("Request blocked by security guardrails.", "error");
                quizBtn.disabled = true;
            } else {
                // Turn the loading bubble into the explanation response card
                loadBubble.classList.remove("temp-loader-bubble");
                loadBubble.classList.add("explanation-card");
                loadBubble.setAttribute("data-topic", currentTopic);
                loadBubble.innerHTML = `
                    <div class="card-header-decorator">
                        <i class="fa-solid fa-book"></i> Explanation Lesson
                    </div>
                    ${marked.parse(data.response)}
                `;
                
                quizBtn.disabled = false;
                loadHistorySidebar(); // Refresh history sidebar
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        } catch (err) {
            explainBtn.disabled = false;
            // Remove the loading bubble since the API request failed, and show a temporary toast
            loadBubble.remove();
            showToast(`Server error: ${err.message}`, "error");
        }
    }

    async function handleQuiz() {
        if (!currentTopic) return;

        explainBtn.disabled = true;
        quizBtn.disabled = true;

        // Append temporary loading bubble at the bottom of chat feed
        const loadBubble = document.createElement("div");
        loadBubble.className = "message-bubble quiz-bubble temp-loader-bubble";
        loadBubble.innerHTML = `
            <div class="spinner" style="width: 20px; height: 20px; display: inline-block; margin-right: 10px; border-top-color: #a855f7; vertical-align: middle;"></div>
            <span style="color: #c084fc; font-size: 0.9rem; font-style: italic; vertical-align: middle;">Tutor Agent is compiling a 5-question multiple choice quiz...</span>
        `;
        chatContainer.appendChild(loadBubble);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const response = await fetch("/quiz", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic: currentTopic })
            });
            const data = await response.json();

            explainBtn.disabled = false;
            quizBtn.disabled = false;

            // Turn the loading bubble into the quiz response card
            loadBubble.classList.remove("temp-loader-bubble");
            loadBubble.setAttribute("data-quiz-for", currentTopic);
            loadBubble.innerHTML = `
                <div class="card-header-decorator">
                    <i class="fa-solid fa-gamepad"></i> Knowledge Check Quiz
                </div>
                ${marked.parse(data.response)}
            `;
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } catch (err) {
            explainBtn.disabled = false;
            quizBtn.disabled = false;
            // Remove the loading bubble since the request failed, and show a temporary toast
            loadBubble.remove();
            showToast(`Quiz error: ${err.message}`, "error");
        }
    }

    async function handleClear() {
        if (confirm("Are you sure you want to clear your session memory?")) {
            await fetch("/history/clear", { method: "POST" });
            currentTopic = "";
            quizBtn.disabled = true;
            renderWelcomeScreen();
            loadHistorySidebar();
        }
    }

    function renderWelcomeScreen() {
        chatContainer.innerHTML = `
            <div class="welcome-container">
                <div class="welcome-header">
                    <h2>Welcome to InfoQuant AI</h2>
                    <p>Learn technical concepts through AI-powered research, simplified explanations, and interactive quizzes.</p>
                </div>
                
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon"><i class="fa-solid fa-book"></i></div>
                        <h3>📚 Explain Concepts</h3>
                        <p>Understand difficult technical topics using the Research Agent and Tutor Agent.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon"><i class="fa-solid fa-magnifying-glass"></i></div>
                        <h3>🔍 Google Developer Knowledge</h3>
                        <p>Research is grounded using Google's official Developer Knowledge MCP.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon"><i class="fa-solid fa-pencil"></i></div>
                        <h3>📝 Quizzes</h3>
                        <p>Test your understanding after every lesson with automatically generated quizzes.</p>
                    </div>
                </div>

                <div class="getting-started">
                    <h4>Try asking:</h4>
                    <ul id="starter-prompts">
                        <li data-prompt="What is a Transformer?">What is a Transformer?</li>
                        <li data-prompt="Explain CNNs">Explain CNNs</li>
                        <li data-prompt="What is Vertex AI?">What is Vertex AI?</li>
                        <li data-prompt="What is Google Cloud Storage?">What is Google Cloud Storage?</li>
                    </ul>
                </div>
            </div>
        `;

        // Add event listeners to starter prompt buttons
        document.querySelectorAll("#starter-prompts li").forEach(li => {
            li.addEventListener("click", () => {
                const promptText = li.getAttribute("data-prompt");
                handleExplain(promptText);
            });
        });
    }

    async function initConversation() {
        try {
            const response = await fetch("/history");
            const data = await response.json();
            
            if (data.history.length === 0) {
                renderWelcomeScreen();
                return;
            }

            chatContainer.innerHTML = "";
            data.history.forEach((turn) => {
                const bubble = document.createElement("div");
                bubble.className = "message-bubble explanation-card";
                bubble.setAttribute("data-topic", turn.topic);
                bubble.innerHTML = `
                    <div class="card-header-decorator">
                        <i class="fa-solid fa-book"></i> Explanation Lesson
                    </div>
                    ${marked.parse(turn.response)}
                `;
                chatContainer.appendChild(bubble);
            });
            
            // Set the active learning topic to the latest topic
            if (data.topics && data.topics.length > 0) {
                currentTopic = data.topics[data.topics.length - 1];
                quizBtn.disabled = false;
            }
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
        } catch (err) {
            console.error("Error initializing conversation:", err);
            renderWelcomeScreen();
        }
    }

    async function loadHistorySidebar() {
        try {
            const response = await fetch("/history");
            const data = await response.json();
            
            historyList.innerHTML = "";
            if (data.history.length === 0) {
                historyList.innerHTML = `<p class="empty-text">No topics discussed yet.</p>`;
                return;
            }

            data.history.forEach((turn) => {
                const item = document.createElement("div");
                item.className = "history-item";
                item.innerHTML = `<i class="fa-solid fa-book-open"></i> ${turn.topic}`;
                item.addEventListener("click", () => {
                    currentTopic = turn.topic;
                    quizBtn.disabled = false;
                    
                    // Scroll directly to the explanation card in the conversation feed
                    const element = document.querySelector(`[data-topic="${turn.topic}"]`);
                    if (element) {
                        element.scrollIntoView({ behavior: "smooth", block: "start" });
                    }
                });
                historyList.appendChild(item);
            });
        } catch (err) {
            console.error("Error loading history sidebar:", err);
        }
    }

    // Toast helper function
    function showToast(message, type = "error") {
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        
        let icon = "fa-triangle-exclamation";
        if (type === "success") icon = "fa-circle-check";
        if (type === "info") icon = "fa-circle-info";

        toast.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${message}</span>
            <button class="toast-close">&times;</button>
        `;
        
        toastContainer.appendChild(toast);

        // Add dismiss listener to click
        toast.querySelector(".toast-close").addEventListener("click", () => {
            toast.remove();
        });

        // Auto remove toast after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
});

// Modal Alert controls
function showModal(message) {
    document.getElementById("alert-message").textContent = message;
    document.getElementById("alert-modal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("alert-modal").classList.add("hidden");
}
