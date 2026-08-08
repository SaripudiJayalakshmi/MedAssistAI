// App.jsx
// This is our root React component — the starting point of our UI.

import { useState, useEffect } from "react"; // React hooks for state and side-effects

function App() {
  // "backendMessage" holds whatever text we get back from the FastAPI server
  // "setBackendMessage" is the function we call to update it
  const [backendMessage, setBackendMessage] = useState("Loading...");

  // useEffect runs code when the component first loads (empty [] = run once)
  useEffect(() => {
    fetch("http://127.0.0.1:8000/")       // calls our FastAPI root endpoint
      .then((res) => res.json())          // parses the JSON response
      .then((data) => setBackendMessage(data.message)) // saves it into state
      .catch(() => setBackendMessage("Could not reach backend ❌"));
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="bg-white shadow-lg rounded-2xl p-8 text-center">
        <h1 className="text-3xl font-bold text-blue-600 mb-2">MedAssist AI</h1>
        <p className="text-slate-600">Backend says: {backendMessage}</p>
      </div>
    </div>
  );
}

export default App;