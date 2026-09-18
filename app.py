<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT Clone UI</title>
    <!-- Tailwind CSS for modern and clean design -->
    <script src="https://jsdelivr.net"></script>
    <!-- FontAwesome for exact match icons -->
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        /* Custom scrollbar hiding for clean mobile view */
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="bg-white text-gray-800 font-sans h-screen flex flex-col justify-between overflow-hidden">

    <!-- 1. TOP HEADER BAR -->
    <header class="flex justify-between items-center px-4 py-3 bg-white border-b border-gray-100 sticky top-0 z-50">
        <!-- Sidebar Menu Icon -->
        <button class="text-2xl text-gray-600 focus:outline-none">
            <i class="fa-solid fa-bars-staggered"></i>
        </button>
        <!-- Right Action Icons (New Chat & Menu) -->
        <div class="flex items-center gap-5">
            <button class="text-xl text-gray-600 focus:outline-none">
                <i class="fa-regular fa-pen-to-square"></i>
            </button>
            <button class="text-xl text-gray-600 focus:outline-none">
                <i class="fa-solid fa-ellipsis-vertical"></i>
            </button>
        </div>
    </header>

    <!-- 2. CHAT MESSAGES AREA -->
    <main id="chat-container" class="flex-1 overflow-y-auto px-4 py-4 space-y-6 no-scrollbar">
        <!-- User Initials / Profile Marker (Top Right Corner inside chat if needed, matching 'H') -->
        <div class="flex justify-end mb-2">
            <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm">
                H
            </div>
        </div>

        <!-- ChatGPT Response Box -->
        <div class="space-y-3 max-w-3xl">
            <!-- Bot Answer Text -->
            <p id="bot-response" class="text-[16px] leading-relaxed text-gray-900 font-normal">
                हाँ भाई 😊 बताइए, क्या करना है?
            </p>

            <!-- THE 6 OPTIONS TOOLBAR (Exact Match) -->
            <div class="flex items-center gap-5 text-gray-400 text-[15px] pt-1 pl-1">
                <!-- 1. Copy -->
                <button class="hover:text-gray-600 transition-colors" title="Copy"><i class="fa-regular fa-copy"></i></button>
                <!-- 2. Thumbs Up -->
                <button class="hover:text-gray-600 transition-colors" title="Like"><i class="fa-regular fa-thumbs-up"></i></button>
                <!-- 3. Thumbs Down -->
                <button class="hover:text-gray-600 transition-colors" title="Dislike"><i class="fa-regular fa-thumbs-down"></i></button>
                <!-- 4. Read Aloud / Speaker -->
                <button class="hover:text-gray-600 transition-colors" title="Read Aloud"><i class="fa-solid fa-volume-high"></i></button>
                <!-- 5. Share -->
                <button class="hover:text-gray-600 transition-colors" title="Share"><i class="fa-solid fa-share-nodes"></i></button>
                <!-- 6. More (Three Dots) -->
                <button class="hover:text-gray-600 transition-colors" title="More"><i class="fa-solid fa-ellipsis-vertical"></i></button>
            </div>
        </div>
    </main>

    <!-- 3. BOTTOM INPUT BAR -->
    <footer class="p-3 bg-white border-t border-gray-100">
        <div class="flex items-center gap-3 max-w-3xl mx-auto bg-gray-100 rounded-full px-4 py-2.5">
            <!-- Attachment Plus Icon -->
            <button class="text-gray-500 text-xl focus:outline-none">
                <i class="fa-solid fa-plus"></i>
            </button>
            
            <!-- Input Text Box -->
            <input type="text" id="user-input" placeholder="Reply to ChatGPT" 
                   class="flex-1 bg-transparent border-none outline-none text-[15px] text-gray-800 placeholder-gray-400">
            
            <!-- Microphone Icon -->
            <button class="text-gray-500 text-lg focus:outline-none">
                <i class="fa-solid fa-microphone"></i>
            </button>
            
            <!-- Voice Mode / Audio Wave Blue Button -->
            <button onclick="simulateFastResponse()" class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center focus:outline-none shadow-sm hover:bg-blue-700 transition-all">
                <i class="fa-solid fa-waveform text-xs"></i>
            </button>
        </div>
    </footer>

    <!-- JAVASCRIPT FOR FAST AUTO-SCROLL AND STREAMING EFFECT -->
    <script>
        const chatContainer = document.getElementById('chat-container');
        const botResponse = document.getElementById('bot-response');

        // Fast Auto-Scroll Function
        function fastScrollToBottom() {
            // instant scroll setup for lightning fast responses
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Test Function: Fast Response Typing Simulation
        function simulateFastResponse() {
            const sampleText = "आपका कोड अब बिल्कुल तैयार है भाई! इसमें ऑटो-स्क्रॉलिंग को फ़ास्ट कर दिया गया है और नीचे दिए गए छह ऑप्शंस भी जोड़ दिए गए हैं।";
            botResponse.innerHTML = "";
            let i = 0;
            
            // Fast Interval for Streaming Text Effect
            const interval = setInterval(() => {
                if (i < sampleText.length) {
                    botResponse.innerHTML += sampleText.charAt(i);
                    i++;
                    fastScrollToBottom(); // Keeps scrolling instantly as text generates
                } else {
                    clearInterval(interval);
                }
            }, 20); // 20ms for super-fast text delivery
        }
    </script>
</body>
</html>
