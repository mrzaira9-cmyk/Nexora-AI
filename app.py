<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nexora AI</title>
  <!-- Font Awesome Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    body {
      display: flex;
      height: 100vh;
      background-color: #f8f9fa;
      color: #1e1e1e;
      overflow: hidden;
    }

    /* ---------- SIDEBAR ---------- */
    .sidebar {
      width: 260px;
      background-color: #181d28;
      color: #ffffff;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 16px;
      transition: all 0.3s ease;
      z-index: 100;
    }

    .sidebar.closed {
      margin-left: -260px;
    }

    .sidebar-top {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 4px 0;
    }

    .brand-icon {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 18px;
    }

    .brand-name {
      font-size: 18px;
      font-weight: 600;
    }

    .new-chat-btn {
      display: flex;
      align-items: center;
      gap: 10px;
      background-color: #242b3b;
      color: #ffffff;
      border: 1px solid #333d52;
      border-radius: 12px;
      padding: 10px 14px;
      font-size: 14px;
      cursor: pointer;
      transition: background 0.2s;
    }

    .new-chat-btn:hover {
      background-color: #2e374d;
    }

    .history-title {
      font-size: 12px;
      color: #8e9bb0;
      margin-top: 10px;
    }

    .history-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
      max-height: 50vh;
      overflow-y: auto;
    }

    .history-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 10px;
      border-radius: 8px;
      font-size: 13px;
      color: #d1d5db;
      cursor: pointer;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .history-item:hover {
      background-color: #242b3b;
      color: #fff;
    }

    .sidebar-bottom {
      display: flex;
      flex-direction: column;
      gap: 8px;
      border-top: 1px solid #283144;
      padding-top: 12px;
    }

    .nav-btn {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 10px;
      border-radius: 8px;
      color: #d1d5db;
      font-size: 14px;
      cursor: pointer;
      background: none;
      border: none;
      text-align: left;
      width: 100%;
    }

    .nav-btn:hover {
      background-color: #242b3b;
      color: #fff;
    }

    /* ---------- MAIN CONTAINER ---------- */
    .main-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100vh;
      position: relative;
    }

    /* Header */
    .top-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      background-color: #ffffff;
      border-bottom: 1px solid #f0f0f0;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .toggle-btn {
      background: none;
      border: none;
      font-size: 18px;
      cursor: pointer;
      color: #4b5563;
    }

    .header-title {
      font-size: 18px;
      font-weight: 600;
    }

    .header-right {
      display: flex;
      gap: 16px;
      color: #4b5563;
      font-size: 16px;
    }

    .header-right i {
      cursor: pointer;
    }

    /* Chat Area */
    .chat-area {
      flex: 1;
      overflow-y: auto;
      padding: 20px 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .chat-content {
      width: 100%;
      max-width: 680px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    /* Hero Section */
    .hero-section {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      margin: 15px 0 25px 0;
    }

    .hero-logo {
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      border-radius: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 44px;
      font-weight: bold;
      margin-bottom: 16px;
      box-shadow: 0 8px 20px rgba(59, 130, 246, 0.25);
    }

    .hero-title {
      font-size: 26px;
      font-weight: 700;
      color: #111827;
      margin-bottom: 6px;
    }

    .hero-subtitle {
      font-size: 15px;
      color: #6b7280;
    }

    /* Prompt Cards */
    .cards-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      width: 100%;
      margin-bottom: 24px;
    }

    .card {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      padding: 14px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      gap: 12px;
    }

    .card:hover {
      border-color: #3b82f6;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    .card-icon {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      flex-shrink: 0;
    }

    .card-icon.blue { background-color: #eff6ff; color: #2563eb; }
    .card-icon.purple { background-color: #faf5ff; color: #9333ea; }
    .card-icon.green { background-color: #f0fdf4; color: #16a34a; }
    .card-icon.orange { background-color: #fff7ed; color: #ea580c; }

    .card-text h4 {
      font-size: 14px;
      font-weight: 600;
      color: #1f2937;
      margin-bottom: 2px;
    }

    .card-text p {
      font-size: 12px;
      color: #6b7280;
    }

    /* Messages */
    .message {
      display: flex;
      flex-direction: column;
      gap: 8px;
      width: 100%;
    }

    .message.ai {
      background-color: #f3f4f6;
      border-radius: 16px;
      padding: 16px;
    }

    .message.user {
      align-items: flex-end;
    }

    .user-bubble {
      background-color: #3b82f6;
      color: white;
      padding: 12px 16px;
      border-radius: 16px;
      border-bottom-right-radius: 4px;
      max-width: 80%;
      font-size: 14px;
    }

    .message-header {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .avatar {
      width: 28px;
      height: 28px;
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: bold;
      font-size: 14px;
    }

    .bot-name {
      font-size: 13px;
      font-weight: 600;
      color: #374151;
    }

    .message-body {
      font-size: 14px;
      line-height: 1.5;
      color: #1f2937;
    }

    /* Action Toolbar */
    .action-bar {
      display: flex;
      gap: 16px;
      margin-top: 8px;
      color: #6b7280;
      font-size: 14px;
    }

    .action-bar i {
      cursor: pointer;
      transition: color 0.2s;
    }

    .action-bar i:hover {
      color: #111827;
    }

    .action-bar i.active-like {
      color: #16a34a;
    }

    .action-bar i.active-dislike {
      color: #dc2626;
    }

    /* Bottom Input Bar */
    .input-container {
      padding: 12px 16px 20px 16px;
      background-color: #ffffff;
      display: flex;
      justify-content: center;
    }

    .input-box {
      width: 100%;
      max-width: 680px;
      background-color: #f3f4f6;
      border: 1px solid #e5e7eb;
      border-radius: 28px;
      display: flex;
      align-items: center;
      padding: 6px 12px 6px 18px;
    }

    .input-box input {
      flex: 1;
      border: none;
      outline: none;
      background: transparent;
      font-size: 14px;
      color: #1f2937;
    }

    .input-btn {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      margin-left: 6px;
      background: transparent;
      color: #4b5563;
      font-size: 15px;
    }

    .input-btn.send-btn {
      background-color: #000000;
      color: #ffffff;
    }

    .input-btn.send-btn:hover {
      background-color: #1f2937;
    }

    /* Responsive */
    @media (max-width: 640px) {
      .sidebar {
        position: absolute;
        height: 100%;
      }
      .cards-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>

  <!-- SIDEBAR -->
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-top">
      <div class="brand">
        <div class="brand-icon">N</div>
        <div class="brand-name">Nexora AI</div>
      </div>

      <button class="new-chat-btn" onclick="startNewChat()">
        <i class="fa-regular fa-comment"></i>
        <span>New Chat</span>
      </button>

      <div class="history-title">History</div>
      <div class="history-list" id="historyList">
        <div class="history-item" onclick="loadHistory(this)"><i class="fa-regular fa-message"></i> भारत की राजधानी क्या है?</div>
        <div class="history-item" onclick="loadHistory(this)"><i class="fa-regular fa-message"></i> Python सीखने की शुरुआत</div>
        <div class="history-item" onclick="loadHistory(this)"><i class="fa-regular fa-message"></i> आज का productivity plan</div>
        <div class="history-item" onclick="loadHistory(this)"><i class="fa-regular fa-message"></i> एक मज़ेदार कहानी सुनाइए</div>
        <div class="history-item" onclick="loadHistory(this)"><i class="fa-regular fa-message"></i> हेल्थ टिप्स</div>
        <div class="history-item" onclick="loadHistory(this)"><i class="fa-regular fa-message"></i> AI के बारे में जानकारी</div>
      </div>
    </div>

    <div class="sidebar-bottom">
      <button class="nav-btn" onclick="openSettings()">
        <i class="fa-solid fa-gear"></i>
        <span>Settings</span>
      </button>
      <button class="nav-btn" onclick="openHelp()">
        <i class="fa-regular fa-circle-question"></i>
        <span>Help</span>
      </button>
    </div>
  </aside>

  <!-- MAIN AREA -->
  <main class="main-container">
    <!-- Top Header -->
    <header class="top-header">
      <div class="header-left">
        <button class="toggle-btn" onclick="toggleSidebar()"><i class="fa-solid fa-bars"></i></button>
        <span class="header-title">Nexora AI</span>
      </div>
      <div class="header-right">
        <i class="fa-solid fa-magnifying-glass" onclick="alert('Search option click hua')"></i>
        <i class="fa-solid fa-ellipsis-vertical" onclick="alert('More options click hua')"></i>
      </div>
    </header>

    <!-- Chat Scroll Area -->
    <div class="chat-area">
      <div class="chat-content" id="chatContent">
        
        <!-- Hero Section -->
        <div class="hero-section" id="heroSection">
          <div class="hero-logo">N</div>
          <h2 class="hero-title">Nexora AI</h2>
          <p class="hero-subtitle">मुझसे कुछ भी पूछिए</p>
        </div>

        <!-- 4 Prompt Cards -->
        <div class="cards-grid" id="cardsGrid">
          <div class="card" onclick="sendQuickPrompt('मुझे किसी भी विषय पर जानकारी दीजिए')">
            <div class="card-icon blue"><i class="fa-regular fa-lightbulb"></i></div>
            <div class="card-text">
              <h4>जानकारी पूछें</h4>
              <p>किसी भी विषय पर सवाल पूछें</p>
            </div>
          </div>

          <div class="card" onclick="sendQuickPrompt('मुझे एक सुंदर कहानी या संदेश लिखकर दीजिए')">
            <div class="card-icon purple"><i class="fa-solid fa-pen-nib"></i></div>
            <div class="card-text">
              <h4>लिखने में मदद</h4>
              <p>कहानी, संदेश या लेख लिखें</p>
            </div>
          </div>

          <div class="card" onclick="sendQuickPrompt('मुझे कोडिंग और पढ़ाई में मदद की ज़रूरत है')">
            <div class="card-icon green"><i class="fa-solid fa-laptop-code"></i></div>
            <div class="card-text">
              <h4>सीखने में मदद</h4>
              <p>कोड और पढ़ाई में सहायता</p>
            </div>
          </div>

          <div class="card" onclick="sendQuickPrompt('मेरे आज के काम का योजना (Plan) बनाइए')">
            <div class="card-icon orange"><i class="fa-solid fa-braille"></i></div>
            <div class="card-text">
              <h4>योजना बनाएं</h4>
              <p>काम को आसान तरीके से व्यवस्थित करें</p>
            </div>
          </div>
        </div>

        <!-- Default Bot Greeting -->
        <div class="message ai">
          <div class="message-header">
            <div class="avatar">N</div>
            <span class="bot-name">Nexora AI</span>
          </div>
          <div class="message-body" id="greetingText">
            नमस्ते! मैं Nexora AI हूँ।<br>
            आप कुछ भी पूछ सकते हैं, मैं आपकी मदद करने के लिए हमेशा तैयार हूँ।
          </div>
          <!-- Action Buttons -->
          <div class="action-bar">
            <i class="fa-regular fa-copy" title="Copy" onclick="copyText('greetingText')"></i>
            <i class="fa-regular fa-thumbs-up" title="Like" onclick="toggleLike(this)"></i>
            <i class="fa-regular fa-thumbs-down" title="Dislike" onclick="toggleDislike(this)"></i>
            <i class="fa-solid fa-volume-high" title="Speak" onclick="speakText('greetingText')"></i>
            <i class="fa-solid fa-share-nodes" title="Share" onclick="shareContent()"></i>
            <i class="fa-solid fa-ellipsis-vertical" title="Option"></i>
          </div>
        </div>

      </div>
    </div>

    <!-- Input Box Bar -->
    <div class="input-container">
      <div class="input-box">
        <input type="text" id="userInput" placeholder="यहाँ अपना सवाल लिखें..." onkeypress="handleKeyPress(event)">
        <button class="input-btn" title="Voice Input" onclick="startVoiceInput()"><i class="fa-solid fa-microphone"></i></button>
        <button class="input-btn send-btn" title="Send" onclick="sendMessage()"><i class="fa-solid fa-paper-plane"></i></button>
      </div>
    </div>
  </main>

  <script>
    // Sidebar Toggle
    function toggleSidebar() {
      document.getElementById('sidebar').classList.toggle('closed');
    }

    // New Chat Reset
    function startNewChat() {
      const chatContent = document.getElementById('chatContent');
      // Reset layout to default state
      location.reload();
    }

    // Send Message Logic
    function sendMessage() {
      const input = document.getElementById('userInput');
      const text = input.value.trim();
      if (!text) return;

      appendUserMessage(text);
      input.value = '';

      // Add to sidebar history
      addToHistory(text);

      // Simulate AI Response
      setTimeout(() => {
        appendAiResponse("मैंने आपका सवाल प्राप्त कर लिया है: '" + text + "'। मैं इस पर प्रक्रिया कर रहा हूँ!");
      }, 600);
    }

    function sendQuickPrompt(promptText) {
      appendUserMessage(promptText);
      addToHistory(promptText);

      setTimeout(() => {
        appendAiResponse("ज़रूर! मैं आपकी इसमें पूरी सहायता करूँगा। बताइए आप कहाँ से शुरुआत करना चाहते हैं?");
      }, 600);
    }

    function appendUserMessage(text) {
      const chatContent = document.getElementById('chatContent');
      const userDiv = document.createElement('div');
      userDiv.className = 'message user';
      userDiv.innerHTML = `<div class="user-bubble">${escapeHtml(text)}</div>`;
      chatContent.appendChild(userDiv);
      scrollToBottom();
    }

    function appendAiResponse(text) {
      const chatContent = document.getElementById('chatContent');
      const aiDiv = document.createElement('div');
      aiDiv.className = 'message ai';
      const textId = 'msg-' + Date.now();

      aiDiv.innerHTML = `
        <div class="message-header">
          <div class="avatar">N</div>
          <span class="bot-name">Nexora AI</span>
        </div>
        <div class="message-body" id="${textId}">${escapeHtml(text)}</div>
        <div class="action-bar">
          <i class="fa-regular fa-copy" title="Copy" onclick="copyText('${textId}')"></i>
          <i class="fa-regular fa-thumbs-up" title="Like" onclick="toggleLike(this)"></i>
          <i class="fa-regular fa-thumbs-down" title="Dislike" onclick="toggleDislike(this)"></i>
          <i class="fa-solid fa-volume-high" title="Speak" onclick="speakText('${textId}')"></i>
          <i class="fa-solid fa-share-nodes" title="Share" onclick="shareContent()"></i>
          <i class="fa-solid fa-ellipsis-vertical" title="Option"></i>
        </div>
      `;
      chatContent.appendChild(aiDiv);
      scrollToBottom();
    }

    function handleKeyPress(e) {
      if (e.key === 'Enter') {
        sendMessage();
      }
    }

    function scrollToBottom() {
      const chatArea = document.querySelector('.chat-area');
      chatArea.scrollTop = chatArea.scrollHeight;
    }

    // Add to Sidebar History
    function addToHistory(text) {
      const historyList = document.getElementById('historyList');
      const item = document.createElement('div');
      item.className = 'history-item';
      item.onclick = function() { loadHistory(this); };
      item.innerHTML = `<i class="fa-regular fa-message"></i> ${escapeHtml(text)}`;
      historyList.prepend(item);
    }

    function loadHistory(element) {
      const text = element.innerText.trim();
      appendUserMessage(text);
      setTimeout(() => {
        appendAiResponse("यह आपके इतिहास (" + text + ") का विवरण है।");
      }, 500);
    }

    // Actions implementation
    function copyText(elementId) {
      const text = document.getElementById(elementId).innerText;
      navigator.clipboard.writeText(text).then(() => {
        alert('टेक्स्ट कॉपी हो गया है!');
      });
    }

    function toggleLike(element) {
      element.classList.toggle('active-like');
    }

    function toggleDislike(element) {
      element.classList.toggle('active-dislike');
    }

    function speakText(elementId) {
      const text = document.getElementById(elementId).innerText;
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'hi-IN';
        window.speechSynthesis.speak(utterance);
      } else {
        alert('आपकी ब्राउज़र में वॉइस सपोर्ट उपलब्ध नहीं है।');
      }
    }

    function shareContent() {
      if (navigator.share) {
        navigator.share({
          title: 'Nexora AI Chat',
          text: 'Nexora AI के साथ चैट करें!'
        }).catch(() => {});
      } else {
        alert('शेयर लिंक कॉपी कर लिया गया है!');
      }
    }

    function startVoiceInput() {
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'hi-IN';
        recognition.start();

        recognition.onresult = function(event) {
          const transcript = event.results[0][0].transcript;
          document.getElementById('userInput').value = transcript;
        };
      } else {
        alert('आपके ब्राउज़र में डायरेक्ट माइक इनपुट सपोर्ट नहीं है।');
      }
    }

    function openSettings() {
      alert('Settings Menu Open');
    }

    function openHelp() {
      alert('Help & Support Menu Open');
    }

    function escapeHtml(text) {
      return text
          .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }
  </script>
</body>
</html>
