import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";
import ReactMarkdown from "react-markdown";

function App() {
  const [userInput, setUserInput] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false); // 🆕 spinner control
  const chatEndRef = useRef(null);

  const handleSend = async () => {
    if (!userInput.trim()) return;

    const newChat = [...chat, { type: "user", text: userInput }];
    setChat(newChat);
    setUserInput("");
    setLoading(true); // show spinner

    try {
      const response = await axios.post("http://127.0.0.1:8002/chat", {
        query: userInput,
      });
      setChat([...newChat, { type: "bot", text: response.data.reply }]);
    } catch (error) {
      setChat([
        ...newChat,
        { type: "bot", text: "⚠️ Error: Could not connect to chatbot." },
      ]);
    } finally {
      setLoading(false); // hide spinner
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleSend();
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, loading]);

  return (
    <div className="app">
      <div className="chat-container">
        <header className="chat-header">
          <h1>🌿 AgriChat Buddy</h1>
          <p>Your AI Partner for Sustainable Farming</p>
        </header>

        <div className="chat-box">
          {chat.length === 0 ? (
            <div className="welcome">
              <h3>👋 Welcome to AgriChat Buddy</h3>
              <p>
                Ask me anything about organic farming, soil health, irrigation,
                or sustainable agriculture!
              </p>
            </div>
          ) : (
            chat.map((msg, i) => (
              <div
                key={i}
                className={`message ${msg.type === "user" ? "user" : "bot"}`}
              >
                
<div className="message-text">
  <ReactMarkdown>{msg.text}</ReactMarkdown>
</div>
              </div>
            ))
          )}

          {/* 🆕 Spinner while waiting for response */}
          {loading && (
            <div className="message bot">
              <div className="loading-spinner"></div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        <div className="input-area">
          <input
            type="text"
            placeholder="Type your question here..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyDown={handleKeyPress}
          />
          <button onClick={handleSend}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
