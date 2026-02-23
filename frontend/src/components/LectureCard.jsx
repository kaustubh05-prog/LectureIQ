import { Link } from "react-router-dom";
import StatusBadge from "./StatusBadge";
import { formatRelativeTime, formatDuration } from "../utils/formatters";

export default function LectureCard({ lecture, onDelete }) {
    const isReady = lecture.status === "completed";
    const isProcessing = lecture.status === "processing" || lecture.status === "uploading";
    const isFailed = lecture.status === "failed";

    return (
        <div className="glass-hover p-5 animate-fade-in">
            <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <StatusBadge status={lecture.status} />
                        {lecture.duration && (
                            <span className="text-xs text-gray-500">{formatDuration(lecture.duration)}</span>
                        )}
                    </div>
                    <h3 className="font-semibold text-white truncate leading-snug text-[15px]">
                        {lecture.title}
                    </h3>
                    <p className="text-xs text-gray-600 mt-1">{formatRelativeTime(lecture.uploaded_at)}</p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                    {isReady && (
                        <Link to={`/lectures/${lecture.id}`} className="btn-neon text-xs py-1.5 px-4">
                            Open →
                        </Link>
                    )}
                    <button
                        onClick={() => onDelete(lecture.id, lecture.title)}
                        className="p-1.5 rounded-lg text-gray-600 hover:text-red-400 hover:bg-red-500/10 transition-all"
                        title="Delete"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            </div>

            {isProcessing && (
                <div className="mt-4">
                    <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-gray-500">AI is analysing your lecture...</span>
                        <span className="text-neon-cyan font-medium">{lecture.progress}%</span>
                    </div>
                    <div className="neon-progress">
                        <div className="neon-progress-bar" style={{ width: `${Math.max(lecture.progress, 4)}%` }} />
                    </div>
                </div>
            )}

            {isFailed && (
                <p className="mt-2 text-xs text-red-400 truncate">⚠ {lecture.error_message || "Processing failed"}</p>
            )}
        </div>
    );
}
