import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ----------------- 1. DATABASE SETUP (डेटाबेस सेटअप) -----------------
# यह कोड आपके कंप्यूटर पर अपने आप एक डेटाबेस फ़ाइल बनाएगा ताकि पुरानी चैट सेव रहे
DB_FILE = "nexora_chat.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # चैट मैसेजेस को सेव करने के लिए टेबल
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ऐप शुरू होते ही डेटाबेस को चालू करें
init_db()


# ----------------- 2. HTML, CSS & JS FRONTEND (डिजाइन और स्क्रिप्ट) -----------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexora AI Chat Interface</title>
    <link href="https://googleapis.com" rel="stylesheet">
    <link rel="stylesheet" href="https://cloudflare.com">
    
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Noto Sans Devanagari', 'Roboto', sans-serif; }
        body { display: flex; height: 100vh; background-color: #f7f9fc; color: #333; overflow: hidden; }
        
        /* Sidebar Styles */
        .sidebar { width: 300px; background-color: #172237; color: #fff; display: flex; flex-direction: column; justify-content: space-between; padding: 20px 0; flex-shrink: 0; }
        .brand-section { display: flex; align-items: center; padding: 0 20px 20px 20px; border-bottom: 1px solid #243452; }
        .brand-logo-small { width: 36px; height: 36px; background: linear-gradient(135deg, #2f54eb, #1890ff); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 20px; margin-right: 12px; }
        .brand-name-sidebar { font-size: 18px; font-weight: 600; }
        .new-chat-btn { margin: 20px; padding: 12px; background-color: transparent; border: 1px solid #364e79; color: #fff; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 10px; font-size: 14px; transition: 0.3s; width: calc(100% - 40px); text-align: left; }
        .new-chat-btn:hover { background-color: #243452; }
        .history-section { flex-grow: 1; padding: 0 20px; overflow-y: auto; }
        .history-title { font-size: 12px; color: #7289ad; text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.5px; }
        .history-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; color: #b0c4de; font-size: 14px; cursor: pointer; transition: 0.2s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .history-item:hover { color: #fff; }
        .sidebar-footer { padding: 20px; border-top: 1px solid #243452; display: flex; flex-direction: column; gap: 15px; }
        .footer-link { display: flex; align-items: center; gap: 12px; color: #b0c4de; font-size: 14px; text-decoration: none; cursor: pointer; }
        .footer-link:hover { color: #fff; }

        /* Main Screen Styles */
        .main-container { flex-grow: 1; display: flex; flex-direction: column; height: 100%; background-color: #f8fafc; }
        .main-header { display: flex; align-items: center; justify-content: space-between; padding: 15px 30px; background-color: #fff; border-bottom: 1px solid #eef2f6; }
        .header-left { display: flex; align-items: center; gap: 20px; }
        .menu-toggle { font-size: 20px; cursor: pointer; color: #555; }
        .header-title { font-size: 20px; font-weight: 600; color: #1e293b; }
        .header-right { display: flex; align-items: center; gap: 20px; font-size: 18px; color: #555; }
        .header-right i { cursor: pointer; }

        /* Chat Feed Area */
        .chat-feed { flex-grow: 1; padding: 40px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .welcome-section { text-align: center; margin-bottom: 40px; width: 100%; }
        .large-logo { width: 80px; height: 80px; background: linear-gradient(135deg, #3b82f6, #1d4ed8); border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 45px; color: #fff; font-weight: bold; margin: 0 auto 20px auto; box-shadow: 0 10px 25px rgba(59, 130, 246, 0.25); }
        .welcome-title { font-size: 32px; color: #1e293b; font-weight: 700; margin-bottom: 8px; }
        .welcome-subtitle { font-size: 18px; color: #64748b; }

        /* Cards Layout */
        .suggestions-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; width: 100%; max-width: 700px; margin-bottom: 40px; }
        .card { background-color: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; display: flex; gap: 15px; cursor: pointer; transition: all 0.2s ease; }
        .card:hover { border-color: #cbd5e1; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); transform: translateY(-1px); }
        .card-icon-box { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
        
        .bg-blue   { background-color: #eff6ff; color: #3b82f6; }
        .bg-purple { background-color: #faf5ff; color: #a855f7; }
        .bg-green  { background-color: #f0fdf4; color: #22c55e; }
        .bg-orange { background-color: #fff7ed; color: #f97316; }

        .card-content h3 { font-size: 16px; color: #1e293b; font-weight: 600; margin-bottom: 4px; }
        .card-content p { font-size: 13px; color: #64748b; }

        /* Message Bubbles */
        .message-container { width: 100%; max-width: 700px; background-color: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.01); }
        .message-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
        .msg-logo { width: 28px; height: 28px; background: linear-gradient(135deg, #3b82f6, #1d4ed8); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 14px; color: #fff; font-weight: bold; }
        .msg-author { font-size: 13px; font-weight: 600; color: #475569; }
        .message-body { font-size: 15px; color: #334155; line-height: 1.6; white-space: pre-line; }
        .message-actions { display: flex; gap: 16px; margin-top: 15px; padding-top: 12px; border-top: 1px solid #f1f5f9; color: #94a3b8; font-size: 15px; }
        .action-btn { cursor: pointer; transition: color 0.2s; }
        .action-btn:hover { color: #475569; }

        /* Input Controls */
        .chat-input-container { padding: 20px 40px; background-color: #f8fafc; display: flex; justify-content: center; align-items: center; flex-shrink: 0; }
        .input-wrapper { width: 100%; max-width: 700px; background-color: #fff; border: 1px solid #cbd5e1; border-radius: 30px; padding: 6px 8px 6px 20px; display: flex; align-items: center; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02); }
        .input-wrapper input { flex-grow: 1; border: none; outline: none; font-size: 15px; color: #333; padding: 8px 0; }
        .input-wrapper input::placeholder { color: #94a3b8; }
        .mic-btn { background: none; border: none; color: #64748b; font-size: 18px; padding: 10px; cursor: pointer; margin-right: 5px; }
        .send-btn { background-color: #172237; color: #fff; border: none; width: 40px; height: 40px; border-radius: 50px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 16px; flex-shrink: 0; }
        .send-btn:hover { background-color: #0f172a; }
    </style>
</head>
<body>

    <div class="sidebar">
        <div>
            <div class="brand-section">
                <div class="brand-logo-small">N</div>
                <div class="brand-name-sidebar">Nexora AI</div>
            </div>
            
            <button class="new-chat-btn" onclick="clearAllChatHistory()">
                <i class="fa-solid fa-trash-can"></i> Clear Chat History
            </button>

            <div class="history-section">
                <div class="history-title">History</div>
                <!-- डेटाबेस से आई पुरानी हिस्ट्री यहाँ अपने आप लोड होगी -->
                <div id="dynamicHistoryList"></div>
            </div>
        </div>

        <div class="sidebar-footer">
            <a class="footer-link"><i class="fa-solid fa-gear"></i> Settings</a>
            <a class="footer-link"><i class="fa-regular fa-circle-question"></i> Help</a>
        </div>
    </div>

    <div class="main-container">
        <header class="main-header">
            <div class="header-left">
                <i class="fa-solid fa-bars menu-toggle"></i>
                <span class="header-title">Nexora AI</span>
            </div>
            <div class="header-right">
                <i class="fa-solid fa-magnifying-glass"></i>
                <i class="fa-solid fa-ellipsis-vertical" style="margin-left: 15px;"></i>
            </div>
        </header>

        <div class="chat-feed" id="chatFeed">
            <div class="welcome-section" id="welcomeSection">
                <div class="large-logo">N</div>
                <h1 class="welcome-title">Nexora AI</h1>
                <p class="welcome-subtitle">मुझसे कुछ भी पूछिए</p>
            </div>

            <div class="suggestions-grid" id="suggestionsGrid">
                <div class="card" onclick="selectSuggestion('भारत की राजधानी क्या है?')">
                    <div class="card-icon-box bg-blue"><i class="fa-regular fa-lightbulb"></i></div>
                    <div class="card-content"><h3>जानकारी पूछें</h3><p>भारत की राजधानी क्या है?</p></div>
                </div>
                
