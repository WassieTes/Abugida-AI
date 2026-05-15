import { useState } from "react";
import { uploadPDF, askQuestion } from "./api";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  // ======================
  // UPLOAD PDF
  // ======================
  const upload = async () => {
    if (!file) {
      alert("Please select a PDF first");
      return;
    }

    setLoading(true);

    try {
      const res = await uploadPDF(file);

      if (!res || res.success === false) {
        alert(res?.error || "Upload failed");
        return;
      }

      alert(`Processed ${res.chunks ?? 0} chunks`);
    } catch (err) {
      console.log(err);
      alert("Upload error");
    } finally {
      setLoading(false);
    }
  };

  // ======================
  // ASK QUESTION
  // ======================
  const send = async () => {
    if (!question.trim()) return;

    const userQ = question;

    setChat((prev) => [...prev, { role: "user", text: userQ }]);

    setQuestion("");

    try {
      const res = await askQuestion(userQ);

      setChat((prev) => [
        ...prev,
        {
          role: "bot",
          text: res?.answer ?? "No response from server",
        },
      ]);
    } catch (err) {
      setChat((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Error getting response",
        },
      ]);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Offline AI Tutor</h2>

      {/* UPLOAD */}
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={upload} disabled={loading}>
        {loading ? "Processing..." : "Upload PDF"}
      </button>

      <hr />

      {/* CHAT */}
      <div style={{ marginBottom: 20 }}>
        {chat.map((c, i) => (
          <p key={i}>
            <b>{c.role}:</b> {c.text}
          </p>
        ))}
      </div>

      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask question..."
      />
      <button onClick={send}>Send</button>
    </div>
  );
}

export default App;
