import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";
import { lectureService } from "../services/lectureService";
import Navbar from "../components/Navbar";
import { formatFileSize } from "../utils/formatters";

export default function UploadPage() {
    const [file, setFile] = useState(null);
    const [title, setTitle] = useState("");
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const navigate = useNavigate();

    const onDrop = useCallback((accepted, rejected) => {
        if (rejected.length > 0) {
            const err = rejected[0].errors[0];
            toast.error(err.code === "file-too-large" ? "File too large. Max 100 MB." : "Invalid format. Use MP3, WAV, or M4A.");
            return;
        }
        const f = accepted[0];
        setFile(f);
        setTitle(f.name.replace(/\.[^.]+$/, ""));
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { "audio/*": [".mp3", ".wav", ".m4a", ".ogg", ".flac"] },
        maxSize: 100 * 1024 * 1024,
        multiple: false,
    });

    async function handleUpload() {
        if (!file) { toast.error("Select a file first."); return; }
        if (!title.trim()) { toast.error("Enter a lecture title."); return; }
        setUploading(true);
        try {
            const form = new FormData();
            form.append("file", file);
            form.append("title", title.trim());
            const res = await lectureService.upload(form, setProgress);
            toast.success("Upload complete! Processing started 🚀");
            navigate(`/lectures/${res.data.id}`);
        } catch (err) {
            toast.error(err.response?.data?.detail || "Upload failed.");
            setUploading(false);
            setProgress(0);
        }
    }

    return (
        <div className="min-h-screen" style={{ background: "#07070f" }}>
            <Navbar />
            {/* Glow */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-20 right-0 w-96 h-96 opacity-10 rounded-full"
                    style={{ background: "radial-gradient(ellipse,#8B5CF6,transparent)", filter: "blur(80px)" }} />
            </div>

            <div className="relative max-w-xl mx-auto px-4 py-12">
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-white">Upload a Lecture</h1>
                    <p className="text-gray-500 text-sm mt-1">
                        MP3, WAV, M4A, OGG, FLAC · Max 100 MB · Hindi + English
                    </p>
                </div>

                <div className="glass p-7 space-y-5">
                    {/* Dropzone */}
                    <div {...getRootProps()}
                        className="rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 border-2 border-dashed"
                        style={{
                            borderColor: isDragActive ? "#00D4FF" : file ? "#00FF87" : "#1e1e38",
                            background: isDragActive ? "rgba(0,212,255,0.05)" : file ? "rgba(0,255,135,0.04)" : "rgba(255,255,255,0.02)",
                            boxShadow: isDragActive ? "0 0 30px rgba(0,212,255,0.15)" : file ? "0 0 30px rgba(0,255,135,0.1)" : "none",
                        }}>
                        <input {...getInputProps()} />
                        {file ? (
                            <div className="animate-slide-up">
                                <div className="text-5xl mb-3">🎵</div>
                                <p className="font-semibold text-neon-green">{file.name}</p>
                                <p className="text-xs text-gray-500 mt-1">{formatFileSize(file.size)}</p>
                                <button onClick={e => { e.stopPropagation(); setFile(null); setTitle(""); }}
                                    className="text-xs text-red-400 hover:text-red-300 mt-3 underline">
                                    Remove
                                </button>
                            </div>
                        ) : isDragActive ? (
                            <div>
                                <div className="text-5xl mb-3">📂</div>
                                <p className="text-neon-cyan font-semibold">Drop it here!</p>
                            </div>
                        ) : (
                            <div>
                                <div className="text-5xl mb-3 animate-float inline-block">🎙️</div>
                                <p className="text-gray-300 font-medium">Drag & drop your lecture here</p>
                                <p className="text-sm text-gray-600 mt-1">or click to browse</p>
                            </div>
                        )}
                    </div>

                    {/* Title */}
                    <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wide">
                            Lecture title
                        </label>
                        <input type="text" value={title} onChange={e => setTitle(e.target.value)} maxLength={200}
                            placeholder="e.g. Data Structures — Lecture 3: Binary Search Trees"
                            className="neon-input" />
                    </div>

                    {/* Upload progress */}
                    {uploading && (
                        <div className="animate-slide-up">
                            <div className="flex justify-between text-xs mb-2">
                                <span className="text-gray-400">Uploading...</span>
                                <span className="text-neon-cyan font-medium">{progress}%</span>
                            </div>
                            <div className="neon-progress">
                                <div className="neon-progress-bar" style={{ width: `${progress}%` }} />
                            </div>
                        </div>
                    )}

                    <button onClick={handleUpload} disabled={uploading || !file} className="btn-neon w-full py-3.5 text-base">
                        {uploading ? `Uploading… ${progress}%` : "Upload & Process →"}
                    </button>

                    <p className="text-xs text-center text-gray-700">
                        Processing takes 1–3 minutes depending on lecture length.
                    </p>
                </div>
            </div>
        </div>
    );
}
