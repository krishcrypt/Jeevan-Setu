// ============================================================
// JeevanSetu M3 CHAT UI
// M3 UI -> M2 FastAPI Backend
// Supports English, Hindi and Marathi voice input
// ============================================================

const messages = document.querySelector('#messages');
const form = document.querySelector('#composer');
const input = document.querySelector('#messageInput');
const status = document.querySelector('#status');
const resetButton = document.querySelector('#resetButton');
const voiceButton = document.querySelector('#voiceButton');
const footerText = document.querySelector('#footerText');

// ============================================================
// M2 BACKEND
// ============================================================

const API_URL =
  'https://jeevan-setu-1.onrender.com/api/v1/chat';

// ============================================================
// UI TEXT
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
    voiceSending: 'Voice message received — JeevanSetu AI is responding…',
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
      'JeevanSetu AI में आपका स्वागत है।\nअपना स्वास्थ्य संबंधी सवाल हिंदी, मराठी या अंग्रेज़ी में पूछें।',
    placeholder: 'अपना स्वास्थ्य संबंधी सवाल लिखें',
    online: 'स्वास्थ्य सहायक • ऑनलाइन',
    processing: 'JeevanSetu AI जवाब तैयार कर रहा है…',
    typing: 'JeevanSetu AI लिख रहा है…',
    listening: 'सुन रहा हूँ… बोलिए',
    voiceSending:
      'आवाज़ प्राप्त हुई — JeevanSetu AI जवाब दे रहा है…',
    cannotContact:
      'चैट सेवा से संपर्क नहीं हो सका। कृपया M2 backend चालू है या नहीं जांचें।',
    voiceUnsupported:
      'इस ब्राउज़र में voice input उपलब्ध नहीं है। Chrome या Edge इस्तेमाल करें।',
    voiceError: 'Voice input में समस्या',
    tryAgain: 'कृपया दोबारा प्रयास करें या अपना सवाल लिखें।',
    footer:
      'AI स्वास्थ्य जानकारी केवल जानकारी के लिए है — यह निदान नहीं है। आपातकाल में 112 पर कॉल करें।'
  },

  mr: {
    welcome:
      'JeevanSetu AI मध्ये आपले स्वागत आहे.\nतुमचा आरोग्यविषयक प्रश्न मराठी, हिंदी किंवा इंग्रजीमध्ये विचारा.',
    placeholder: 'तुमचा आरोग्यविषयक प्रश्न लिहा',
    online: 'आरोग्य सहाय्यक • ऑनलाइन',
    processing: 'JeevanSetu AI उत्तर तयार करत आहे…',
    typing: 'JeevanSetu AI लिहित आहे…',
    listening: 'ऐकत आहे… बोला',
    voiceSending:
      'आवाज प्राप्त झाला — JeevanSetu AI उत्तर देत आहे…',
    cannotContact:
      'चॅट सेवेशी संपर्क होऊ शकला नाही. कृपया M2 backend चालू आहे का ते तपासा.',
    voiceUnsupported:
      'या ब्राउझरमध्ये voice input उपलब्ध नाही. Chrome किंवा Edge वापरा.',
    voiceError: 'Voice input मध्ये समस्या',
    tryAgain: 'कृपया पुन्हा प्रयत्न करा किंवा प्रश्न टाइप करा.',
    footer:
      'AI आरोग्य माहिती फक्त माहितीसाठी आहे — हे वैद्यकीय निदान नाही. आपत्कालीन परिस्थितीत 112 वर कॉल करा.'
  }
};

// ============================================================
// STATE
// ============================================================

let language = null;
let voiceMessageReady = false;
let isListening = false;

// Session ID used by M2
const sessionId =
  localStorage.getItem('jeevansetu_session_id') ||
  crypto.randomUUID();

localStorage.setItem(
  'jeevansetu_session_id',
  sessionId
);

// ============================================================
// VOICE LANGUAGE SELECTOR
// ============================================================

// Create a small language selector beside microphone.
// This makes Hindi/Marathi recognition much more reliable.

const voiceLanguageSelect = document.createElement('select');

voiceLanguageSelect.id = 'voiceLanguage';

voiceLanguageSelect.title =
  'Select voice language';

voiceLanguageSelect.innerHTML = `
  <option value="auto">Auto</option>
  <option value="en">English</option>
  <option value="hi">हिंदी</option>
  <option value="mr">मराठी</option>
`;

// Insert selector immediately before microphone button
if (voiceButton && voiceButton.parentNode) {
  voiceButton.parentNode.insertBefore(
    voiceLanguageSelect,
    voiceButton
  );
}

// ============================================================
// ADD MESSAGE
// ============================================================

function addBubble(
  text,
  type = 'bot',
  meta = ''
) {
  const node =
    document.createElement('div');

  node.className =
    `bubble ${type}`;

  node.textContent =
    text;

  if (meta) {
    const note =
      document.createElement('div');

    note.className =
      'meta';

    note.textContent =
      meta;

    node.append(note);
  }

  messages.append(node);

  messages.scrollTop =
    messages.scrollHeight;

  return node;
}

// ============================================================
// LANGUAGE DETECTION
// ============================================================

function detectLanguage(text) {

  const value =
    text.trim().toLowerCase();

  if (!value) {
    return 'en';
  }

  // ----------------------------------------------------------
  // Marathi Devanagari words
  // ----------------------------------------------------------

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
    'कुठे',
    'कधी',
    'सांगा',
    'माहिती',
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
    'लसीकरण',
    'लस',
    'दुखत',
    'दुखते',
    'काय करावे',
    'काय करू'
  ];

  if (
    marathiWords.some(
      word => value.includes(word)
    )
  ) {
    return 'mr';
  }

  // ----------------------------------------------------------
  // Hindi Devanagari words
  // ----------------------------------------------------------

  const hindiWords = [
    'मुझे',
    'मेरा',
    'मेरी',
    'मेरे',
    'मुझको',
    'क्या',
    'कैसे',
    'कैसी',
    'कहाँ',
    'कब',
    'क्यों',
    'बताइए',
    'बताओ',
    'लक्षण',
    'बीमारी',
    'बीमार',
    'बुखार',
    'सिरदर्द',
    'सिर दर्द',
    'दर्द',
    'खांसी',
    'उल्टी',
    'दस्त',
    'पेट दर्द',
    'स्वास्थ्य',
    'सांस',
    'साँस'
  ];

  if (
    hindiWords.some(
      word => value.includes(word)
    )
  ) {
    return 'hi';
  }

  // ----------------------------------------------------------
  // If Devanagari is present
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
  // Roman Hindi
  // ----------------------------------------------------------

  const romanHindi = [
    'mera',
    'meri',
    'mere',
    'mujhe',
    'mujhko',
    'mujhse',
    'aap',
    'aapko',
    'aapki',
    'kya',
    'kaise',
    'kaisi',
    'kaisa',
    'kahan',
    'kab',
    'kyun',
    'kyon',
    'batao',
    'bataye',
    'bataiye',
    'mujhe batao',
    'mujhe bataiye',
    'sar dukh',
    'sar dard',
    'sir dukh',
    'sir dard',
    'dard ho',
    'dard hai',
    'bukhar',
    'bukhaar',
    'khansi',
    'ulti',
    'dast',
    'pet dard',
    'pet mein dard',
    'saans lene',
    'saans nahi',
    'saans lene mein',
    'tabiyat',
    'beemar',
    'bimaar',
    'bimari',
    'ilaj',
    'ilaaj',
    'dawai',
    'dava',
    'doctor ke paas',
    'hospital jana',
    'kya karu',
    'kya karoon',
    'kya karna chahiye'
  ];

  if (
    romanHindi.some(
      phrase => value.includes(phrase)
    )
  ) {
    return 'hi';
  }

  // ----------------------------------------------------------
  // Roman Marathi
  // ----------------------------------------------------------

  const romanMarathi = [
    'mala',
    'majha',
    'majhi',
    'majhe',
    'majhya',
    'ahe',
    'ahet',
    'kay',
    'kasa',
    'kashi',
    'kuthe',
    'kadhi',
    'sanga',
    'sang',
    'mala mahiti',
    'mala sanga',
    'lakshane',
    'laksane',
    'arogya',
    'aarogya',
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
    romanMarathi.some(
      word => value.includes(word)
    )
  ) {
    return 'mr';
  }

  return 'en';
}

// ============================================================
// UPDATE UI LANGUAGE
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
// WELCOME
// ============================================================

function showWelcome() {

  addBubble(
    'Welcome to JeevanSetu AI.\n' +
    'Ask your health question in English, Hindi, or Marathi.'
  );
}

// ============================================================
// TYPING INDICATOR
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
// RESET
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
    uiText.en.footer;

  voiceLanguageSelect.value =
    'auto';

  showWelcome();

  input.focus();
}

// ============================================================
// TEXT TO SPEECH
// ============================================================

function speakReply(
  text,
  replyLanguage
) {

  if (
    !('speechSynthesis' in window)
  ) {
    return;
  }

  window.speechSynthesis.cancel();

  const utterance =
    new SpeechSynthesisUtterance(
      text
    );

  const targetLanguage =
    {
      en: 'en-IN',
      hi: 'hi-IN',
      mr: 'mr-IN'
    }[replyLanguage] || 'en-IN';

  utterance.lang =
    targetLanguage;

  const voices =
    window.speechSynthesis
      .getVoices();

  // Prefer exact Indian language voice
  let matchingVoice =
    voices.find(
      voice =>
        voice.lang.toLowerCase() ===
        targetLanguage.toLowerCase()
    );

  // Otherwise find language family
  if (!matchingVoice) {
    matchingVoice =
      voices.find(
        voice =>
          voice.lang
            .toLowerCase()
            .startsWith(
              targetLanguage
                .slice(0, 2)
                .toLowerCase()
            )
      );
  }

  if (matchingVoice) {
    utterance.voice =
      matchingVoice;
  }

  utterance.rate =
    0.95;

  utterance.pitch =
    1;

  window.speechSynthesis.speak(
    utterance
  );
}

// ============================================================
// SEND MESSAGE TO M2
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

  // Detect language from actual text
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

    const response =
      await fetch(
        API_URL,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',
            'Accept':
              'application/json'
          },

          body:
            JSON.stringify({
              session_id:
                sessionId,

              message:
                message,

              language:
                language,

              channel:
                'web'
            })
        }
      );

    if (!response.ok) {

      let errorMessage =
        `Server error: ${response.status}`;

      try {

        const errorData =
          await response.json();

        if (errorData.detail) {

          errorMessage =
            typeof errorData.detail ===
            'string'
              ? errorData.detail
              : JSON.stringify(
                  errorData.detail
                );
        }

      } catch (_) {}

      throw new Error(
        errorMessage
      );
    }

    const data =
      await response.json();

    typing.remove();

    // M2 response:
    //
    // {
    //   reply,
    //   session_id,
    //   language,
    //   is_emergency
    // }

    const replyLanguage =
      ['en', 'hi', 'mr'].includes(
        data.language
      )
        ? data.language
        : language;

    language =
      replyLanguage;

    updateInterfaceLanguage();

    const bubbleType =
      data.is_emergency
        ? 'bot emergency'
        : 'bot';

    const emergencyText =
      data.is_emergency
        ? ' • emergency'
        : '';

    addBubble(
      data.reply,
      bubbleType,
      `${replyLanguage} • M2 connected${emergencyText}`
    );

    // Speak answer in same language
    if (shouldSpeakReply) {

      speakReply(
        data.reply,
        replyLanguage
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

    input.disabled =
      false;

    status.textContent =
      uiText[
        language || 'en'
      ].online;

    input.focus();
  }
}

// ============================================================
// FORM SUBMIT
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
// NORMAL TEXT INPUT
// ============================================================

input.addEventListener(
  'input',
  () => {

    voiceMessageReady =
      false;
  }
);

// ============================================================
// RESET BUTTON
// ============================================================

resetButton.addEventListener(
  'click',
  resetChat
);

// ============================================================
// SPEECH RECOGNITION
// ============================================================

const SpeechRecognition =
  window.SpeechRecognition ||
  window.webkitSpeechRecognition;

if (!SpeechRecognition) {

  voiceButton.disabled =
    true;

  voiceButton.title =
    'Voice input is not supported in this browser. Use Chrome or Edge.';

} else {

  const recognition =
    new SpeechRecognition();

  // We want partial speech results
  recognition.interimResults =
    true;

  // More alternatives improves recognition quality
  recognition.maxAlternatives =
    5;

  // Do not continuously listen forever
  recognition.continuous =
    false;

  // ----------------------------------------------------------
  // Select recognition language
  // ----------------------------------------------------------

  function getSpeechLanguage() {

    const selected =
      voiceLanguageSelect.value;

    if (selected === 'en') {
      return 'en-IN';
    }

    if (selected === 'hi') {
      return 'hi-IN';
    }

    if (selected === 'mr') {
      return 'mr-IN';
    }

    // AUTO MODE
    //
    // Use already detected conversation language.
    if (language === 'hi') {
      return 'hi-IN';
    }

    if (language === 'mr') {
      return 'mr-IN';
    }

    if (language === 'en') {
      return 'en-IN';
    }

    // Use browser language if available.
    const browserLanguage =
      (
        navigator.language ||
        'en-IN'
      ).toLowerCase();

    if (
      browserLanguage.startsWith('mr')
    ) {
      return 'mr-IN';
    }

    if (
      browserLanguage.startsWith('hi')
    ) {
      return 'hi-IN';
    }

    return 'en-IN';
  }

  // ----------------------------------------------------------
  // Microphone click
  // ----------------------------------------------------------

  voiceButton.addEventListener(
    'click',
    () => {

      if (isListening) {

        recognition.stop();

        return;
      }

      voiceMessageReady =
        false;

      input.value = '';

      const speechLanguage =
        getSpeechLanguage();

      recognition.lang =
        speechLanguage;

      console.log(
        'Speech recognition language:',
        speechLanguage
      );

      try {

        recognition.start();

      } catch (error) {

        console.log(
          'Recognition already running:',
          error
        );
      }
    }
  );

  // ----------------------------------------------------------
  // Started listening
  // ----------------------------------------------------------

  recognition.onstart =
    () => {

      isListening =
        true;

      voiceButton.classList.add(
        'listening'
      );

      voiceButton.textContent =
        '🔴';

      const currentLanguage =
        voiceLanguageSelect.value ===
        'auto'
          ? language || 'en'
          : voiceLanguageSelect.value;

      status.textContent =
        uiText[
          currentLanguage
        ].listening;
    };

  // ----------------------------------------------------------
  // Recognition result
  // ----------------------------------------------------------

  recognition.onresult =
    event => {

      let transcript = '';

      // Combine all final/interim results
      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {

        transcript +=
          event.results[i][0]
            .transcript;
      }

      transcript =
        transcript.trim();

      if (!transcript) {
        return;
      }

      // Show recognized speech inside input
      // before sending it.
      input.value =
        transcript;

      // Detect actual language
      // from recognized transcript.
      const detected =
        detectLanguage(
          transcript
        );

      language =
        detected;

      updateInterfaceLanguage();

      console.log(
        'Recognized speech:',
        transcript
      );

      console.log(
        'Detected language:',
        detected
      );

      // Only send once final result arrives
      const lastResult =
        event.results[
          event.results.length - 1
        ];

      if (
        lastResult.isFinal
      ) {

        voiceMessageReady =
          true;

        sendMessage(
          transcript,
          true
        );
      }
    };

  // ----------------------------------------------------------
  // Error handling
  // ----------------------------------------------------------

  recognition.onerror =
    event => {

      console.error(
        'Speech recognition error:',
        event.error
      );

      isListening =
        false;

      voiceButton.classList.remove(
        'listening'
      );

      voiceButton.textContent =
        '🎙';

      let currentLanguage =
        language || 'en';

      // Permission error
      if (
        event.error ===
        'not-allowed'
      ) {

        addBubble(
          'Microphone permission was denied. Please allow microphone access for this website and try again.',
          'bot emergency'
        );

        return;
      }

      // No speech
      if (
        event.error ===
        'no-speech'
      ) {

        addBubble(
          `${uiText[currentLanguage].voiceError}: No speech detected. Please speak clearly and try again.`,
          'bot'
        );

        return;
      }

      // Network error
      if (
        event.error ===
        'network'
      ) {

        addBubble(
          `${uiText[currentLanguage].voiceError}: Browser speech recognition network error. Please check your internet connection.`,
          'bot emergency'
        );

        return;
      }

      // Other errors
      if (
        event.error !==
        'aborted'
      ) {

        addBubble(
          `${uiText[currentLanguage].voiceError}: ${event.error}. ${uiText[currentLanguage].tryAgain}`,
          'bot'
        );
      }
    };

  // ----------------------------------------------------------
  // Recognition ended
  // ----------------------------------------------------------

  recognition.onend =
    () => {

      isListening =
        false;

      voiceButton.classList.remove(
        'listening'
      );

      voiceButton.textContent =
        '🎙';

      if (!voiceMessageReady) {

        status.textContent =
          uiText[
            language || 'en'
          ].online;
      }
    };
}

// ============================================================
// SPEECH SYNTHESIS VOICE LOADING
// ============================================================

if (
  'speechSynthesis' in window
) {

  window.speechSynthesis.onvoiceschanged =
    () => {

      // Force browser to load available voices.
      window.speechSynthesis
        .getVoices();
    };
}

// ============================================================
// START CHAT
// ============================================================

showWelcome();