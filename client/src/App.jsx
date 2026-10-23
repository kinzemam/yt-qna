import { useState } from "react";
import axios from "axios";
import "./App.css";
import ReactMarkdown from "react-markdown";
import VideoPlayer from "./VideoPlayer";
import Header from "./components/header";
import Login from "./pages/Login";
import {
    BrowserRouter,
    Routes,
    Route,
    Navigate,
    redirect,
} from "react-router-dom";
import Home from "./pages/Home";
import Signup from "./pages/Signup";
export default function App() {
    const [user, setUser] = useState(() => {
        const savedUser = localStorage.getItem("user");
        return savedUser ? JSON.parse(savedUser) : null;
    });

    const [error, setError] = useState(null);

    const [passwordCheck, setPasswordCheck] = useState(true);

    async function loginSub(event) {
        event.preventDefault();
        setPasswordCheck(true);
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());
        try {
            const result = await axios.post("http://127.0.0.1:8000/login", data);
            if (result.status == 200) {
                const token = result.data["access_token"];
                const response = await axios.get("http://127.0.0.1:8000/me", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    }
                });
                console.log(response);
                if (response.status == 200) {
                    localStorage.setItem("token", token);
                    localStorage.setItem("user", JSON.stringify(response.data));
                    setUser(response.data);
                    setError(null);
                }
            }
        } catch (err) {
            console.error("Authentication failed", err);
            if (err.response && err.response.status === 401) {
                setPasswordCheck(false);
                console.log(err.response.data)
                setError(err.response.data.detail)
            }
        }
    }

    function logoutHandle(event) {
        event.preventDefault();
        localStorage.removeItem("user");
        localStorage.removeItem("token");
        setUser(null);
    }

    async function signupSub(event) {
        event.preventDefault()
        const formData = new FormData(event.target)
        const data = Object.fromEntries(formData.entries())
        try {
            const result = await axios.post("http://127.0.0.1:8000/signup", data);
            console.log(result)
            if (result.status == 200 || result.status == 201) {
                
                const loginResult = await axios.post("http://127.0.0.1:8000/login", {
                    email: data.email,
                    password: data.password
                })
                setError(null)
                console.log("Login success:", loginResult);
                if (loginResult.status == 200) {
                    const token = loginResult.data["access_token"]

                    const response = await axios.get("http://127.0.0.1:8000/me", {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    })
                    if (response.status == 200) {
                        localStorage.setItem("token", token)
                        localStorage.setItem("user", JSON.stringify(response.data))
                        setUser(response.data)
                    }
                }
            }
        } catch (err) {
            console.log(err.response.data)
            setError(err.response.data.detail)
        }
    }

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/signup" element={user ? <Navigate to={'/me'} /> : <Signup handleSubmit={signupSub} error={error} />} />
                <Route
                    path="/login"
                    element={
                        user ? (
                            <Navigate to="/me" />
                        ) : (
                                <Login handleSubmit={loginSub} error={error} />
                        )
                    }
                />
                <Route path="/" element={<Navigate to="/login" replace />} />
                <Route
                    path="/me"
                    element={
                        user ? (
                            <Home handleSubmit={logoutHandle} />
                        ) : (
                            <Navigate to="/login" replace />
                        )
                    }
                />
            </Routes>
        </BrowserRouter>
    );
}
