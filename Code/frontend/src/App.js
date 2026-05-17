import { useState, useRef, useEffect } from "react";
import { uploadPDF, askQuestion } from "./api";

import { Plus, Trash2, Send, Brain, Upload, FileText, X } from "lucide-react";

/* -------------------- helper -------------------- */

const generateId = () =>
  Date.now().toString(36) + Math.random().toString(36).substr(2, 5);

function App() {
  const [question, setQuestion] = useState("");

  const [chat, setChat] = useState([]);

  const [loading, setLoading] = useState(false);

  const [typing, setTyping] = useState(false);

  const [uploadedFiles, setUploadedFiles] = useState([]);

  // NEW
  const [chatId, setChatId] = useState(null);

  const [documentId, setDocumentId] = useState(null);

  /* -------------------- history -------------------- */

  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem("chat_history");

    return saved ? JSON.parse(saved) : [];
  });

  const [activeChatId, setActiveChatId] = useState(null);

  const fileInputRef = useRef(null);

  const chatEndRef = useRef(null);

  const openFilePicker = () => fileInputRef.current.click();

  /* -------------------- persist -------------------- */

  useEffect(() => {
    localStorage.setItem("chat_history", JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [chat, typing]);

  /* -------------------- upload PDF -------------------- */

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];

    // IMPORTANT FIX
    e.target.value = null;

    if (!file) return;

    setLoading(true);

    try {
      const res = await uploadPDF(file);

      if (res.success) {
        setUploadedFiles([file]);

        setChatId(res.chat_id);

        setDocumentId(res.document_id);

        setChat([
          {
            role: "bot",

            text: res.reused
              ? `Existing document reused.\n\nYou can now ask questions about "${file.name}".`
              : `Document "${file.name}" uploaded successfully.\n\nYou can now ask questions about this document.`,
          },
        ]);
      } else {
        setChat([
          {
            role: "bot",
            text: res.message || "Failed to upload document.",
          },
        ]);
      }
    } catch (err) {
      console.log(err);

      setChat([
        {
          role: "bot",
          text: "Upload failed.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };
  /* -------------------- STREAMING -------------------- */

  const streamAnswer = (fullText) => {
    return new Promise((resolve) => {
      let i = 0;

      setChat((prev) => [
        ...prev,
        {
          role: "bot",
          text: "",
        },
      ]);

      const interval = setInterval(() => {
        i++;

        setChat((prev) => {
          const copy = [...prev];

          copy[copy.length - 1] = {
            role: "bot",
            text: fullText.slice(0, i),
          };

          return copy;
        });

        if (i >= fullText.length) {
          clearInterval(interval);

          resolve();
        }
      }, 12);
    });
  };

  /* -------------------- SEND MESSAGE -------------------- */

  const send = async () => {
    if (!question.trim()) return;

    if (loading || typing) return;

    if (!documentId) {
      setChat((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Please upload a document first.",
        },
      ]);

      return;
    }

    const userQ = question;

    setQuestion("");

    setTyping(true);

    // IMPORTANT:
    // single atomic update
    setChat((prev) => [
      ...prev,

      {
        role: "user",
        text: userQ,
      },

      {
        role: "bot",
        text: "",
      },
    ]);

    try {
      await askQuestion(
        userQ,
        chatId,
        documentId,

        // STREAM CALLBACK
        (chunk) => {
          setChat((prev) => {
            const updated = [...prev];

            // always target LAST BOT MESSAGE
            const lastIndex = updated.length - 1;

            if (updated[lastIndex] && updated[lastIndex].role === "bot") {
              updated[lastIndex] = {
                ...updated[lastIndex],
                text: updated[lastIndex].text + chunk,
              };
            }

            return updated;
          });
        },
      );
    } catch (err) {
      console.log(err);

      setChat((prev) => {
        const updated = [...prev];

        const lastIndex = updated.length - 1;

        if (updated[lastIndex] && updated[lastIndex].role === "bot") {
          updated[lastIndex] = {
            ...updated[lastIndex],
            text: "Streaming error",
          };
        }

        return updated;
      });
    } finally {
      setTyping(false);
    }
  };

  /* -------------------- NEW CHAT -------------------- */

  const newChat = () => {
    if (chat.length > 0) {
      const firstUser = chat.find((m) => m.role === "user");

      const session = {
        id: activeChatId || generateId(),

        title: firstUser?.text || uploadedFiles?.[0]?.name || "New Chat",

        chat,

        files: uploadedFiles,

        chatId,

        documentId,
      };

      setHistory((prev) => [session, ...prev]);
    }

    setChat([]);

    setUploadedFiles([]);

    setChatId(null);

    setDocumentId(null);

    setActiveChatId(generateId());
  };

  /* -------------------- OPEN HISTORY -------------------- */

  const openHistory = (item) => {
    setChat(item.chat || []);

    setUploadedFiles(item.files || []);

    setActiveChatId(item.id);

    setChatId(item.chatId || null);

    setDocumentId(item.documentId || null);
  };

  /* -------------------- REMOVE FILE -------------------- */

  const removeFile = (index) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));

    // reset document linkage
    setDocumentId(null);

    setChatId(null);

    setChat([]);
  };

  return (
    <div className="app">
      {/* SIDEBAR */}

      <div className="sidebar">
        <div>
          <div className="logo">
            <div className="logo-icon">✦</div>

            <div>
              <h2>Abugida AI</h2>

              <p>Offline Assistant</p>
            </div>
          </div>

          <button className="new-chat" onClick={newChat}>
            <Plus size={18} />
            New Chat
          </button>

          <h4>CHAT HISTORY</h4>

          <div className="history">
            {history.length === 0 ? (
              <p className="empty">No chats yet</p>
            ) : (
              history.map((h) => (
                <div
                  key={h.id}
                  className="history-card"
                  onClick={() => openHistory(h)}
                  style={{
                    cursor: "pointer",
                  }}
                >
                  {h.title}
                </div>
              ))
            )}
          </div>
        </div>

        <button
          className="clear-btn"
          onClick={() => {
            setHistory([]);

            localStorage.removeItem("chat_history");
          }}
        >
          <Trash2 size={18} />
          Clear History
        </button>
      </div>

      {/* MAIN */}

      <div className="main">
        <div className="chat">
          <div className="hero">
            <Brain size={42} color="white" />

            <h1>How can I help you today?</h1>

            <p>Ask anything and process documents locally.</p>

            {uploadedFiles.length > 0 && (
              <div className="file-box">
                {uploadedFiles.map((f, i) => (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      gap: "10px",
                      alignItems: "center",
                    }}
                  >
                    <FileText />

                    <div>
                      <b>{f.name}</b>

                      <p>{(f.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>

                    <X
                      size={18}
                      style={{
                        cursor: "pointer",
                      }}
                      onClick={() => removeFile(i)}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="messages">
            {chat.map((c, i) => (
              <div key={i} className={`msg ${c.role}`}>
                <div
                  style={{
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}
                >
                  {c.text}
                </div>
              </div>
            ))}

            {typing && <div className="typing">AI is thinking...</div>}

            <div ref={chatEndRef} />
          </div>
        </div>

        {/* INPUT */}

        <div className="input">
          <input
            ref={fileInputRef}
            type="file"
            hidden
            onChange={handleFileUpload}
          />

          <button className="plus" onClick={openFilePicker}>
            {loading ? <Upload size={18} /> : <Plus size={20} />}
          </button>

          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask anything..."
          />

          <button className="send" onClick={send}>
            <Send size={18} />
            Send
          </button>
        </div>
      </div>

      {/* STYLES */}

      <style>{`
        html, body, #root {
          height: 100%;
          margin: 0;
          overflow: hidden;
        }

        * { box-sizing: border-box; }

        .app {
          display: flex;
          height: 100vh;
          width: 100vw;
          overflow: hidden;
          font-family: Inter, sans-serif;
          background: #f4f7fb;
        }

        .sidebar {
          width: 260px;
          height: 100vh;
          background: white;
          border-right: 1px solid #e5e7eb;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          padding: 20px;
        }

        .logo {
          display: flex;
          gap: 12px;
        }

        .logo-icon {
          width: 50px;
          height: 50px;
          border-radius: 14px;
          background: linear-gradient(135deg,#61d1cf,#6be671,#e4e25f);
          display:flex;
          align-items:center;
          justify-content:center;
          color:white;
          font-weight:bold;
        }

        .new-chat {
          width: 100%;
          margin: 20px 0;
          padding: 12px;
          border: none;
          border-radius: 14px;
          background: linear-gradient(135deg,#6cff4f,#45f6ff);
          color: white;
          font-weight: 700;
        }

        .history {
          overflow-y: auto;
          max-height: 55vh;
        }

        .history-card {
          padding: 10px;
          margin-bottom: 8px;
          border: 1px solid #eee;
          border-radius: 10px;
        }

        .clear-btn {
          width: 100%;
          padding: 12px;
          border-radius: 14px;
          border: none;
          background: linear-gradient(135deg,#ff6b6b,#ff8e53);
          color: white;
          font-weight: 700;
        }

        .main {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .chat {
          flex: 1;
          overflow-y: auto;
          padding: 30px;
        }

        .hero {
          text-align: center;
        }

        .messages {
          max-width: 800px;
          margin: 0 auto;
          margin-top: 20px;
        }

        .msg {
          padding: 14px 18px;
          border-radius: 16px;
          margin-bottom: 10px;
          max-width: 70%;
        }

        .user {
          margin-left: auto;
          background: linear-gradient(135deg,#6cff4f,#45f6ff);
          color: white;
        }

        .bot {
          background: white;
        }

        .input {
          display: flex;
          gap: 12px;
          padding: 14px;
          border-top: 1px solid #e5e7eb;
          background: white;
        }

        .input input {
          flex: 1;
          padding: 14px;
          border-radius: 30px;
          border: none;
          background: #f1f5f9;
          outline: none;
        }

        .plus {
          width: 44px;
          height: 44px;
          border-radius: 50%;
          border: none;
          background: linear-gradient(135deg,#6cff4f,#45f6ff);
          color: white;
        }

        .send {
          padding: 12px 18px;
          border-radius: 20px;
          border: none;
          background: linear-gradient(135deg,#6cff4f,#45f6ff);
          color: white;
          font-weight: 700;
        }
      `}</style>
    </div>
  );
}

export default App;
