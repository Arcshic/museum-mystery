import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [puzzle, setPuzzle] = useState(null);
  const [answer, setAnswer] = useState("");
  const [message, setMessage] = useState("");
  const [revealedHints, setRevealedHints] = useState(1);
  const [score, setScore] = useState(0);
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [submitted, setSubmitted] = useState(false);

  function loadPuzzle() {
    setPuzzle(null);
    setAnswer("");
    setMessage("");
    setRevealedHints(1);
    setSubmitted(false);

    fetch("http://127.0.0.1:5000/api/puzzle")
      .then((response) => response.json())
      .then((data) => setPuzzle(data))
      .catch((error) => {
        console.error("Failed to load puzzle:", error);
        setMessage("Could not load puzzle from backend.");
      });
  }

  useEffect(() => {
    loadPuzzle();
  }, []);

  function revealHint() {
    if (!puzzle) return;

    setRevealedHints((current) =>
      Math.min(current + 1, puzzle.hints.length)
    );
  }

  function submitAnswer() {
    if (!puzzle || submitted) return;

    const userAnswer = answer.trim().toLowerCase();
    const correctAnswer = puzzle.answer.trim().toLowerCase();

    setQuestionsAnswered((current) => current + 1);
    setSubmitted(true);

    if (userAnswer === correctAnswer) {
      setScore((current) => current + 1);
      setMessage("Correct!");
    } else {
      setMessage(`Not quite. The correct answer is: ${puzzle.answer}`);
    }
  }

  if (!puzzle) {
    return <main className="container">Loading puzzle...</main>;
  }

  return (
    <main className="container">
      <section className="card">
        <header className="top-bar">
          <div>
            <p className="label">AI-powered museum quiz</p>
            <h1>{puzzle.title}</h1>
          </div>

          <div className="score-box">
            Score: {score} / {questionsAnswered}
          </div>
        </header>

        {puzzle.image_url && (
          <img
            className="artwork"
            src={puzzle.image_url}
            alt="Museum artwork"
          />
        )}

        <section className="hint-box">
          <h2>Hints</h2>

          {puzzle.hints.slice(0, revealedHints).map((hint, index) => (
            <p key={index}>
              <strong>Hint {index + 1}:</strong> {hint}
            </p>
          ))}

          {revealedHints < puzzle.hints.length && !submitted && (
            <button className="secondary-button" onClick={revealHint}>
              Reveal Another Hint
            </button>
          )}
        </section>

        <section className="answer-box">
          <label htmlFor="answer">Your answer</label>

          <input
            id="answer"
            value={answer}
            onChange={(event) => setAnswer(event.target.value)}
            placeholder="Type your guess"
            disabled={submitted}
          />

          <button onClick={submitAnswer} disabled={submitted}>
            Submit Answer
          </button>
        </section>

        {message && (
          <section className="result-box">
            <h2>{message}</h2>
            <p>{puzzle.explanation}</p>
            <p>
              <strong>Source:</strong>{" "}
              <a href={puzzle.source} target="_blank" rel="noreferrer">
                View museum record
              </a>
            </p>
          </section>
        )}

        <button className="next-button" onClick={loadPuzzle}>
          Next Mystery
        </button>
      </section>
    </main>
  );
}

export default App;