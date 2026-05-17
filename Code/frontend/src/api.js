import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 60000,
});

// ================= UPLOAD =================

export const uploadPDF = async (file) => {
  try {
    const formData = new FormData();

    formData.append("file", file);

    const res = await API.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return res.data;
  } catch (err) {
    console.log("UPLOAD ERROR:", err.response?.data || err.message);

    return {
      success: false,
      error: err.response?.data || err.message,
    };
  }
};

// ================= STREAM CHAT =================

export const askQuestion = async (
  question,
  chatId = null,
  documentId = null,
  onChunk,
) => {
  const response = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      question,
      chat_id: chatId,
      document_id: documentId,
    }),
  });

  if (!response.ok) {
    throw new Error("Chat request failed");
  }

  if (!response.body) {
    throw new Error("No response stream");
  }

  const reader = response.body.getReader();

  const decoder = new TextDecoder("utf-8");

  let fullText = "";

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    const chunk = decoder.decode(value);

    fullText += chunk;

    if (onChunk) {
      onChunk(chunk);
    }
  }

  return fullText;
};
