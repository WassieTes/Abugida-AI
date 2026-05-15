import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 60000, // IMPORTANT for PDF + embeddings
});

// UPLOAD
export const uploadPDF = async (file) => {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const res = await API.post("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
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

// CHAT
export const askQuestion = async (question) => {
  try {
    const res = await API.post("/chat", { question });
    return res.data;
  } catch (err) {
    return {
      success: false,
      answer: "Network error",
      error: err.response?.data || err.message,
    };
  }
};
