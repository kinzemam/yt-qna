import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
axios.interceptors.request.use((config) => {
  config.url = config.url.replace("http://127.0.0.1:8000", API_URL);
  return config;
});
createRoot(document.getElementById('root')).render(
    <App />
)
