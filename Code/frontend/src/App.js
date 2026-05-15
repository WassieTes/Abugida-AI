import { useState } from "react";
import { uploadPDF, askQuestion } from "./api";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);

  const send = async () => {
    const res = await askQuestion(question);

    setChat((prev) => [
      ...prev,
      { role: "user", text: question },
      { role: "bot", text: res.data.answer },
    ]);

    setQuestion("");
  };

  const upload = async () => {
    if (!file) return;

    const res = await uploadPDF(file);
    alert(`Processed ${res.data.chunks} chunks`);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Offline AI Tutor</h2>

      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={upload}>Upload PDF</button>

      <hr />

      {chat.map((c, i) => (
        <p key={i}>
          <b>{c.role}:</b> {c.text}
        </p>
      ))}

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
