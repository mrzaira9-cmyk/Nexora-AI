<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexora AI — Multi-Feature Dashboard</title>
    <!-- Tailwind CSS for Modern UI -->
    <script src="https://jsdelivr.net"></script>
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cloudflare.com">
</head>
<body class="bg-gray-900 text-gray-100 font-sans h-screen flex overflow-hidden">

    <!-- 1. SIDEBAR: Chat History & Account -->
    <div class="w-80 bg-gray-950 flex flex-col justify-between border-r border-gray-800 hidden md:flex">
        <div class="p-4 flex flex-col flex-1 overflow-y-auto">
            <!-- App Logo & Title -->
            <div class="flex items-center gap-3 mb-6">
                <div class="bg-blue-600 p-2 rounded-lg text-white font-bold text-xl">🚀</div>
                <h1 class="text-xl font-bold tracking-wide">Nexora AI</h1>
            </div>

            <!-- New Chat Button -->
            <button onclick="newChat()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition mb-6 shadow-lg">
                <i class="fa-solid class='fa-plus'"></i> New Chat
            </button>

            <!-- Search Chats -->
            <div class="relative mb-4">
                <input type="text" placeholder="Search chats..." class="w-full bg-gray-900 border border-gray-700 rounded-lg py-1.5 pl-9 pr-4 text-sm focus:outline-none focus:border-blue-500">
                <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-gray-500 text-sm"></i>
            </div>

            <!-- Chat History List -->
            <div class="flex-1">
                <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Recent Conversations</p>
                <div class="space-y-1" id="chat-history-list">
                    <div class="flex items-center justify-between p-2 rounded-lg bg-gray-800 group cursor-pointer">
                        <div class="flex items-center gap-2 truncate">
                            <i class="fa-regular fa-comment text-gray-400"></i>
                            <span class="text-sm truncate" id="chat-title-1">Python Flask Setup Guide</span>
                        </div>
                        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                            <button onclick="renameChat(1)" class="text-gray-400 hover:text-white p-1 text-xs"><i class="fa-solid fa-pen"></i></button>
                            <button onclick="deleteChat(this)" class="text-red-400 hover:text-red-500 p-1 text-xs"><i class="fa-solid fa-trash"></i></button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- User Profile & Admin Settings Footer -->
        <div class="p-4 border-t border-gray-800 bg-gray-950 flex flex-col gap-2">
            <button onclick="openModal('devSettingsModal')" class="w-full text-left text-sm text-gray-400 hover:text-white flex items-center gap-2 p-2 rounded-lg hover:bg-gray-900 transition">
                <i class="fa-solid fa-sliders"></i> Developer / Admin Settings
            </button>
            <div class="flex items-center justify-between p-2 rounded-lg bg-gray-900">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center font-bold text-sm text-white">U</div>
                    <div>
                        <p class="text-sm font-medium">Aman Kumar</p>
                        <p class="text-xs text-gray-500">Pro Account</p>
                    </div>
                </div>
                <button onclick="openModal('accountModal')" class="text-gray-400 hover:text-white"><i class="fa-solid fa-gear"></i></button>
            </div>
        </div>
    </div>

    <!-- MAIN INTERFACE AREA -->
    <div class="flex-1 flex flex-col h-full bg-gray-900">
        
        <!-- 2. TOP NAVBAR: Model Controls & Web Search Toggle -->
        <header class="h-16 border-b border-gray-800 flex items-center justify-between px-6 bg-gray-900/50 backdrop-blur-md z-10">
            <div class="flex items-center gap-4">
                <!-- AI Model Selector -->
                <select id="modelSelect" class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-blue-500 cursor-pointer">
                    <option value="nexora-fast">🤖 Nexora AI - Fast (Default)</option>
                    <option value="nexora-pro">🧠 Nexora AI - Pro (Advanced Context)</option>
                    <option value="nexora-vision">🖼️ Nexora Vision (Image Analysis)</option>
                </select>

                <!-- Web Search Toggle -->
                <label class="relative inline-flex items-center cursor-pointer select-none">
                    <input type="checkbox" id="webSearchToggle" class="sr-only peer">
                    <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    <span class="ms-3 text-sm font-medium text-gray-300 flex items-center gap-1"><i class="fa-solid fa-earth-americas text-blue-400"></i> Web Search</span>
                </label>
            </div>

            <!-- Voice Controls Toolbar -->
            <div class="flex items-center gap-3">
                <button onclick="toggleVoiceOutput()" id="voiceOutputBtn" class="p-2 rounded-lg bg-gray-800 border border-gray-700 text-gray-300 hover:text-white title='Toggle Text-to-Speech'">
                    <i id="voiceIcon" class="fa-solid fa-volume-high"></i>
                </button>
                <button onclick="openModal('voiceConfigModal')" class="text-sm bg-gray-800 hover:bg-gray-700 border border-gray-700 px-3 py-1.5 rounded-lg flex items-center gap-1">
                    <i class="fa-solid fa-microphone-lines"></i> Voice Settings
                </button>
            </div>
        </header>

        <!-- 3. CHAT MESSAGES STREAM -->
        <main class="flex-1 overflow-y-auto p-6 space-y-6 flex flex-col justify-end" id="chat-window">
            <!-- Initial AI Message with Memory / Instructions State -->
            <div class="flex items-start gap-4 max-w-3xl">
                <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shrink-0 shadow-md">🤖</div>
                <div class="bg-gray-800/60 border border-gray-700/50 rounded-2xl p-4 rounded-tl-none shadow-sm">
                    <p class="text-sm leading-relaxed mb-2 text-gray-200">Pranam! Main Nexora AI hun. Main Hindi, English aur anya bhashao ko samajh sakta hun. Main aapki text questions, files, aur images ko process karne ke liye taiyar hun. Bantiye aaj main aapki kya sahayata karu?</p>
                    <div class="flex items-center gap-3 mt-3 text-xs text-gray-400 border-t border-gray-700/50 pt-2">
                        <button onclick="copyText('Pranam! Main Nexora AI...')" class="hover:text-white flex items-center gap-1"><i class="fa-regular fa-copy"></i> Copy</button>
                        <button onclick="reactMessage(this, 'like')" class="hover:text-blue-400 flex items-center gap-1"><i class="fa-regular fa-thumbs-up"></i> Like</button>
                        <button onclick="reactMessage(this, 'dislike')" class="hover:text-red-400 flex items-center gap-1"><i class="fa-regular fa-thumbs-down"></i> Dislike</button>
                        <button onclick="speakMessage('Pranam! Main Nexora AI hun.')" class="hover:text-green-400 flex items-center gap-1"><i class="fa-solid fa-volume-high"></i> Speak</button>
                    </div>
                </div>
            </div>
        </main>

        <!-- 4. BOTTOM INPUT CONTROLS SYSTEM -->
        <footer class="p-4 bg-gray-900 border-t border-gray-800">
            <div class="max-w-4xl mx-auto flex flex-col gap-2">
                <!-- Attachments Feedback Badges Panel -->
                <div id="attachment-badge-panel" class="flex flex-wrap gap-2 empty:hidden"></div>

                <div class="bg-gray-800 border border-gray-700 rounded-xl p-2 flex flex-col shadow-inner">
                    <!-- Text Area Input -->
                    <textarea id="userInput" rows="2" placeholder="Ask Nexora anything... (or use microphone for voice input)" class="w-full bg-transparent resize-none focus:outline-none p-2 text-sm text-gray-100 placeholder-gray-500"></textarea>
                    
                    <!-- Controls Bar inside Input Field -->
                    <div class="flex items-center justify-between border-t border-gray-700/60 pt-2 px-1 mt-1">
                        <div class="flex items-center gap-1.5">
                            <!-- Image Upload Hidden Trigger -->
                            <input type="file" id="imageFile" accept="image/*" class="hidden" onchange="handleAttachment(this, 'Image')">
                            <button onclick="document.getElementById('imageFile').click()" class="p-2 text-gray-400 hover:text-blue-400 hover:bg-gray-700/50 rounded-lg transition" title="Upload Image / Image Editing"><i class="fa-regular fa-image text-base"></i></button>

                            <!-- Document File Upload Hidden Trigger -->
                            <input type="file" id="docFile" accept=".pdf,.docx,.txt,.csv" class="hidden" onchange="handleAttachment(this, 'Document')">
