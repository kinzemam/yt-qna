import { useEffect, useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import Header from "../components/header";

export default function Home(props) {
    const [videoId, setVideoId] = useState("");
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [chatId, setChatId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [chats, setChats] = useState([])
    const [messages, setMessages] = useState([])
    async function askQuestion(event) {
        event.preventDefault();
        setLoading(true);

        setAnswer("");

        try {
            const result = await axios.post(
                "http://127.0.0.1:8000/ask",
                { video_id: videoId, question: question, chat_id: chatId },
                {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("token")}`,
                    },
                }
            );

            setMessages((prev) => {
                return [
                    ...prev,
                    { role: 'user', content: question },
                    { role: 'ai', content: result.data.answer }
                ]
            })
            setQuestion("")
            setAnswer("");
            setChatId(result.data.chat_id);
            loadChats();
        } catch (err) {
            if (err.response && err.response.status === 401) {
                setAnswer("Session expired. Please log out and log in again.");
            } else {
                setAnswer("Something went wrong. Check that the server is running.");
            }
        }
        setLoading(false);
    }

    async function loadChats(e) {
        const token = localStorage.getItem('token')
        try {
            const response = await axios.get("http://127.0.0.1:8000/chats", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            setChats(response.data)
        } catch (err) {
            console.error(err)
        }

    }
    async function openChat(chat) {
        try {
            const token = localStorage.getItem('token')
            const response = await axios.get(`http://127.0.0.1:8000/chats/${chat.id}/messages`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            setMessages(response.data)
            setChatId(chat.id)
            setVideoId(chat.video_id)
            setAnswer("")
        } catch (err) {
            console.error(err)
        }
    }

    function newChat() {
        setChatId(null)
        setMessages([])
        setAnswer('')
        setVideoId('')
        setQuestion('')
    }

    useEffect(() => {
        loadChats()
    }, [])
    console.log("messages:", messages)
    return (
        <div>
            <Header />
            <div className="container text-center auth px-3 py-3">

                <form onSubmit={askQuestion} className="my-4">
                    <label htmlFor="video-id" className="form-label px-1">Video ID</label>
                    <input
                        name="video-id"
                        id="video-id"
                        className="form-control mb-2"
                        placeholder="YouTube video ID"
                        value={videoId}
                        onChange={(e) => {
                            setVideoId(e.target.value);
                            setChatId(null);
                            setMessages([])
                        }}
                    />
                    <label htmlFor="question" className="form-label px-1">Question</label>
                    <textarea
                        name="question"
                        rows={5}
                        className="form-control mb-2"
                        placeholder="Ask a question about the video"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                    />
                    <input
                        type="submit"
                        className="btn btn-dark"
                        value={loading ? "Thinking..." : "Ask"}
                        disabled={loading}
                    />
                </form>
                <div className="text-start my-4">
                    {messages.map((m,i) =>
                        m.role === "user" ? (
                            <p key={i}><strong>You:</strong> {m.content}</p>
                        ) : (
                            <div key={i}><b>Assistant:</b> <ReactMarkdown>{m.content}</ReactMarkdown></div>
                        )
                    )}
                </div>
                {answer && (
                    <div className="text-start my-4">
                        <ReactMarkdown>{answer}</ReactMarkdown>
                    </div>
                )}
                <div className="text-start my-4">
                    <h5>Your chats</h5>
                    {chats.length === 0 && <p>No chats yet.</p>}
                    <button type="button" className="btn btn-outline-dark btn-sm mb-2" onClick={newChat}>
                        New chat
                    </button>
                    <ul className="list-unstyled">
                        {chats.map((c) => (
                            <li key={c.id}>
                                <button className="btn btn-link p-0" onClick={() => openChat(c)}>
                                    Chat {c.id} · Video {c.video_id}
                                </button>
                                {c.id === chatId && " ← open"}
                            </li>
                        ))}
                    </ul>
                </div>
                <form onSubmit={props.handleSubmit}>
                    <input type="submit" className="btn btn-outline-dark" value="Logout" />
                </form>
            </div>
        </div>
    );
}