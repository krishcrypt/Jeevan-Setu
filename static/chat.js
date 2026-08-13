const messages = document.querySelector('#messages');
const form = document.querySelector('#composer');
const input = document.querySelector('#messageInput');
const status = document.querySelector('#status');
const resetButton = document.querySelector('#resetButton');
const voiceButton = document.querySelector('#voiceButton');
const footerText = document.querySelector('#footerText');


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
      'JeevanSetu AI में आपका स्वागत है।\nअपना स्वास्थ्य प्रश्न हिंदी, अंग्रेज़ी या मराठी में लिखें या बोलें।',
    placeholder: 'अपना स्वास्थ्य प्रश्न लिखें',
    online: 'स्वास्थ्य सहायक • ऑनलाइन',
    processing: 'JeevanSetu AI उत्तर तैयार कर रहा है…',
    typing: 'JeevanSetu AI लिख रहा है…',
    listening: 'सुन रहा है… बोलें',
    voiceSending:
      'वॉइस संदेश प्राप्त हुआ — JeevanSetu AI उत्तर दे रहा है…',
    cannotContact:
      'चैट सेवा से संपर्क नहीं हो सका। कृपया सुनिश्चित करें कि M2 बैकएंड चल रहा है।',
    voiceUnsupported:
      'इस ब्राउज़र में वॉइस इनपुट उपलब्ध नहीं है। Chrome या Edge का उपयोग करें।',
    voiceError: 'वॉइस इनपुट में त्रुटि',
    tryAgain: 'कृपया फिर से प्रयास करें या अपना प्रश्न लिखें।',
    footer:
      'यह केवल स्वास्थ्य संबंधी जानकारी है — यह चिकित्सा निदान नहीं है। आपात स्थिति में 112 पर कॉल करें।'
  },

  mr: {
    welcome:
      'JeevanSetu AI मध्ये आपले स्वागत आहे.\nतुमचा आरोग्यविषयक प्रश्न मराठी, हिंदी किंवा इंग्रजीमध्ये लिहा किंवा बोला.',
    placeholder: 'तुमचा आरोग्यविषयक प्रश्न लिहा',
    online: 'आरोग्य सहाय्यक • ऑनलाइन',
    processing: 'JeevanSetu AI उत्तर तयार करत आहे…',
    typing: 'JeevanSetu AI लिहित आहे…',
    listening: 'ऐकत आहे… बोला',
    voiceSending:
      'व्हॉइस संदेश प्राप्त झाला — JeevanSetu AI उत्तर देत आहे…',
    cannotContact:
      'चॅट सेवेशी संपर्क होऊ शकला नाही. कृपया M2 बॅकएंड सुरू आहे याची खात्री करा.',
    voiceUnsupported:
      'या ब्राउझरमध्ये व्हॉइस इनपुट उपलब्ध नाही. Chrome किंवा Edge वापरा.',
    voiceError: 'व्हॉइस इनपुटमध्ये त्रुटी',
    tryAgain: 'कृपया पुन्हा प्रयत्न करा किंवा तुमचा प्रश्न लिहा.',
    footer:
      'ही केवळ आरोग्यविषयक माहिती आहे — हे वैद्यकीय निदान नाही. आपत्कालीन परिस्थितीत 112 वर कॉल करा.'
  }
};


// ============================================================
// State
// ============================================================

let language = null;
let voiceMessageReady = false;

const userId =
  localStorage.getItem('jeevansetu_user_id') ||
  crypto.randomUUID();

localStorage.setItem(
  'jeevansetu_user_id',
  userId
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

    // Health-related Marathi
    'डोकेदुखी',
    'अंगदुखी',
    'पोटदुखी',
    'घशात',
    'खोकला',
    'मळमळ',
    'उलटी',
    'जुलाब',
    'ताप',
    'चक्कर',
    'थकवा',
    'भूक',
    'श्वास',
    'छातीत',
    'दुखत',
    'दुखणे',
    'दुखतं',
    'वेदना',
    'जखम',
    'सूज',
    'खाज',
    'रक्तदाब',
    'मधुमेह',
    'लसीकरण',
    'लस',
    'लक्षणे',
    'लक्षण',
    'आरोग्य',
    'आजारी',
    'तपासणी',
    'औषध',
    'डॉक्टर',
    'रुग्ण',
    'रुग्णालय',

    // Common Marathi words
    'मला',
    'माझा',
    'माझी',
    'माझे',
    'माझ्या',
    'आहे',
    'आहेत',
    'काय',
    'कसे',
    'कशी',
    'कधी',
    'कुठे',
    'कोठे',
    'का',
    'म्हणजे',
    'माहिती',
    'सांगा',
    'सांग',
    'करावे',
    'करायचे',
    'करू',
    'होते',
    'होत',
    'नाही',
    'नसते',
    'यासाठी',
    'यावर',
    'म्हणून',
    'प्रतिबंध',
    'उद्रेक',
    'बचाव',
    'कृपया',
    'तुमचा',
    'तुमची',
    'तुमचे',
    'माझं',
    'माझ्या'
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
    'क्यों',
    'बताएं',
    'बताइए',
    'जानकारी',
    'लक्षण',
    'बुखार',
    'सिरदर्द',
    'पेट दर्द',
    'खांसी',
    'उल्टी',
    'दस्त',
    'टीका',
    'टीकाकरण',
    'रोकथाम',
    'बचाव',
    'स्वास्थ्य',
    'डॉक्टर',
    'अस्पताल',
    'दर्द'
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

    const res =
      await fetch(
        '/api/chat',
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          body: JSON.stringify({
            user_id: userId,
            message: message,
            language: language,
            channel: 'web'
          })
        }
      );


    if (!res.ok) {
      throw new Error(
        `Server error: ${res.status}`
      );
    }


    const data =
      await res.json();


    typing.remove();


    // Keep the detected language unless
    // M2 explicitly returns another supported language.
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
      data.safety_level === 'emergency'
        ? 'bot emergency'
        : 'bot';


    const sourceText =
      data.source === 'm2'
        ? 'M2 connected'
        : data.source === 'fallback'
          ? 'offline fallback'
          : 'JeevanSetu AI';


    addBubble(
      data.response,
      type,
      `${data.category} • ${data.safety_level} • ${sourceText}`
    );


    if (shouldSpeakReply) {

      speakReply(
        data.response,
        language
      );
    }


  } catch (error) {

    typing.remove();

    addBubble(
      selectedLanguage.cannotContact,
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
        '■';

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


      // Detect language from the transcript.
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
        '🎙';


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