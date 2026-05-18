document.addEventListener("DOMContentLoaded", () => {
    const endpoint = document.body.dataset.chatEndpoint || "/chat/query";
    const chatForm = document.getElementById("chatForm");
    const chatLog = document.getElementById("chatLog");
    const questionInput = document.getElementById("questionInput");
    const sendButton = document.getElementById("sendButton");
    const errorContainer = document.getElementById("errorContainer");
    const audienceSelect = document.getElementById("audience");
    const toneSelect = document.getElementById("tone");
    const taskSelect = document.getElementById("task");

    if (!chatForm || !chatLog || !questionInput || !sendButton || !errorContainer) {
        return;
    }

    const initialButtonText = sendButton.textContent;

    function clearWelcomeCard() {
        const welcomeCard = chatLog.querySelector(".welcome-card");
        if (welcomeCard) {
            welcomeCard.remove();
        }
    }

    function smoothScrollToBottom() {
        chatLog.scrollTo({
            top: chatLog.scrollHeight,
            behavior: "smooth",
        });
    }

    function appendMessage(role, message, extraClass = "") {
        clearWelcomeCard();

        const messageNode = document.createElement("article");
        messageNode.className = `message ${role} ${extraClass}`.trim();
        messageNode.textContent = message;

        chatLog.appendChild(messageNode);
        smoothScrollToBottom();
        return messageNode;
    }

    function setError(message) {
        errorContainer.textContent = message || "";
    }

    function setLoadingState(isLoading) {
        sendButton.disabled = isLoading;
        sendButton.textContent = isLoading ? "Sending..." : initialButtonText;
        questionInput.readOnly = isLoading;
    }

    async function parseResponse(response) {
        const contentType = response.headers.get("content-type") || "";

        if (contentType.includes("application/json")) {
            return response.json();
        }

        const text = await response.text();
        return { error: text || "Unexpected response from server." };
    }

    async function submitPrompt() {
        const question = questionInput.value.trim();
        if (!question) {
            setError("Please enter a prompt before submitting.");
            return;
        }

        setError("");
        appendMessage("user", question);
        questionInput.value = "";
        setLoadingState(true);

        const loadingNode = appendMessage("assistant", "Generating grounded response...", "loading");

        const payload = {
            question,
            audience: audienceSelect ? audienceSelect.value : "general",
            tone: toneSelect ? toneSelect.value : "professional",
            task: taskSelect ? taskSelect.value : "explain",
        };

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const data = await parseResponse(response);
            loadingNode.remove();

            if (!response.ok) {
                const errorMessage = data.error || "Request failed. Please try again.";
                setError(errorMessage);
                appendMessage("assistant", `Error: ${errorMessage}`);
                return;
            }

            const answer = data.response || "No response generated.";
            appendMessage("assistant", answer);
        } catch (_error) {
            loadingNode.remove();
            const message = "Network error while contacting /chat/query.";
            setError(message);
            appendMessage("assistant", `Error: ${message}`);
        } finally {
            setLoadingState(false);
            questionInput.focus();
        }
    }

    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        await submitPrompt();
    });

    questionInput.addEventListener("keydown", async (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            await submitPrompt();
        }
    });

    questionInput.focus();
});
