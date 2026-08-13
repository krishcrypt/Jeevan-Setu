const messages = document.querySelector('#messages');
const form = document.querySelector('#composer');
const input = document.querySelector('#messageInput');
const status = document.querySelector('#status');
const resetButton = document.querySelector('#resetButton');
const voiceButton = document.querySelector('#voiceButton');
const footerText = document.querySelector('#footerText');

// ============================================================
// M2 BACKEND CONFIGURATION
// ============================================================

// M2 FastAPI backend
const API_URL = 'http://127.0.0.1:8000/api/v1/chat';

// ============================================================
// UI translations
// ============================================================

const uiText = {
  en: {
    welcome:
      'Welcome to JeevanSetu AI.\nAsk your health question in English, Hindi, or Marathi.',
    placeholder: 'Type a health question',
    online: 'Health assistant • online',
    processing: 'JeevanSetu AI is processing…',
    typing: 'JeevanSetu AI is typing…',
    listening: 'Listening… Speak now',
    voiceSending:
      'Voice message received — JeevanSetu AI is responding…',
    cannotContact:
      'Could not contact the chat service. Please make sure the M2 backend is running.',
    voiceUnsupported:
      'Voice input is not supported in this browser. Use Chrome or Edge.',
    voiceError: 'Voice input error',
    tryAgain: 'Please try again or type your question.',
    footer:
      'AI health information only — not a diagnosis. For emergencies, call 112.'
  },

  hi: {
    welcome:
      'JeevanSetu AI में आपका स्वागत है।\nअपना स्वास्थ्य प्रश्न हिंदी, अंग्रेज़ी या मराठी में पूछें।',
    placeholder: 'अपना स्वास्थ्य प्रश्न लिखें',
    online: 'स्वास्थ्य सहायक • ऑनलाइन',
    processing: 'JeevanSetu AI जवाब तैयार कर रहा है…',
    typing: 'JeevanSetu AI टाइप कर रहा है…',
    listening: 'सुन रहा है… बोलें',
    voiceSending:
      'वॉइस संदेश प्राप्त हुआ — JeevanSetu AI जवाब दे रहा है…',
    cannotContact:
      'चैट सेवा से संपर्क नहीं हो सका। कृपया सुनिश्चित करें कि M2 backend चल रहा है।',
    voiceUnsupported:
      'इस ब्राउज़र में voice input समर्थित नहीं है। Chrome या Edge का उपयोग करें।',
    voiceError: 'वॉइस इनपुट में त्रुटि',
    tryAgain: 'कृपया फिर से प्रयास करें या अपना प्रश्न टाइप करें।',
    footer:
      'केवल AI स्वास्थ्य जानकारी — यह निदान नहीं है। आपातकाल में 112 पर कॉल करें।'
  },

  mr: {
    welcome:
      'JeevanSetu AI मध्ये आपले स्वागत आहे.\nआपला आरोग्य प्रश्न मराठी, हिंदी किंवा इंग्रजीमध्ये विचारा.',
    placeholder: 'आपला आरोग्य प्रश्न लिहा',
    online: 'आरोग्य सहाय्यक • ऑनलाइन',
    processing: 'JeevanSetu AI उत्तर तयार करत आहे…',
    typing: 'JeevanSetu AI टाइप करत आहे…',
    listening: 'ऐकत आहे… बोला',
    voiceSending:
      'व्हॉइस संदेश प्राप्त झाला — JeevanSetu AI उत्तर देत आहे…',
    cannotContact:
      'चॅट सेवेशी संपर्क होऊ शकला नाही. कृपया M2 backend चालू आहे याची खात्री करा.',
    voiceUnsupported:
      'या ब्राउझरमध्ये voice input समर्थित नाही. Chrome किंवा Edge वापरा.',
    voiceError: 'व्हॉइस इनपुट त्रुटी',
    tryAgain: 'कृपया पुन्हा प्रयत्न करा किंवा आपला प्रश्न टाइप करा.',
    footer:
      'फक्त AI आरोग्य माहिती — हे निदान नाही. आपत्कालीन परिस्थितीत 112 वर कॉल करा.'
  }
};

// ============================================================
// State
// ============================================================

let language = null;
let voiceMessageReady = false;

// M2 uses session_id
const sessionId =
  localStorage.getItem('jeevansetu_session_id') ||
  crypto.randomUUID();

localStorage.setItem(
  'jeevansetu_session_id',
  sessionId
);

// ============================================================
// Add message bubble
// ============================================================

function addBubble(text, type = 'bot', meta = '') {
  const node = document.createElement('div');

  node.className = `bubble ${type}`;

  node.textContent = text;

  if (meta) {
    const note = document.createElement('div');

    note.className = 'meta';

    note.textContent = meta;

    node.append(note);
  }

  messages.append(node);

  messages.scrollTop = messages.scrollHeight;

  return node;
}

// ============================================================
// Marathi detection
// ============================================================

function containsMarathiWord(text) {
  const marathiWords = [
    'मला',
    'माझा',
    'माझी',
    'माझे',
    'माझ्या',
    'आहे',
    'आहेत',
    'काय',
    'कसा',
    'कशी',
    'कधी',
    'कुठे',
    'सांगा',
    'सांग',
    'मला माहिती',
    'मला सांगा',
    'लक्षणे',
    'आरोग्य',
    'ताप',
    'डोकेदुखी',
    'अंगदुखी',
    'पोट दुखत',
    'खोकला',
    'मळमळ',
    'उलटी',
    'जुलाब',
    'लवकर',
    'प्रतिबंध',
    'लसीकरण',
    'लस'
  ];

  return marathiWords.some(
    word => text.includes(word)
  );
}

// ============================================================
// Detect language from text
// ============================================================

function detectLanguage(text) {
  const value =
    text.trim().toLowerCase();

  if (!value) {
    return 'en';
  }

  // ----------------------------------------------------------
  // Marathi-specific detection
  // ----------------------------------------------------------

  if (containsMarathiWord(value)) {
    return 'mr';
  }

  // ----------------------------------------------------------
  // Roman Marathi detection
  // ----------------------------------------------------------

  const romanMarathiWords = [
    'mala',
    'majha',
    'majhi',
    'maje',
    'majhya',
    'ahe',
    'ahet',
    'kay',
    'kasa',
    'kashi',
    'kadhi',
    'kuthe',
    'ka',
    'sanga',
    'sang',
    'mala mahiti',
    'mala sanga',
    'lakshane',
    'laksane',
    'arogya',
    'aarogya',
    'dengue chi',
    'dengyu chi',
    'taap',
    'dokyala',
    'dokhedukh',
    'angdukhi',
    'pott dukhat',
    'khokla',
    'malmal',
    'ulti',
    'julaab',
    'lavkar',
    'pratibandh',
    'lasikaran',
    'lasi'
  ];

  if (
    romanMarathiWords.some(
      word => value.includes(word)
    )
  ) {
    return 'mr';
  }

  // ----------------------------------------------------------
  // Hindi detection
  // ----------------------------------------------------------

  const hindiWords = [
    'मुझे',
    'मेरा',
    'मेरी',
    'मेरे',
    'क्या',
    'कैसे',
    'कैसी',
    'कब',
    'कहाँ',
    'बताएं',
    'बताओ',
    'मुझे जानकारी',
    'लक्षण',
    'बुखार',
    'सिरदर्द',
    'खांसी',
    'उल्टी',
    'दस्त',
    'बीमारी',
    'स्वास्थ्य',
    'इलाज',
    'रोकथाम',
    'टीका',
    'टीकाकरण'
  ];

  if (
    hindiWords.some(
      word => value.includes(word)
    )
  ) {
    return 'hi';
  }

  // ----------------------------------------------------------
  // Devanagari fallback
  // ----------------------------------------------------------

  if (
    [...value].some(
      char =>
        char >= '\u0900' &&
        char <= '\u097F'
    )
  ) {
    return 'hi';
  }

  // ----------------------------------------------------------
  // English default
  // ----------------------------------------------------------

  return 'en';
}

// ============================================================
// Update interface language
// ============================================================

function updateInterfaceLanguage() {
  if (!language) {
    return;
  }

  const text =
    uiText[language];

  input.placeholder =
    text.placeholder;

  status.textContent =
    text.online;

  footerText.textContent =
    text.footer;
}

// ============================================================
// Welcome
// ============================================================

function showWelcome() {
  addBubble(
    'Welcome to JeevanSetu AI.\n' +
    'Ask your health question in English, Hindi, or Marathi.'
  );
}

// ============================================================
// Typing indicator
// ============================================================

function showTyping() {
  const node =
    document.createElement('div');

  node.className =
    'bubble bot typing';

  node.textContent =
    language
      ? uiText[language].typing
      : 'JeevanSetu AI is typing…';

  messages.append(node);

  messages.scrollTop =
    messages.scrollHeight;

  return node;
}

// ============================================================
// Reset
// ============================================================

function resetChat() {
  language = null;

  voiceMessageReady = false;

  messages.replaceChildren();

  input.value = '';

  input.placeholder =
    'Type a health question';

  status.textContent =
    'Health assistant • online';

  footerText.textContent =
    'AI health information only — not a diagnosis. For emergencies, call 112.';

  showWelcome();

  input.focus();
}

// ============================================================
// Text-to-speech
// ============================================================

function speakReply(text, replyLanguage) {
  if (!('speechSynthesis' in window)) {
    return;
  }

  window.speechSynthesis.cancel();

  const utterance =
    new SpeechSynthesisUtterance(text);

  const targetLanguage =
    {
      en: 'en-IN',
      hi: 'hi-IN',
      mr: 'mr-IN'
    }[replyLanguage] || 'en-IN';

  utterance.lang =
    targetLanguage;

  const languagePrefix =
    targetLanguage
      .slice(0, 2)
      .toLowerCase();

  const matchingVoice =
    window.speechSynthesis
      .getVoices()
      .find(
        voice =>
          voice.lang
            .toLowerCase()
            .startsWith(languagePrefix)
      );

  if (matchingVoice) {
    utterance.voice =
      matchingVoice;
  }

  utterance.rate =
    0.95;

  window.speechSynthesis.speak(
    utterance
  );
}

// ============================================================
// Send message
// ============================================================

async function sendMessage(
  message,
  shouldSpeakReply = false
) {
  message =
    message.trim();

  if (!message) {
    return;
  }

  // Automatically detect language.
  language =
    detectLanguage(message);

  updateInterfaceLanguage();

  const selectedLanguage =
    uiText[language];

  addBubble(
    message,
    'user'
  );

  input.value = '';

  input.disabled = true;

  status.textContent =
    selectedLanguage.processing;

  const typing =
    showTyping();

  try {
    // ========================================================
    // M3 → M2 CONNECTION
    // ========================================================

    const res =
      await fetch(
        API_URL,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          body: JSON.stringify({
            session_id: sessionId,
            message: message,
            language: language,
            channel: 'web'
          })
        }
      );

    if (!res.ok) {
      let errorMessage =
        `Server error: ${res.status}`;

      try {
        const errorData =
          await res.json();

        if (errorData.detail) {
          errorMessage =
            typeof errorData.detail === 'string'
              ? errorData.detail
              : JSON.stringify(errorData.detail);
        }
      } catch (_) {
        // Ignore JSON parsing errors.
      }

      throw new Error(errorMessage);
    }

    const data =
      await res.json();

    typing.remove();

    // ========================================================
    // M2 RESPONSE
    //
    // M2 returns:
    // {
    //   reply,
    //   session_id,
    //   language,
    //   is_emergency
    // }
    // ========================================================

    const replyLanguage =
      ['en', 'hi', 'mr'].includes(
        data.language
      )
        ? data.language
        : language;

    language =
      replyLanguage;

    updateInterfaceLanguage();

    const type =
      data.is_emergency
        ? 'bot emergency'
        : 'bot';

    const emergencyText =
      data.is_emergency
        ? ' • emergency'
        : '';

    addBubble(
      data.reply,
      type,
      `${data.language} • M2 connected${emergencyText}`
    );

    if (shouldSpeakReply) {
      speakReply(
        data.reply,
        language
      );
    }

  } catch (error) {
    console.error(
      'M2 backend connection error:',
      error
    );

    typing.remove();

    addBubble(
      `${selectedLanguage.cannotContact}\n\nError: ${error.message}`,
      'bot emergency'
    );

  } finally {
    input.disabled = false;

    status.textContent =
      uiText[
        language || 'en'
      ].online;

    input.focus();
  }
}

// ============================================================
// Form submit
// ============================================================

form.addEventListener(
  'submit',
  event => {
    event.preventDefault();

    const shouldSpeakReply =
      voiceMessageReady;

    voiceMessageReady =
      false;

    sendMessage(
      input.value,
      shouldSpeakReply
    );
  }
);

// ============================================================
// Input
// ============================================================

input.addEventListener(
  'input',
  () => {
    voiceMessageReady = false;
  }
);

// ============================================================
// Reset
// ============================================================

resetButton.addEventListener(
  'click',
  resetChat
);

// ============================================================
// Voice recognition
// ============================================================

const SpeechRecognition =
  window.SpeechRecognition ||
  window.webkitSpeechRecognition;

if (!SpeechRecognition) {
  voiceButton.disabled = true;

  voiceButton.title =
    'Voice input is not supported in this browser. Use Chrome or Edge.';

} else {
  const recognition =
    new SpeechRecognition();

  recognition.interimResults =
    false;

  recognition.maxAlternatives =
    3;

  let voiceTextCaptured =
    false;

  voiceButton.addEventListener(
    'click',
    () => {
      voiceTextCaptured =
        false;

      const browserLanguage =
        navigator.language ||
        'en-IN';

      const speechLanguage =
        browserLanguage
          .toLowerCase()
          .startsWith('hi')
          ? 'hi-IN'
          : browserLanguage
              .toLowerCase()
              .startsWith('mr')
            ? 'mr-IN'
            : 'en-IN';

      recognition.lang =
        speechLanguage;

      try {
        recognition.start();
      } catch (_) {
        // Already running.
      }
    }
  );

  recognition.onstart =
    () => {
      voiceButton.classList.add(
        'listening'
      );

      voiceButton.textContent =
        '🎤';

      status.textContent =
        uiText[
          language || 'en'
        ].listening;
    };

  recognition.onresult =
    event => {
      const spokenText =
        event.results[0][0]
          .transcript;

      voiceTextCaptured =
        true;

      voiceMessageReady =
        true;

      // Detect language from transcript.
      language =
        detectLanguage(
          spokenText
        );

      updateInterfaceLanguage();

      status.textContent =
        uiText[language]
          .voiceSending;

      sendMessage(
        spokenText,
        true
      );
    };

  recognition.onerror =
    event => {
      if (
        event.error !== 'aborted'
      ) {
        const currentText =
          uiText[
            language || 'en'
          ];

        addBubble(
          `${currentText.voiceError}: ${event.error}. ${currentText.tryAgain}`,
          'bot'
        );
      }
    };

  recognition.onend =
    () => {
      voiceButton.classList.remove(
        'listening'
      );

      voiceButton.textContent =
        '🎤';

      if (!voiceTextCaptured) {
        status.textContent =
          uiText[
            language || 'en'
          ].online;
      }
    };
}

// ============================================================
// Start
// ============================================================

showWelcome();