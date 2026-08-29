import { useState } from "react";
import axios from "axios";
import "./App.css";
import ReactMarkdown from "react-markdown";
import VideoPlayer from "./VideoPlayer";
function App() {
    const [videoId, setVideoId] = useState("");
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!videoId || !question) {
            setError("Please enter both a video ID and a question.");
            return;
        }

        setLoading(true);
        setError("");
        setAnswer("");

        try {
            const response = await axios.post("http://127.0.0.1:8000/ask", {
                video_id: videoId,
                question: question,
            });

            setAnswer(response.data.answer);
        } catch (err) {
            console.error(err);
            setError("Something went wrong. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app">
            <header className="header">
                <h1>YouTube Q&A</h1>
                <p>Ask questions about any YouTube video.</p>
            </header>

            <main className="container">
                
                <div className="main">
                    <form onSubmit={handleSubmit} className="question-form">
                        <label htmlFor="videoId">YouTube Video ID</label>

                        <input
                            id="videoId"
                            type="text"
                            placeholder="e.g. dQw4w9WgXcQ"
                            value={videoId}
                            onChange={(e) => setVideoId(e.target.value)}
                        />

                        <label htmlFor="question">Your Question</label>

                        <textarea
                            id="question"
                            placeholder="What is this video about?"
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            rows="5"
                        />

                        <button type="submit" disabled={loading}>
                            {loading ? "Thinking..." : "Ask Question"}
                        </button>
                    </form>

                    {error && <div className="error">{error}</div>}

                    {answer && (
                        <section className="answer-section">
                            <h2>Answer</h2>
                            <p>
                                <ReactMarkdown>{answer}</ReactMarkdown>
                            </p>
                        </section>
                    )}
                </div>
                {videoId && <VideoPlayer videoId={videoId} />}        
            </main>
        </div>
    );
}

export default App;
