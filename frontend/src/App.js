import React, { useState, useEffect } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";
import { registerKoalaLanguage } from "./koalaLang";

function App() {
  const [code, setCode] = useState(
    `x = 5;
 give(x);
 z = x + 7;
 give(z);
 give("Hello from Koala!");`
  );
  const [output, setOutput] = useState("");
  const [theme, setTheme] = useState("vs-dark");

  useEffect(() => {
    registerKoalaLanguage();
  }, []);

  const runCode = async () => {
    setOutput("⏳ Running...");
    try {
      const response = await axios.post("http://127.0.0.1:8000/run", { code });
      setOutput(response.data.output || "No output");
    } catch (error) {
      console.error(error);
      setOutput("❌ Error running code");
    }
  };

  const clearOutput = () => setOutput("");

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", background: "#7393B3", color: "#e0e0e0", fontFamily: "Fira Code, monospace" }}>
      {/* Header */}
      <div style={{
        padding: "12px 20px",
        background: "#7393B3",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        boxShadow: "0 2px 6px rgba(0,0,0,0.6)"
      }}>
        <h2 style={{ margin: 0, fontSize: "18px", fontWeight: "bold", letterSpacing: "1px" }}>KoalaCode IDE 🐨</h2>
        <div>
          <button
            onClick={runCode}
            style={{
              marginRight: "10px",
              padding: "8px 18px",
              background: "#4caf50",
              border: "none",
              color: "#fff",
              borderRadius: "8px",
              cursor: "pointer",
              fontWeight: "bold"
            }}
          >
            ▶ Run
          </button>
          <button
            onClick={clearOutput}
            style={{
              marginRight: "10px",
              padding: "8px 18px",
              background: "#f44336",
              border: "none",
              color: "#fff",
              borderRadius: "8px",
              cursor: "pointer",
              fontWeight: "bold"
            }}
          >
            ✖ Clear
          </button>
          <button
            onClick={() => setTheme(theme === "vs-dark" ? "vs-light" : "vs-dark")}
            style={{
              padding: "8px 18px",
              background: "#2196f3",
              border: "none",
              color: "#fff",
              borderRadius: "8px",
              cursor: "pointer",
              fontWeight: "bold"
            }}
          >
            🎨 Theme
          </button>
        </div>
      </div>

      {/* Body */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Editor */}
        <div style={{ flex: "65%", borderRight: "2px solid #333" }}>
          <Editor
            height="100%"
            defaultLanguage="koala"
            value={code}
            onChange={(value) => setCode(value || "")}
            theme={theme}
            options={{
              fontSize: 15,
              minimap: { enabled: false },
              wordWrap: "on",
              fontFamily: "Fira Code, monospace",
              lineNumbers: "on",
              scrollBeyondLastLine: false
            }}
          />
        </div>

        {/* Output */}
        <div style={{ flex: "35%", background: "#000000", padding: "15px", overflowY: "auto", display: "flex", flexDirection: "column" }}>
          <h3 style={{ marginTop: 0, marginBottom: "10px", fontSize: "16px", borderBottom: "1px solid #333", paddingBottom: "5px" }}>🖥️ Output</h3>
          <pre style={{
            flex: 1,
            whiteSpace: "pre-wrap",
            wordWrap: "break-word",
            fontSize: "14px",
            color: output.startsWith("❌") ? "#ff5252" : "#4caf50"
          }}>
            {output}
          </pre>
        </div>
      </div>
    </div>
  );
}

export default App;