import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { lectureService } from "../services/lectureService";
import useAuthStore from "../store/useAuthStore";
import Navbar from "../components/Navbar";
import LectureCard from "../components/LectureCard";
import { LectureCardSkeleton } from "../components/LoadingSkeleton";

export default function DashboardPage() {
    const { user } = useAuthStore();
    const [lectures, setLectures] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchLectures = useCallback(async (silent = false) => {
        if (!silent) setLoading(true);
        try {
            const res = await lectureService.list();
            setLectures(res.data);
        } catch { if (!silent) toast.error("Failed to load lectures."); }
        finally { setLoading(false); }
    }, []);

    useEffect(() => { fetchLectures(); }, [fetchLectures]);

    useEffect(() => {
        const hasActive = lectures.some(l => l.status === "processing" || l.status === "uploading");
        if (!hasActive) return;
        const t = setInterval(() => fetchLectures(true), 5000);
        return () => clearInterval(t);
    }, [lectures, fetchLectures]);

    async function handleDelete(id, title) {
        if (!window.confirm(`Delete "${title}"?`)) return;
        try {
            await lectureService.delete(id);
            setLectures(p => p.filter(l => l.id !== id));
            toast.success("Deleted.");
        } catch { toast.error("Delete failed."); }
    }

    const processing = lectures.filter(l => ["processing", "uploading"].includes(l.status));
    const ready = lectures.filter(l => l.status === "completed");
    const failed = lectures.filter(l => l.status === "failed");

    return (
        <div className="min-h-screen" style={{ background: "#07070f" }}>
            <Navbar />
            <div className="max-w-4xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-2xl font-bold text-white">
                            Hey, <span className="text-gradient">{user?.name?.split(" ")[0]}</span> 👋
                        </h1>
                        <p className="text-gray-600 text-sm mt-0.5">
                            {lectures.length} lecture{lectures.length !== 1 ? "s" : ""} in your library
                        </p>
                    </div>
                    <Link to="/upload" className="btn-neon flex items-center gap-2">
                        <span className="text-lg">+</span> Upload
                    </Link>
                </div>

                {/* Stats row */}
                {lectures.length > 0 && (
                    <div className="grid grid-cols-3 gap-4 mb-8">
                        {[
                            { label: "Total", count: lectures.length, color: "#00D4FF" },
                            { label: "Ready", count: ready.length, color: "#00FF87" },
                            { label: "Processing", count: processing.length, color: "#FFBB00" },
                        ].map((s, i) => (
                            <div key={i} className="glass p-4 text-center">
                                <p className="text-2xl font-bold" style={{ color: s.color }}>{s.count}</p>
                                <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
                            </div>
                        ))}
                    </div>
                )}

                {loading && <div className="space-y-3">{[1, 2, 3].map(i => <LectureCardSkeleton key={i} />)}</div>}

                {/* Empty state */}
                {!loading && lectures.length === 0 && (
                    <div className="glass p-16 text-center">
                        <div className="text-6xl mb-5 animate-float inline-block">🎙️</div>
                        <h2 className="text-xl font-bold text-white mb-2">No lectures yet</h2>
                        <p className="text-gray-500 text-sm mb-7">
                            Upload your first lecture recording to get started.
                        </p>
                        <Link to="/upload" className="btn-neon inline-block">Upload your first lecture →</Link>
                    </div>
                )}

                {/* Processing */}
                {processing.length > 0 && (
                    <section className="mb-6">
                        <p className="text-xs font-bold uppercase tracking-widest text-yellow-500/70 mb-3 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse inline-block" />
                            Processing ({processing.length})
                        </p>
                        <div className="space-y-3">{processing.map(l => <LectureCard key={l.id} lecture={l} onDelete={handleDelete} />)}</div>
                    </section>
                )}

                {/* Ready */}
                {ready.length > 0 && (
                    <section className="mb-6">
                        <p className="text-xs font-bold uppercase tracking-widest text-neon-green/60 mb-3">Ready ({ready.length})</p>
                        <div className="space-y-3">{ready.map(l => <LectureCard key={l.id} lecture={l} onDelete={handleDelete} />)}</div>
                    </section>
                )}

                {/* Failed */}
                {failed.length > 0 && (
                    <section>
                        <p className="text-xs font-bold uppercase tracking-widest text-red-500/60 mb-3">Failed ({failed.length})</p>
                        <div className="space-y-3">{failed.map(l => <LectureCard key={l.id} lecture={l} onDelete={handleDelete} />)}</div>
                    </section>
                )}
            </div>
        </div>
    );
}
