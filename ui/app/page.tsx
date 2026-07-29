"use client";
import { useState } from "react";

type Format = "text" | "audio" | "image" | "video";
type VoiceOption = "female" | "male" | "female2" | "male2";
type SpeedOption = "-20%" | "+0%" | "+20%" | "+40%";

interface Output {
  story?: string;
  audioUrl?: string;
  imageUrl?: string;
  videoUrl?: string;
  voice?: string;
}

const VOICE_LABELS: Record<VoiceOption, string> = {
  female:  "🔵 Female — Jenny (US)",
  male:    "🟢 Male — Guy (US)",
  female2: "🔵 Female — Sonia (British)",
  male2:   "🟢 Male — Ryan (British)",
};

const SPEED_LABELS: Record<SpeedOption, string> = {
  "-20%": "Slow",
  "+0%":  "Normal",
  "+20%": "Fast",
  "+40%": "Very fast",
};

interface VideoEdits {
  trimStart: string;
  trimEnd: string;
  overlayText: string;
  overlayPosition: "top" | "center" | "bottom";
  transition: "fade" | "fade-in" | "none";
}

const DEFAULT_VIDEO_EDITS: VideoEdits = {
  trimStart: "0",
  trimEnd: "",
  overlayText: "",
  overlayPosition: "bottom",
  transition: "none",
};

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [format, setFormat] = useState<Format>("text");
  const [output, setOutput] = useState<Output | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // audio options
  const [voice, setVoice] = useState<VoiceOption>("female");
  const [speed, setSpeed] = useState<SpeedOption>("+0%");

  // video edit state
  const [videoEdits, setVideoEdits] = useState<VideoEdits>(DEFAULT_VIDEO_EDITS);
  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  // ── Generate ───────────────────────────────────────────────────────────────
  const generate = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);
    setOutput(null);
    setVideoEdits(DEFAULT_VIDEO_EDITS);

    // Only send voice/speed for formats that use audio narration
    const audioOptions =
      format === "audio" || format === "video" ? { voice, speed } : {};

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, format, ...audioOptions }),
      });
      if (!res.ok) throw new Error(`Backend error ${res.status}: ${await res.text()}`);
      setOutput(await res.json());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  // ── Video edits ────────────────────────────────────────────────────────────
  const applyVideoEdit = async (
    endpoint: string,
    body: Record<string, unknown>,
  ) => {
    if (!output?.videoUrl) return;
    setEditLoading(true);
    setEditError(null);

    try {
      const res = await fetch(`/api/video-edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ endpoint, videoUrl: output.videoUrl, ...body }),
      });
      if (!res.ok) throw new Error(`Edit error ${res.status}: ${await res.text()}`);
      const data = await res.json();
      setOutput((prev) => ({ ...prev, videoUrl: data.videoUrl }));
    } catch (err: unknown) {
      setEditError(err instanceof Error ? err.message : "Edit failed.");
    } finally {
      setEditLoading(false);
    }
  };

  const handleTrim = () =>
    applyVideoEdit("trim", {
      start: parseFloat(videoEdits.trimStart) || 0,
      end: parseFloat(videoEdits.trimEnd) || undefined,
    });

  const handleOverlay = () =>
    applyVideoEdit("overlay", {
      text: videoEdits.overlayText,
      position: videoEdits.overlayPosition,
    });

  const handleTransition = () =>
    applyVideoEdit("transition", { transition: videoEdits.transition });

  const edit = (field: keyof VideoEdits) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setVideoEdits((prev) => ({ ...prev, [field]: e.target.value }));

  const hasOutput =
    output &&
    (output.story || output.audioUrl || output.imageUrl || output.videoUrl);

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">

        {/* ── Left: Input ───────────────────────────────────────────────────── */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-indigo-600 mb-4">Enter Prompt</h2>

          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your story…"
            rows={6}
            disabled={loading}
            className="w-full p-4 border rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-indigo-500 mb-4 disabled:opacity-50"
          />

          <select
            value={format}
            onChange={(e) => { setFormat(e.target.value as Format); setOutput(null); setError(null); }}
            disabled={loading}
            className="w-full p-2 border rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-indigo-500 mb-4 disabled:opacity-50"
          >
            <option value="text">📝 Text story</option>
            <option value="audio">🔊 Audio narration</option>
            <option value="image">🖼️ Image illustration</option>
            <option value="video">🎬 Narrated video</option>
          </select>

          {/* ── Voice & speed controls (audio only) ─────────────────────── */}
          {(format === "audio" || format === "video") && (
            <div className="mb-4 p-3 border rounded-lg bg-gray-50 space-y-3">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Voice Options
              </p>

              {/* Voice picker */}
              <div>
                <label className="text-sm text-gray-600 mb-1 block">Voice</label>
                <div className="grid grid-cols-2 gap-2">
                  {(Object.keys(VOICE_LABELS) as VoiceOption[]).map((v) => (
                    <button
                      key={v}
                      onClick={() => setVoice(v)}
                      disabled={loading}
                      className={`px-3 py-2 rounded-lg text-sm border transition text-left ${
                        voice === v
                          ? "bg-indigo-600 text-white border-indigo-600"
                          : "bg-white text-gray-700 border-gray-300 hover:border-indigo-400"
                      } disabled:opacity-50`}
                    >
                      {VOICE_LABELS[v]}
                    </button>
                  ))}
                </div>
              </div>

              {/* Speed picker */}
              <div>
                <label className="text-sm text-gray-600 mb-1 block">Speed</label>
                <div className="flex gap-2">
                  {(Object.keys(SPEED_LABELS) as SpeedOption[]).map((s) => (
                    <button
                      key={s}
                      onClick={() => setSpeed(s)}
                      disabled={loading}
                      className={`flex-1 py-1.5 rounded-lg text-sm border transition ${
                        speed === s
                          ? "bg-indigo-600 text-white border-indigo-600"
                          : "bg-white text-gray-700 border-gray-300 hover:border-indigo-400"
                      } disabled:opacity-50`}
                    >
                      {SPEED_LABELS[s]}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          <button
            onClick={generate}
            disabled={loading || !prompt.trim()}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Generating…
              </>
            ) : (
              "Generate"
            )}
          </button>

          {/* ── Video edit panel (shown only after a video is generated) ──── */}
          {format === "video" && output?.videoUrl && (
            <div className="mt-6 border-t pt-4">
              <h3 className="font-semibold text-gray-700 mb-3">✂️ Edit Video</h3>

              {editError && (
                <p className="text-red-600 text-sm mb-2">{editError}</p>
              )}

              {/* Trim */}
              <div className="mb-4">
                <p className="text-sm text-gray-500 mb-1 font-medium">Trim</p>
                <div className="flex gap-2 items-center">
                  <input
                    type="number"
                    min="0"
                    placeholder="Start (s)"
                    value={videoEdits.trimStart}
                    onChange={edit("trimStart")}
                    className="w-28 p-2 border rounded-lg text-sm text-gray-900 bg-white"
                  />
                  <span className="text-gray-400 text-sm">→</span>
                  <input
                    type="number"
                    min="0"
                    placeholder="End (s)"
                    value={videoEdits.trimEnd}
                    onChange={edit("trimEnd")}
                    className="w-28 p-2 border rounded-lg text-sm text-gray-900 bg-white"
                  />
                  <button
                    onClick={handleTrim}
                    disabled={editLoading}
                    className="px-3 py-2 bg-indigo-100 text-indigo-700 rounded-lg text-sm hover:bg-indigo-200 transition disabled:opacity-50"
                  >
                    Apply
                  </button>
                </div>
              </div>

              {/* Overlay text */}
              <div className="mb-4">
                <p className="text-sm text-gray-500 mb-1 font-medium">Overlay Text</p>
                <div className="flex gap-2 items-center flex-wrap">
                  <input
                    type="text"
                    placeholder="Caption text…"
                    value={videoEdits.overlayText}
                    onChange={edit("overlayText")}
                    className="flex-1 min-w-32 p-2 border rounded-lg text-sm text-gray-900 bg-white"
                  />
                  <select
                    value={videoEdits.overlayPosition}
                    onChange={edit("overlayPosition")}
                    className="p-2 border rounded-lg text-sm text-gray-900 bg-white"
                  >
                    <option value="top">Top</option>
                    <option value="center">Center</option>
                    <option value="bottom">Bottom</option>
                  </select>
                  <button
                    onClick={handleOverlay}
                    disabled={editLoading || !videoEdits.overlayText.trim()}
                    className="px-3 py-2 bg-indigo-100 text-indigo-700 rounded-lg text-sm hover:bg-indigo-200 transition disabled:opacity-50"
                  >
                    Apply
                  </button>
                </div>
              </div>

              {/* Transition */}
              <div className="mb-2">
                <p className="text-sm text-gray-500 mb-1 font-medium">Transition</p>
                <div className="flex gap-2 items-center">
                  <select
                    value={videoEdits.transition}
                    onChange={edit("transition")}
                    className="p-2 border rounded-lg text-sm text-gray-900 bg-white"
                  >
                    <option value="none">None</option>
                    <option value="fade">Fade in + out</option>
                    <option value="fade-in">Fade in only</option>
                  </select>
                  <button
                    onClick={handleTransition}
                    disabled={editLoading || videoEdits.transition === "none"}
                    className="px-3 py-2 bg-indigo-100 text-indigo-700 rounded-lg text-sm hover:bg-indigo-200 transition disabled:opacity-50"
                  >
                    Apply
                  </button>
                </div>
              </div>

              {editLoading && (
                <p className="text-indigo-500 text-sm mt-2 flex items-center gap-2">
                  <span className="inline-block w-3 h-3 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                  Applying edit…
                </p>
              )}
            </div>
          )}
        </div>

        {/* ── Right: Output ─────────────────────────────────────────────────── */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-indigo-600 mb-4">Output</h2>

          {/* Error */}
          {error && (
            <div className="p-4 border border-red-300 rounded-lg bg-red-50 text-red-700 text-sm">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Loading */}
          {loading && !error && (
            <div className="flex flex-col items-center justify-center py-16 text-gray-400 gap-3">
              <span className="inline-block w-8 h-8 border-4 border-indigo-300 border-t-indigo-600 rounded-full animate-spin" />
              <span>Generating your {format}…</span>
              {format === "video" && (
                <span className="text-xs text-center max-w-xs">
                  Video generation takes 30–60 s — building story, narration &amp; image first…
                </span>
              )}
            </div>
          )}

          {/* Results */}
          {!loading && !error && hasOutput && (
            <div className="space-y-4">
              {/* Audio also shows the story text */}
              {format === "audio" && output?.story && (
                <div className="p-3 border rounded-lg bg-gray-50 text-gray-700 text-sm whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                  <p className="text-xs font-semibold text-gray-400 mb-1 uppercase tracking-wide">Story</p>
                  {output.story}
                </div>
              )}

              {format === "text" && output?.story && (
                <div className="p-4 border rounded-lg bg-gray-50 text-gray-900 whitespace-pre-wrap leading-relaxed">
                  {output.story}
                </div>
              )}

              {format === "audio" && output?.audioUrl && (
                <>
                  {output.voice && (
                    <p className="text-xs text-gray-400 mb-1">
                      Voice used:{" "}
                      <span className="font-medium text-gray-600">
                        {VOICE_LABELS[output.voice as VoiceOption] ?? output.voice}
                      </span>
                    </p>
                  )}
                  <audio controls src={output.audioUrl} className="w-full mt-2" />
                </>
              )}

              {format === "image" && output?.imageUrl && (
                <img
                  src={output.imageUrl}
                  alt="Generated illustration"
                  className="rounded-lg shadow-md w-full object-contain"
                />
              )}

              {format === "video" && output?.videoUrl && (
                <video
                  key={output.videoUrl}
                  controls
                  src={output.videoUrl}
                  className="rounded-lg shadow-md w-full"
                />
              )}
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && !hasOutput && (
            <div className="flex items-center justify-center py-16 text-gray-400 text-sm">
              Your generated content will appear here.
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
