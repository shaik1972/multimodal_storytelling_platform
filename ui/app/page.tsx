"use client";
import { useState } from "react";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [format, setFormat] = useState("text");
  const [output, setOutput] = useState<any>(null);

  const generate = async () => {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, format }),
    });
    const data = await res.json();
    setOutput(data);
  };

  return (
    <main style={{ padding: "2rem" }}>
      <h1>🎬 Multimodal Storytelling</h1>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your story or audio prompt..."
        rows={4}
        style={{ width: "100%", marginBottom: "1rem" }}
      />
      <select value={format} onChange={(e) => setFormat(e.target.value)}>
        <option value="text">Text</option>
        <option value="audio">Audio</option>
        <option value="image">Image</option>
        <option value="video">Video</option>
      </select>

      <button onClick={generate} style={{ marginLeft: "1rem" }}>
        Generate
      </button>

      {format === "text" && output?.story && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Generated Story</h2>
          <p>{output.story}</p>
        </div>
      )}

      {format === "audio" && output?.audioUrl && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Generated Audio</h2>
          <audio controls src={output.audioUrl}></audio>
        </div>
      )}

      {format === "image" && output?.imageUrl && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Generated Image</h2>
          <img src={output.imageUrl} alt="Generated" style={{ maxWidth: "100%" }} />
        </div>
      )}

      {format === "video" && output?.videoUrl && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Generated Video</h2>
          <video controls src={output.videoUrl} style={{ maxWidth: "100%" }} />
        </div>
      )}

    </main>
  );
}
