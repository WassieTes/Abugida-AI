import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 60000,
});

// ---------------- UPLOAD PDF ----------------

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

// ---------------- CHAT ----------------

export const askQuestion = async (question, chatId, documentId) => {
  try {
    const res = await API.post("/chat", {
      question,
      chat_id: chatId,
      document_id: documentId,
    });

    return res.data;
  } catch (err) {
    console.log("CHAT ERROR:", err.response?.data || err.message);

    return {
      success: false,
      answer: "Network error",
      error: err.response?.data || err.message,
    };
  }
};
