const messages = document.querySelector('#messages');
const form = document.querySelector('#composer');
const input = document.querySelector('#messageInput');
const status = document.querySelector('#status');
const resetButton = document.querySelector('#resetButton');
const voiceButton = document.querySelector('#voiceButton');
const footerText = document.querySelector('#footerText');


// ============================================================
// Language Configuration
// ============================================================

const languageLabels = {
  en: 'English',
  hi: 'हिंदी',
  mr: 'मराठी'
};


const uiText = {

  // ==========================================================
  // English
  // ==========================================================

  en: {
    selected: 'Language selected: English. Please type your health question.',
    placeholder: 'Type a health question',
    statusOnline: 'Health assistant • online',
    statusProcessing: 'JeevanSetu AI is processing…',
    typing: 'JeevanSetu AI is typing…',
    welcome: 'Welcome to JeevanSetu AI.\nChoose your language:',
    chooseLanguage: 'Choose your language / भाषा निवडा:',
    cannotContact: 'Could not contact the chat service. Please make sure the M2 backend is running.',
    voiceUnsupported: 'Voice input is not supported in this browser. Use Chrome or Edge.',
    chooseLanguageVoice: 'Please choose a language before using voice input.',
    listening: 'Listening… Speak now',
    voiceSending: 'Voice message sent — JeevanSetu AI is responding…',
    voiceError: 'Voice input error',
    tryAgain: 'Please try again or type your question.',
    footer: 'AI health information only — not a diagnosis. For emergencies, call 112.'
  },


  // ==========================================================
  // Hindi
  // ==========================================================

  hi: {
    selected: 'भाषा चुनी गई: हिंदी। कृपया अपना स्वास्थ्य प्रश्न लिखें।',
    placeholder: 'अपना स्वास्थ्य प्रश्न लिखें',
    statusOnline: 'स्वास्थ्य सहायक • ऑनलाइन',
    statusProcessing: 'JeevanSetu AI उत्तर तैयार कर रहा है…',
    typing: 'JeevanSetu AI लिख रहा है…',
    welcome: 'JeevanSetu AI में आपका स्वागत है।\nअपनी भाषा चुनें:',
    chooseLanguage: 'अपनी भाषा चुनें:',
    cannotContact: 'चैट सेवा से संपर्क नहीं हो सका। कृपया सुनिश्चित करें कि M2 बैकएंड चल रहा है।',
    voiceUnsupported: 'इस ब्राउज़र में वॉइस इनपुट उपलब्ध नहीं है। Chrome या Edge का उपयोग करें।',
    chooseLanguageVoice: 'वॉइस इनपुट का उपयोग करने से पहले भाषा चुनें।',
    listening: 'सुन रहा है… बोलें',
    voiceSending: 'वॉइस संदेश भेजा गया — JeevanSetu AI उत्तर दे रहा है…',
    voiceError: 'वॉइस इनपुट में त्रुटि',
    tryAgain: 'कृपया फिर से प्रयास करें या अपना प्रश्न लिखें।',
    footer: 'यह केवल स्वास्थ्य संबंधी जानकारी है — यह चिकित्सा निदान नहीं है। आपात स्थिति में 112 पर कॉल करें।'
  },


  // ==========================================================
  // Marathi
  // ==========================================================

  mr: {
    selected: 'भाषा निवडली: मराठी. कृपया तुमचा आरोग्यविषयक प्रश्न लिहा.',
    placeholder: 'तुमचा आरोग्यविषयक प्रश्न लिहा',
    statusOnline: 'आरोग्य सहाय्यक • ऑनलाइन',
    statusProcessing: 'JeevanSetu AI उत्तर तयार करत आहे…',
    typing: 'JeevanSetu AI लिहित आहे…',
    welcome: 'JeevanSetu AI मध्ये आपले स्वागत आहे.\nतुमची भाषा निवडा:',
    chooseLanguage: 'तुमची भाषा निवडा:',
    cannotContact: 'चॅट सेवेशी संपर्क होऊ शकला नाही. कृपया M2 बॅकएंड सुरू आहे याची खात्री करा.',
    voiceUnsupported: 'या ब्राउझरमध्ये व्हॉइस इनपुट उपलब्ध नाही. Chrome किंवा Edge वापरा.',
    chooseLanguageVoice: 'व्हॉइस इनपुट वापरण्यापूर्वी भाषा निवडा.',
    listening: 'ऐकत आहे… बोला',
    voiceSending: 'व्हॉइस संदेश पाठवला आहे — JeevanSetu AI उत्तर देत आहे…',
    voiceError: 'व्हॉइस इनपुटमध्ये त्रुटी',
    tryAgain: 'कृपया पुन्हा प्रयत्न करा किंवा तुमचा प्रश्न लिहा.',
    footer: 'ही केवळ आरोग्यविषयक माहिती आहे — हे वैद्यकीय निदान नाही. आपत्कालीन परिस्थितीत 112 वर कॉल करा.'
  }

};


// ============================================================
// Quick Reply Buttons
// ============================================================

const quickReplyLabels = {

  en: [
    ['Dengue symptoms', 'What are dengue symptoms?'],
    ['Prevention tips', 'Give prevention tips'],
    ['Vaccination', 'Vaccination schedule'],
    ['Outbreak alerts', 'Is there an outbreak alert?'],
    ['Emergency help', 'I have severe chest pain']
  ],

  hi: [
    ['डेंग्यू लक्षण', 'डेंग्यू के लक्षण क्या हैं?'],
    ['बचाव सलाह', 'बचाव के उपाय बताएं'],
    ['टीकाकरण', 'टीकाकरण की जानकारी'],
    ['आउटब्रेक अलर्ट', 'क्या कोई आउटब्रेक अलर्ट है?'],
    ['आपात मदद', 'मुझे सीने में तेज दर्द है']
  ],

  mr: [
    ['डेंग्यू लक्षणे', 'मला डेंग्यूची लक्षणे सांगा'],
    ['प्रतिबंध', 'प्रतिबंधाचे उपाय सांगा'],
    ['लसीकरण', 'लसीकरणाची माहिती'],
    ['उद्रेक सूचना', 'उद्रेकाची सूचना आहे का?'],
    ['आणीबाणी मदत', 'माझ्या छातीत तीव्र दुखत आहे']
  ]

};


// ============================================================
// User ID
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
// Add Chat Bubble
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
// Update Interface Language
// ============================================================

function updateInterfaceLanguage() {

  if (!language) return;

  const text = uiText[language];

  input.placeholder = text.placeholder;

  status.textContent = text.statusOnline;

  footerText.textContent = text.footer;
}


// ============================================================
// Language Selection Menu
// ============================================================

function languageMenu() {

  const welcomeText =
    language === null
      ? 'Welcome to JeevanSetu .\nChoose your language / भाषा निवडा  / अपनी भाषा चुनें: '
      : uiText[language].welcome;

  const node = addBubble(welcomeText);

  for (const [code, label] of Object.entries(languageLabels)) {

    const button =
      document.createElement('button');

    button.className = 'choice';

    button.textContent = label;

    button.onclick = () => {

      language = code;

      const text = uiText[language];

      node.remove();

      // Update all UI text
      updateInterfaceLanguage();

      // First message after selecting language
      addBubble(text.selected);

      // Show quick replies
      quickReplies();

      input.focus();
    };

    node.append(button);
  }
}


// ============================================================
// Quick Replies
// ============================================================

function quickReplies() {

  const labels = quickReplyLabels[language];

  const container =
    document.createElement('div');

  container.className = 'quick-replies';

  for (const [label, text] of labels) {

    const button =
      document.createElement('button');

    button.className = 'quick-reply';

    button.textContent = label;

    button.onclick = () => {
      sendMessage(text);
    };

    container.append(button);
  }

  messages.append(container);

  messages.scrollTop =
    messages.scrollHeight;
}


// ============================================================
// Typing Indicator
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
// Reset Chat
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

  languageMenu();

  input.focus();
}


// ============================================================
// Text-to-Speech
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
        (voice) =>
          voice.lang
            .toLowerCase()
            .startsWith(languagePrefix)
      );

  if (matchingVoice) {
    utterance.voice = matchingVoice;
  }

  utterance.rate = 0.95;

  window.speechSynthesis.speak(
    utterance
  );
}


// ============================================================
// Start Application
// ============================================================

function start() {

  languageMenu();
}


// ============================================================
// Send Message
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

  if (!language) {

    languageMenu();

    return;
  }

  addBubble(
    message,
    'user'
  );

  input.value = '';

  input.disabled = true;

  status.textContent =
    uiText[language].statusProcessing;

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
            channel: 'whatsapp'
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
        data.language
      );
    }

  } catch (error) {

    typing.remove();

    addBubble(
      uiText[language].cannotContact,
      'bot emergency'
    );

  } finally {

    input.disabled = false;

    status.textContent =
      uiText[language].statusOnline;

    input.focus();
  }
}


// ============================================================
// Form Submit
// ============================================================

form.addEventListener(
  'submit',
  (event) => {

    event.preventDefault();

    const shouldSpeakReply =
      voiceMessageReady;

    voiceMessageReady = false;

    sendMessage(
      input.value,
      shouldSpeakReply
    );
  }
);


// ============================================================
// Input Event
// ============================================================

input.addEventListener(
  'input',
  () => {

    voiceMessageReady = false;
  }
);


// ============================================================
// Reset Button
// ============================================================

resetButton.addEventListener(
  'click',
  resetChat
);


// ============================================================
// Voice Recognition
// ============================================================

const SpeechRecognition =
  window.SpeechRecognition ||
  window.webkitSpeechRecognition;


if (!SpeechRecognition) {

  voiceButton.disabled = true;

  voiceButton.title =
    'Voice input is not supported in this browser.';

} else {

  const recognition =
    new SpeechRecognition();

  recognition.interimResults =
    false;

  recognition.maxAlternatives =
    1;

  let voiceTextCaptured = false;


  voiceButton.addEventListener(
    'click',
    () => {

      if (!language) {

        addBubble(
          'Please choose a language before using voice input.'
        );

        return;
      }

      voiceTextCaptured =
        false;

      recognition.lang =
        {
          en: 'en-IN',
          hi: 'hi-IN',
          mr: 'mr-IN'
        }[language];

      recognition.start();
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
        uiText[language].listening;
    };


  recognition.onresult =
    (event) => {

      const spokenText =
        event.results[0][0].transcript;

      voiceTextCaptured =
        true;

      voiceMessageReady =
        false;

      status.textContent =
        uiText[language].voiceSending;

      sendMessage(
        spokenText,
        true
      );
    };


  recognition.onerror =
    (event) => {

      if (event.error !== 'aborted') {

        addBubble(
          `${uiText[language].voiceError}: ${event.error}. ${uiText[language].tryAgain}`,
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
          uiText[language]
            ? uiText[language].statusOnline
            : 'Health assistant • online';
      }
    };
}


// ============================================================
// Start
// ============================================================

start();