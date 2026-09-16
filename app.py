import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, TextInput } from 'react-native';

export default function App() {
  const [currentMenu, setCurrentMenu] = useState('Chat');

  // Sidebar / Menu Items as per your list
  const menuItems = [
    { category: 'A. Chat Basics', items: ['New Chat', 'Chat History', 'Multilingual Chat', 'Rename/Delete Chat'] },
    { category: 'B. Answer Tools', items: ['👍 Like', '👎 Dislike', '🔊 Speak', '📋 Copy', '↗️ Share'] },
    { category: 'C. Voice', items: ['🎤 Mic', '🔊 Voice Reply', '⏸️ Pause', '⏹️ Stop', '⚙️ Voice Settings', 'Voice Selection'] },
    { category: 'D. Internet', items: ['🌐 Web Search', '📰 Latest Info', '🔗 Source Links', '🔎 Research'] },
    { category: 'E. Files & Images', items: ['📎 File Upload', '📄 PDF Read', '📊 Data Analysis', '🖼️ Vision', '🎨 Image Gen'] },
    { category: 'F. Advanced', items: ['🧠 Memory', '📁 Projects', '⏰ Tasks', '📝 Workspace'] },
  ];

  return (
    <View style={styles.container}>
      {/* Top Header */}
      <View style={styles.header}>
        <Text style={styles.headerText}>🤖 My Advanced AI Assistant</Text>
      </View>

      <View style={styles.mainBody}>
        {/* Left Sidebar for Options */}
        <ScrollView style={styles.sidebar} showsVerticalScrollIndicator={false}>
          {menuItems.map((sec, idx) => (
            <View key={idx} style={styles.sectionContainer}>
              <Text style={styles.sectionTitle}>{sec.category}</Text>
              {sec.items.map((item, itemIdx) => (
                <TouchableOpacity 
                  key={itemIdx} 
                  style={[styles.menuButton, currentMenu === item && styles.activeMenu]}
                  onPress={() => setCurrentMenu(item)}
                >
                  <Text style={styles.menuText}>{item}</Text>
                </TouchableOpacity>
              ))}
            </View>
          ))}
        </ScrollView>

        {/* Right Side Chat Screen */}
        <View style={styles.chatArea}>
          <View style={styles.chatHeader}>
            <Text style={styles.chatHeaderTitle}>Active Mode: {currentMenu}</Text>
          </View>
          
          {/* Chat Messages Placeholder */}
          <ScrollView style={styles.messageList}>
            <View style={styles.aiMessage}>
              <Text style={styles.messageText}>Hello! Main aapki kaise madad kar sakta hoon? Aapne abhi '{currentMenu}' option select kiya hai.</Text>
            </View>
          </ScrollView>

          {/* Input Bar */}
          <View style={styles.inputContainer}>
            <TextInput style={styles.input} placeholder="Type your message here..." />
            <TouchableOpacity style={styles.sendButton}>
              <Text style={styles.sendButtonText}>Send</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1e1e2e' },
  header: { height: 60, backgroundColor: '#11111b', justifyContent: 'center', paddingHorizontal: 15, borderBottomWidth: 1, borderColor: '#313244' },
  headerText: { color: '#cdd6f4', fontSize: 18, fontWeight: 'bold' },
  mainBody: { flex: 1, flexDirection: 'row' },
  sidebar: { width: '35%', backgroundColor: '#181825', padding: 10, borderRightWidth: 1, borderColor: '#313244' },
  sectionContainer: { marginBottom: 15 },
  sectionTitle: { color: '#a6adc8', fontSize: 11, fontWeight: 'bold', marginBottom: 5, uppercase: true },
  menuButton: { paddingVertical: 8, paddingHorizontal: 5, borderRadius: 5, marginBottom: 2 },
  activeMenu: { backgroundColor: '#45475a' },
  menuText: { color: '#cdd6f4', fontSize: 13 },
  chatArea: { width: '65%', backgroundColor: '#1e1e2e', justifyContent: 'space-between' },
  chatHeader: { padding: 10, backgroundColor: '#181825', borderBottomWidth: 1, borderColor: '#313244' },
  chatHeaderTitle: { color: '#fab387', fontWeight: 'bold', fontSize: 14 },
  messageList: { flex: 1, padding: 10 },
  aiMessage: { backgroundColor: '#313244', padding: 12, borderRadius: 10, maxWidth: '85%', marginBottom: 10 },
  inputContainer: { flexDirection: 'row', padding: 10, backgroundColor: '#181825', alignItems: 'center' },
  input: { flex: 1, backgroundColor: '#313244', color: '#cdd6f4', borderRadius: 20, paddingHorizontal: 15, height: 40 },
  sendButton: { marginLeft: 10, backgroundColor: '#89b4fa', paddingHorizontal: 15, paddingVertical: 10, borderRadius: 20 },
  sendButtonText: { color: '#11111b', fontWeight: 'bold' }
});
