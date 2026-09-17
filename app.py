<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Nexora AI</title>

<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    --bg: #ffffff;
    --sidebar: #f7f7f8;
    --text: #202123;
    --muted: #6b7280;
    --border: #e5e7eb;
    --hover: #ececec;
    --card: #ffffff;
    --input: #ffffff;
    --accent: #111827;
    --user: #f0f0f0;
}

body.dark {
    --bg: #212121;
    --sidebar: #171717;
    --text: #f5f5f5;
    --muted: #a1a1aa;
    --border: #3a3a3a;
    --hover: #2f2f2f;
    --card: #212121;
    --input: #2f2f2f;
    --accent: #ffffff;
    --user: #343434;
}

body {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Arial,
        sans-serif;

    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow: hidden;
}

/* =========================
   APP
========================= */

.app {
    display: flex;
    height: 100vh;
    width: 100%;
}

/* =========================
   SIDEBAR
========================= */

.sidebar {
    width: 270px;
    background: var(--sidebar);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    padding: 12px;
    transition: 0.25s;
    flex-shrink: 0;
}

.logo-area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 20px;
}

.logo-icon {
    width: 34px;
    height: 34px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(
        135deg,
        #06b6d4,
        #6366f1,
        #a855f7
    );
    color: white;
    font-weight: 800;
}

.icon-btn {
    width: 38px;
    height: 38px;
    border: none;
    background: transparent;
    color: var(--text);
    border-radius: 9px;
    cursor: pointer;
    font-size: 20px;
}

.icon-btn:hover {
    background: var(--hover);
}

.new-chat {
    width: 100%;
    border: 1px solid var(--border);
    background: var(--card);
    color: var(--text);
    padding: 12px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 14px;
    text-align: left;
    margin-bottom: 14px;
}

.new-chat:hover {
    background: var(--hover);
}

.sidebar-title {
    font-size: 12px;
    color: var(--muted);
    padding: 8px 10px;
}

.history {
    flex: 1;
    overflow-y: auto;
}

.history-item {
    padding: 10px;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.history-item:hover {
    background: var(--hover);
}

.sidebar-bottom {
    border-top: 1px solid var(--border);
    padding-top: 10px;
}

.sidebar-option {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 10px;
    border-radius: 9px;
    cursor: pointer;
    font-size: 14px;
}

.sidebar-option:hover {
    background: var(--hover);
}

/* =========================
   MAIN
========================= */

.main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
}

/* =========================
   TOP BAR
========================= */

.topbar {
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 18px;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
}

.top-left {
    display: flex;
    align-items: center;
    gap: 10px;
}

.mobile-menu {
    display: none;
}

.model-selector {
    border: none;
    background: transparent;
    color: var(--text);
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    padding: 8px 10px;
    border-radius: 8px;
}

.model-selector:hover {
    background: var(--hover);
}

.top-right {
    display: flex;
    align-items: center;
    gap: 5px;
}

/* =========================
   CHAT AREA
========================= */

.chat-area {
    flex: 1;
    overflow-y: auto;
    scroll-behavior: smooth;
}

.welcome {
    min-height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 30px 20px 180px;
}

.welcome-logo {
    width: 62px;
    height: 62px;
    border-radius: 20px;
    background:
        linear-gradient(
            135deg,
            #06b6d4,
            #6366f1,
            #a855f7
        );

    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 30px;
    font-weight: 800;
    box-shadow: 0 8px 35px rgba(99,102,241,.25);
}

.welcome h1 {
    margin-top: 22px;
    font-size: 30px;
    text-align: center;
}

.welcome p {
    margin-top: 8px;
    color: var(--muted);
    text-align: center;
    font-size: 15px;
}

.quick-grid {
    width: min(850px, 100%);
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-top: 38px;
}

.quick-card {
    border: 1px solid var(--border);
    background: var(--card);
    border-radius: 13px;
    padding: 16px;
    cursor: pointer;
    transition: .2s;
}

.quick-card:hover {
    background: var(--hover);
    transform: translateY(-1px);
}

.quick-icon {
    font-size: 21px;
    margin-bottom: 9px;
}

.quick-title {
    font-weight: 600;
    font-size: 14px;
}

.quick-text {
    margin-top: 5px;
    color: var(--muted);
    font-size: 13px;
}

/* =========================
   MESSAGES
========================= */

.messages {
    max-width: 850px;
    margin: 0 auto;
    padding: 25px 18px 180px;
    width: 100%;
}

.message {
    display: flex;
    gap: 13px;
    margin-bottom: 28px;
}

.message.user {
    justify-content: flex-end;
}

.message-content {
    max-width: 78%;
}

.user .message-content {
    background: var(--user);
    padding: 11px 15px;
    border-radius: 17px;
}

.avatar {
    width: 31px;
    height: 31px;
    min-width: 31px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(
        135deg,
        #06b6d4,
        #6366f1,
        #a855f7
    );
    color: white;
    font-size: 13px
