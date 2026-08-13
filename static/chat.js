// ============================================================
// JeevanSetu M3 CHAT.JS
// M3 UI -> M2 Backend on Render
// ============================================================

const API_URL = "https://jeevan-setu-1.onrender.com/api/v1/chat";

const messages = document.getElementById("messages");
const messageInput = document.getElementById("messageInput");
const composer = document.getElementById("composer");
const voiceButton = document.getElementById("voiceButton");
const resetButton = document.getElementById("resetButton");
const statusText = document.getElementById("status");


// ============================================================
// SESSION
// ============================================================

let sessionId = localStorage.getItem("jeevansetu_session_id");

if (!sessionId) {
    sessionId =
        "web-" +
        Date.now() +
        "-" +
        Math.random().toString(36).substring(2, 10);

    localStorage.setItem("jeevansetu_session_id", sessionId);
}


// ============================================================
// LANGUAGE DETECTION
// ============================================================

function detectLanguage(text) {

    // Marathi-specific words
    const marathiWords = [
        "आहे",
        "मला",
        "माझे",
        "माझा",
        "माझी",
        "काय",
        "कसे",
        "कशी",
        "दुखत",
        "ताप",
        "झाला",
        "झाली",
        "होतो",
        "होते",
        "करावे",
        "करायचे"
    ];

    if (marathiWords.some(word => text.includes(word))) {
        return "mr";
    }


    // Devanagari text
    if (/[\u0900-\u097F]/.test(text)) {
        return "hi";
    }


    // Hindi written using English letters
    const hindiRomanWords = [
        "mujhe",
        "mujh",
        "mera",
        "meri",
        "mere",
        "hai",
        "hain",
        "mujko",
        "bukhar",
        "sar",
        "dard",
        "khansi",
        "saans",
        "pet",
        "nahi",
        "nahin",
        "raha",
        "rahi",
        "ho",
        "kya"
    ];

    const lower = text.toLowerCase();

    if (
        hindiRomanWords.some(word =>
            lower.split(/\s+/).includes(word)
        )
    ) {
        return "hi";
    }


    return "en";
}


// ============================================================
// ADD CHAT BUBBLE
// ============================================================

function addMessage(text, type, language = null, emergency = false) {

    const bubble = document.createElement("div");

    bubble.classList.add("bubble");

    if (type === "user") {
        bubble.classList.add("user");
    } else {
        bubble.classList.add("bot");
    }

    if (emergency) {
        bubble.classList.add("emergency");
    }


    // Message text
    const messageText = document.createElement("div");

    messageText.textContent = text;

    bubble.appendChild(messageText);


    // Bot metadata
    if (type === "bot") {

        const meta = document.createElement("div");

        meta.classList.add("meta");

        let languageName = "English";

        if (language === "hi") {
            languageName = "Hindi";
        }

        if (language === "mr") {
            languageName = "Marathi";
        }

        meta.textContent =
            languageName + " • M2 connected";

        bubble.appendChild(meta);
    }


    messages.appendChild(bubble);

    messages.scrollTop = messages.scrollHeight;

    return bubble;
}


// ============================================================
// WELCOME MESSAGE
// ============================================================

function showWelcome() {

    messages.innerHTML = "";

    addMessage(
        "Welcome to JeevanSetu AI.\nAsk your health question in English, Hindi, or Marathi.",
        "bot",
        null
    );
}


// ============================================================
// TYPING INDICATOR
// ============================================================

function showTyping() {

    const typing = document.createElement("div");

    typing.id = "typingIndicator";

    typing.classList.add("typing");

    typing.textContent = "JeevanSetu is typing...";

    messages.appendChild(typing);

    messages.scrollTop = messages.scrollHeight;
}


function hideTyping() {

    const typing =
        document.getElementById("typingIndicator");

    if (typing) {
        typing.remove();
    }
}


// ============================================================
// SEND MESSAGE TO M2
// ============================================================

async function sendMessage(text) {

    text = text.trim();

    if (!text) {
        return;
    }


    // Detect language BEFORE sending
    const language = detectLanguage(text);

    console.log("Message:", text);
    console.log("Detected language:", language);


    // Show user bubble
    addMessage(
        text,
        "user"
    );


    // Clear input
    messageInput.value = "";


    // Show typing
    showTyping();


    try {

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },

            body: JSON.stringify({

                session_id: sessionId,

                message: text,

                language: language,

                channel: "web"
            })
        });


        hideTyping();


        // HTTP error
        if (!response.ok) {

            console.error(
                "M2 HTTP error:",
                response.status
            );

            addMessage(
                "Sorry, I am unable to generate a response right now. Please try again in a moment.",
                "bot",
                language
            );

            return;
        }


        const data = await response.json();

        console.log("M2 response:", data);


        // Update session if backend returns one
        if (data.session_id) {

            sessionId = data.session_id;

            localStorage.setItem(
                "jeevansetu_session_id",
                sessionId
            );
        }


        // Get backend response
        const reply =
            data.reply ||
            data.response ||
            data.message ||
            "Sorry, I could not generate a response.";


        // Add response
        addMessage(
            reply,
            "bot",
            data.language || language,
            data.is_emergency === true
        );


    } catch (error) {

        hideTyping();

        console.error(
            "M2 connection error:",
            error
        );


        addMessage(
            "Could not contact the chat service. Please try again later.",
            "bot",
            language
        );
    }
}


// ============================================================
// FORM SUBMIT
// ============================================================

composer.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();

        const text =
            messageInput.value.trim();

        if (text) {
            sendMessage(text);
        }
    }
);


// ============================================================
// RESET CHAT
// ============================================================

resetButton.addEventListener(
    "click",
    function () {

        sessionId =
            "web-" +
            Date.now() +
            "-" +
            Math.random().toString(36).substring(2, 10);

        localStorage.setItem(
            "jeevansetu_session_id",
            sessionId
        );

        showWelcome();

        messageInput.focus();
    }
);


// ============================================================
// VOICE RECOGNITION
// ============================================================

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


let recognition = null;

let isListening = false;


// Voice language.
// Click microphone again after stopping to cycle.
const voiceLanguages = [
    {
        code: "en-IN",
        name: "English"
    },
    {
        code: "hi-IN",
        name: "Hindi"
    },
    {
        code: "mr-IN",
        name: "Marathi"
    }
];

let voiceLanguageIndex = 0;


if (SpeechRecognition) {

    recognition = new SpeechRecognition();

    recognition.continuous = false;

    recognition.interimResults = false;


    recognition.onstart = function () {

        isListening = true;

        voiceButton.classList.add("listening");

        voiceButton.textContent = "⏹";


        if (statusText) {

            statusText.textContent =
                "Listening in " +
                voiceLanguages[voiceLanguageIndex].name +
                "...";
        }
    };


    recognition.onresult = function (event) {

        const transcript =
            event.results[0][0].transcript;

        console.log(
            "Voice transcript:",
            transcript
        );


        messageInput.value = transcript;


        // Automatically detect the resulting text
        const detected =
            detectLanguage(transcript);

        console.log(
            "Detected language:",
            detected
        );
    };


    recognition.onerror = function (event) {

        console.error(
            "Speech recognition error:",
            event.error
        );


        if (statusText) {

            statusText.textContent =
                "Health assistant • online";
        }
    };


    recognition.onend = function () {

        isListening = false;

        voiceButton.classList.remove("listening");

        voiceButton.textContent = "🎙";


        if (statusText) {

            statusText.textContent =
                "Health assistant • online";
        }
    };


    voiceButton.addEventListener(
        "click",
        function () {

            // Stop if already listening
            if (isListening) {

                recognition.stop();

                return;
            }


            // Select language
            recognition.lang =
                voiceLanguages[voiceLanguageIndex].code;


            console.log(
                "Voice language:",
                recognition.lang
            );


            try {

                recognition.start();

            } catch (error) {

                console.error(
                    "Could not start microphone:",
                    error
                );
            }
        }
    );


    // Right-click microphone to change voice language
    voiceButton.addEventListener(
        "contextmenu",
        function (event) {

            event.preventDefault();

            voiceLanguageIndex++;

            if (
                voiceLanguageIndex >=
                voiceLanguages.length
            ) {
                voiceLanguageIndex = 0;
            }


            const selected =
                voiceLanguages[voiceLanguageIndex];


            voiceButton.title =
                "Voice: " +
                selected.name;


            if (statusText) {

                statusText.textContent =
                    "Voice language: " +
                    selected.name;
            }


            console.log(
                "Voice language changed to:",
                selected.name
            );
        }
    );


} else {

    voiceButton.disabled = true;

    voiceButton.title =
        "Voice recognition is not supported by this browser";

    console.warn(
        "Speech Recognition is not supported."
    );
}


// ============================================================
// START CHAT
// ============================================================

showWelcome();

messageInput.focus();