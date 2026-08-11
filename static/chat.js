const messages = document.querySelector('#messages');
const form = document.querySelector('#composer');
const input = document.querySelector('#messageInput');
const status = document.querySelector('#status');
const resetButton = document.querySelector('#resetButton');
const voiceButton = document.querySelector('#voiceButton');
const languageLabels = { en: 'English', hi: 'हिंदी', mr: 'मराठी' };
// Language is intentionally per-page-session: every new visit starts with the
// welcome menu so the demo always shows language selection.
let language = null;
let voiceMessageReady = false;
const userId = localStorage.getItem('jeevansetu_user_id') || crypto.randomUUID();
localStorage.setItem('jeevansetu_user_id', userId);

function addBubble(text, type = 'bot', meta = '') {
  const node = document.createElement('div');
  node.className = `bubble ${type}`;
  node.textContent = text;
  if (meta) { const note = document.createElement('div'); note.className = 'meta'; note.textContent = meta; node.append(note); }
  messages.append(node); messages.scrollTop = messages.scrollHeight; return node;
}
function languageMenu() {
  const node = addBubble('Welcome to JeevanSetu AI.\nChoose your language / भाषा निवडा:');
  for (const [code, label] of Object.entries(languageLabels)) {
    const button = document.createElement('button'); button.className = 'choice'; button.textContent = label;
    button.onclick = () => { language = code; node.remove(); addBubble(`Language selected: ${label}. Please type your health question.`); input.placeholder = code === 'hi' ? 'अपना स्वास्थ्य प्रश्न लिखें' : code === 'mr' ? 'तुमचा आरोग्यविषयक प्रश्न लिहा' : 'Type a health question'; quickReplies(); input.focus(); };
    node.append(button);
  }
}
function quickReplies() {
  const labels = {
    en: [['Dengue symptoms', 'What are dengue symptoms?'], ['Prevention tips', 'Give prevention tips'], ['Vaccination', 'Vaccination schedule'], ['Outbreak alerts', 'Is there an outbreak alert?'], ['Emergency help', 'I have severe chest pain']],
    hi: [['डेंग्यू लक्षण', 'डेंग्यू के लक्षण क्या हैं?'], ['बचाव सलाह', 'बचाव के उपाय बताएं'], ['टीकाकरण', 'टीकाकरण की जानकारी'], ['आउटब्रेक अलर्ट', 'क्या कोई आउटब्रेक अलर्ट है?'], ['आपात मदद', 'मुझे सीने में तेज दर्द है']],
    mr: [['डेंग्यू लक्षणे', 'मला डेंग्यूची लक्षणे सांगा'], ['प्रतिबंध', 'प्रतिबंधाचे उपाय सांगा'], ['लसीकरण', 'लसीकरणाची माहिती'], ['उद्रेक सूचना', 'उद्रेकाची सूचना आहे का?'], ['आणीबाणी मदत', 'माझ्या छातीत तीव्र दुखत आहे']],
  };
  const container = document.createElement('div'); container.className = 'quick-replies';
  for (const [label, text] of labels[language]) { const button = document.createElement('button'); button.className = 'quick-reply'; button.textContent = label; button.onclick = () => sendMessage(text); container.append(button); }
  messages.append(container); messages.scrollTop = messages.scrollHeight;
}
function showTyping() { const node = document.createElement('div'); node.className = 'bubble bot typing'; node.textContent = 'JeevanSetu AI is typing…'; messages.append(node); messages.scrollTop = messages.scrollHeight; return node; }
function resetChat() { language = null; voiceMessageReady = false; messages.replaceChildren(); input.value = ''; input.placeholder = 'Type a health question'; languageMenu(); input.focus(); }
function speakReply(text, replyLanguage) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  const targetLanguage = { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' }[replyLanguage] || 'en-IN';
  utterance.lang = targetLanguage;
  const languagePrefix = targetLanguage.slice(0, 2).toLowerCase();
  const matchingVoice = window.speechSynthesis.getVoices().find((voice) => voice.lang.toLowerCase().startsWith(languagePrefix));
  if (matchingVoice) utterance.voice = matchingVoice;
  utterance.rate = 0.95;
  window.speechSynthesis.speak(utterance);
}
function start() { languageMenu(); }
async function sendMessage(message, shouldSpeakReply = false) {
  message = message.trim(); if (!message) return;
  if (!language) { languageMenu(); return; }
  addBubble(message, 'user'); input.value = ''; input.disabled = true; status.textContent = 'Sending to M2 backend…'; const typing = showTyping();
  try {
    const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({user_id:userId, message, language, channel:'whatsapp'}) });
    const data = await res.json(); const type = data.safety_level === 'emergency' ? 'bot emergency' : 'bot';
    typing.remove(); addBubble(data.response, type, `${data.category} • ${data.safety_level}${data.source === 'fallback' ? ' • offline fallback' : ''}`); if (shouldSpeakReply) speakReply(data.response, data.language);
  } catch (_) { typing.remove(); addBubble('Could not contact the chat service. Please try again.', 'bot emergency'); }
  finally { input.disabled = false; status.textContent = 'Health assistant • online'; input.focus(); }
}
form.addEventListener('submit', (event) => { event.preventDefault(); const shouldSpeakReply = voiceMessageReady; voiceMessageReady = false; sendMessage(input.value, shouldSpeakReply); });
input.addEventListener('input', () => { voiceMessageReady = false; });
resetButton.addEventListener('click', resetChat);

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SpeechRecognition) {
  voiceButton.disabled = true;
  voiceButton.title = 'Voice input is not supported in this browser. Use Chrome or Edge.';
} else {
  const recognition = new SpeechRecognition();
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  let voiceTextCaptured = false;
  voiceButton.addEventListener('click', () => {
    if (!language) { addBubble('Please choose a language before using voice input.'); return; }
    voiceTextCaptured = false;
    recognition.lang = { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' }[language];
    recognition.start();
  });
  recognition.onstart = () => { voiceButton.classList.add('listening'); voiceButton.textContent = '■'; status.textContent = 'Listening… Speak now'; };
  recognition.onresult = (event) => {
    const spokenText = event.results[0][0].transcript;
    voiceTextCaptured = true;
    voiceMessageReady = false;
    status.textContent = 'Voice message sent — JeevanSetu AI is responding…';
    sendMessage(spokenText, true);
  };
  recognition.onerror = (event) => { if (event.error !== 'aborted') addBubble(`Voice input error: ${event.error}. Please try again or type your question.`, 'bot'); };
  recognition.onend = () => { voiceButton.classList.remove('listening'); voiceButton.textContent = '🎙'; if (!voiceTextCaptured) status.textContent = 'Health assistant • online'; };
}
start();
