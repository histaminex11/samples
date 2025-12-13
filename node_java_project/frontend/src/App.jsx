import { useEffect, useState } from "react";

export default function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("/api/greeting")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("Could not reach backend"));
  }, []);

  return (
    <main style={{ fontFamily: "Arial, sans-serif", padding: "2rem" }}>
      <h1>Cursor Full-Stack Sample</h1>
      <p>{message}</p>
      <p style={{ color: "#555" }}>
        This React frontend calls the Spring Boot backend via /api/greeting.
      </p>
    </main>
  );
}

