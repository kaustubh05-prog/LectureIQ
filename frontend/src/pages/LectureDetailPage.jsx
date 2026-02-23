import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import toast from "react-hot-toast";
import { lectureService } from "../services/lectureService";
import Navbar from "../components/Navbar";
import StatusBadge from "../components/StatusBadge";
import FlashcardViewer from "../components/FlashcardViewer";
import QuizRunner from "../components/QuizRunner";
import ResourceList from "../components/ResourceList";
import { LectureCardSkeleton } from "../components/LoadingSkeleton";
import { formatDuration, formatDate } from "../utils/formatters";

const TABS = [
    { id: "notes", label: "📝 Notes" },
    { id: "flashcards", label: "🃏 Flashcards" },
    { id: "quiz", label: "✅ Quiz" },
    { id: "resources", label: "🎬 Resources" },
    { id: "transcript", label: "🎙️ Transcript" },
];

export default function LectureDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [lecture, setLecture] = useState(null);
    const [loading, setLoading] = useState(true);
    const [tab, setTab] = useState("notes");

    const fetch = useCallback(async (silent = false) => {
        if (!silent) setLoading(true);
        try {
            const res = await lectureService.getDetail(id);
            setLecture(res.data);
        } catch (err) {
            if (err.response?.status === 404) { toast.error("Not found."); navigate("/dashboard"); }
            else toast.error("Failed to load.");
        } finally { setLoading(false); }
    }, [id, navigate]);

    useEffect(() => { fetch(); }, [fetch]);

    useEffect(() => {
        if (!lecture) return;
        if (!["processing", "uploading"].includes(lecture.status)) return;
        const t = setInterval(() => fetch(true), 4000);
        return () => clearInterval(t);
    }, [lecture, fetch]);

    if (loading) return (
        <div className="min-h-screen" style={{ background: "#07070f" }}>
            <Navbar />
            <div className="max-w-4xl mx-auto px-4 py-8 space-y-3">
                {[1, 2, 3].map(i => <LectureCardSkeleton key={i} />)}
            </div>
        </div>
    );

    if (!lecture) return null;

    const isProcessing = ["processing", "uploading"].includes(lecture.status);
    const isCompleted = lecture.status === "completed";
    const isFailed = lecture.status === "failed";

    return (
        <div className="min-h-screen" style={{ background: "#07070f" }}>
            <Navbar />
            <div className="max-w-4xl mx-auto px-4 py-8">

                {/* Header card */}
                <div className="glass p-6 mb-5">
                    <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                                <StatusBadge status={lecture.status} />
                                {lecture.duration && <span className="text-xs text-gray-600">{formatDuration(lecture.duration)}</span>}
                                <span className="text-xs text-gray-700">{formatDate(lecture.uploaded_at)}</span>
                            </div>
                            <h1 className="text-xl font-bold text-white leading-snug">{lecture.title}</h1>
                            {lecture.key_concepts?.length > 0 && (
                                <div className="flex flex-wrap gap-1.5 mt-2.5">
                                    {lecture.key_concepts.map((c, i) => (
                                        <span key={i} className="nbadge text-xs"
                                            style={{ background: "rgba(0,212,255,0.08)", color: "rgba(0,212,255,0.7)" }}>
                                            {c}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                        <button onClick={() => navigate("/dashboard")} className="btn-ghost text-sm shrink-0">← Back</button>
                    </div>

                    {isProcessing && (
                        <div className="mt-5">
                            <div className="flex justify-between text-xs mb-1.5">
                                <span className="text-gray-500">AI is analysing your lecture…</span>
                                <span className="text-neon-cyan font-bold">{lecture.progress}%</span>
                            </div>
                            <div className="neon-progress">
                                <div className="neon-progress-bar" style={{ width: `${Math.max(lecture.progress, 4)}%` }} />
                            </div>
                            <p className="text-xs text-gray-700 mt-1.5">Usually 1–3 minutes · You can leave and come back.</p>
                        </div>
                    )}

                    {isFailed && (
                        <div className="mt-4 rounded-xl p-3 border border-red-900/40"
                            style={{ background: "rgba(255,69,96,0.06)" }}>
                            <p className="text-sm text-red-400 font-medium">Processing failed</p>
                            {lecture.error_message && <p className="text-xs text-red-600 mt-0.5">{lecture.error_message}</p>}
                        </div>
                    )}
                </div>

                {isCompleted && (
                    <>
                        {/* Tabs */}
                        <div className="flex gap-1.5 overflow-x-auto pb-1 mb-4">
                            {TABS.map(t => (
                                <button key={t.id} onClick={() => setTab(t.id)}
                                    className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all duration-150 ${tab === t.id ? "text-black" : "text-gray-500 hover:text-gray-300 border border-dark-border"}`}
                                    style={tab === t.id ? {
                                        background: "linear-gradient(135deg,#00D4FF,#8B5CF6)",
                                        boxShadow: "0 0 15px rgba(0,212,255,0.3)",
                                    } : { background: "rgba(255,255,255,0.03)" }}>
                                    {t.label}
                                    {t.id === "flashcards" && lecture.flashcards?.length > 0 && (
                                        <span className={`ml-1.5 text-xs rounded-full px-1.5 ${tab === t.id ? "bg-black/20 text-white" : "bg-dark-border text-gray-500"}`}>
                                            {lecture.flashcards.length}
                                        </span>
                                    )}
                                    {t.id === "quiz" && lecture.mcqs?.length > 0 && (
                                        <span className={`ml-1.5 text-xs rounded-full px-1.5 ${tab === t.id ? "bg-black/20 text-white" : "bg-dark-border text-gray-500"}`}>
                                            {lecture.mcqs.length}
                                        </span>
                                    )}
                                </button>
                            ))}
                        </div>

                        {/* Tab panels */}
                        <div className="glass animate-fade-in">
                            {/* Notes */}
                            {tab === "notes" && (
                                <div className="p-6 prose prose-invert prose-sm max-w-none
                  prose-headings:text-white prose-p:text-gray-300
                  prose-strong:text-white prose-code:text-neon-cyan
                  prose-code:bg-dark-surface prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded
                  prose-pre:bg-dark-surface prose-pre:border prose-pre:border-dark-border
                  prose-a:text-neon-cyan prose-blockquote:border-neon-cyan/30
                  prose-li:text-gray-300 prose-hr:border-dark-border">
                                    {lecture.notes
                                        ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{lecture.notes}</ReactMarkdown>
                                        : <p className="text-gray-600 text-center py-10">Notes not available.</p>}
                                </div>
                            )}

                            {tab === "flashcards" && <FlashcardViewer flashcards={lecture.flashcards} />}
                            {tab === "quiz" && <QuizRunner lectureId={id} mcqs={lecture.mcqs} />}

                            {tab === "resources" && (
                                <div className="p-5"><ResourceList resources={lecture.resources} /></div>
                            )}

                            {tab === "transcript" && (
                                <div className="p-6">
                                    {lecture.transcript ? (
                                        <>
                                            <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
                                                <span>Language: <strong className="text-neon-cyan">{lecture.transcript.language}</strong></span>
                                                <span>·</span>
                                                <span>{lecture.transcript.segments?.length} segments</span>
                                            </div>
                                            <div className="space-y-1 max-h-[60vh] overflow-y-auto pr-2">
                                                {lecture.transcript.segments?.map((seg, i) => (
                                                    <div key={i} className="flex gap-3 text-sm hover:bg-white/[0.02] rounded-lg px-2 py-1.5 group">
                                                        <span className="text-gray-700 shrink-0 w-14 text-xs pt-0.5 font-mono group-hover:text-neon-cyan transition-colors">
                                                            {formatDuration(seg.start)}
                                                        </span>
                                                        <p className="text-gray-300 leading-relaxed">{seg.text}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </>
                                    ) : (
                                        <p className="text-gray-600 text-center py-10">Transcript not available.</p>
                                    )}
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
