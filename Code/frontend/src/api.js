import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 60000,
});

// ---------------- UPLOAD PDF ----------------

export const uploadPDF = async (file, chatId) => {
  try {
    const formData = new FormData();

    formData.append("file", file);

    formData.append("chat_id", chatId);

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
      chunks: 0,
      error: err.response?.data || err.message,
    };
  }
};

// ---------------- CHAT ----------------

export const askQuestion = async (question, chatId = null) => {
  try {
    const res = await API.post("/chat", {
      question,
      chat_id: chatId,
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
