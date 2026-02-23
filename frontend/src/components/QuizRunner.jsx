import { useState } from "react";
import { lectureService } from "../services/lectureService";
import toast from "react-hot-toast";

export default function QuizRunner({ lectureId, mcqs }) {
    const [selected, setSelected] = useState({});
    const [result, setResult] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    if (!mcqs?.length)
        return <p className="text-center text-gray-600 py-16">No questions available.</p>;

    async function handleSubmit() {
        if (Object.keys(selected).length < mcqs.length) {
            toast.error(`Please answer all ${mcqs.length} questions first.`);
            return;
        }
        setSubmitting(true);
        try {
            const res = await lectureService.submitQuiz(lectureId, mcqs.map((_, i) => selected[i]));
            setResult(res.data);
        } catch { toast.error("Failed to submit. Try again."); }
        finally { setSubmitting(false); }
    }

    if (result) {
        const pct = result.percentage;
        const glow = pct >= 80 ? "rgba(0,255,135,0.3)" : pct >= 50 ? "rgba(255,187,0,0.3)" : "rgba(255,69,96,0.3)";
        const col = pct >= 80 ? "#00FF87" : pct >= 50 ? "#FFBB00" : "#FF4560";

        return (
            <div className="py-6 px-4 space-y-5 animate-slide-up">
                {/* Score card */}
                <div className="rounded-2xl p-8 text-center"
                    style={{
                        border: `1px solid ${col}40`, boxShadow: `0 0 40px ${glow}`,
                        background: `linear-gradient(135deg,${col}0d 0%,transparent 100%)`
                    }}>
                    <p className="text-6xl font-extrabold mb-1" style={{ color: col }}>{pct}%</p>
                    <p className="text-gray-300 text-lg">{result.score} / {result.total} correct</p>
                    <p className="text-sm mt-2" style={{ color: col }}>
                        {pct >= 80 ? "🎉 Excellent!" : pct >= 50 ? "👍 Good effort!" : "📚 Keep studying!"}
                    </p>
                </div>

                {/* Breakdown */}
                {result.details.map((d, i) => (
                    <div key={i} className="glass rounded-2xl p-5"
                        style={{ borderLeft: `3px solid ${d.is_correct ? "#00FF87" : "#FF4560"}` }}>
                        <p className="font-medium text-white mb-3 text-sm">Q{i + 1}. {mcqs[i].question}</p>
                        <div className="space-y-1.5 mb-3">
                            {mcqs[i].options.map((opt, j) => (
                                <div key={j} className={`text-sm px-3 py-2 rounded-lg transition-all ${j === d.correct_answer ? "text-neon-green font-medium"
                                        : j === d.your_answer && !d.is_correct ? "text-red-400 line-through"
                                            : "text-gray-500"}`}
                                    style={{
                                        background: j === d.correct_answer ? "rgba(0,255,135,0.08)"
                                            : j === d.your_answer && !d.is_correct ? "rgba(255,69,96,0.08)" : "transparent"
                                    }}>
                                    {j === d.correct_answer ? "✓ " : j === d.your_answer && !d.is_correct ? "✗ " : "  "}
                                    {opt}
                                </div>
                            ))}
                        </div>
                        <p className="text-xs text-gray-500 rounded-xl px-3 py-2"
                            style={{ background: "rgba(255,255,255,0.03)" }}>
                            💡 {d.explanation}
                        </p>
                    </div>
                ))}

                <div className="text-center pt-2">
                    <button onClick={() => { setResult(null); setSelected({}); }} className="btn-neon">
                        Retake Quiz
                    </button>
                </div>
            </div>
        );
    }

    const answered = Object.keys(selected).length;
    return (
        <div className="py-6 px-4 space-y-5">
            <div className="flex justify-between text-sm text-gray-500">
                <span>{mcqs.length} questions</span>
                <span className="text-neon-cyan">{answered} / {mcqs.length} answered</span>
            </div>

            {mcqs.map((mcq, i) => (
                <div key={mcq.id} className="glass rounded-2xl p-5">
                    <p className="font-medium text-white mb-3 text-sm leading-relaxed">
                        <span className="text-neon-cyan mr-2 font-bold">Q{i + 1}.</span>{mcq.question}
                    </p>
                    <div className="space-y-2">
                        {mcq.options.map((opt, j) => (
                            <button key={j} onClick={() => setSelected(s => ({ ...s, [i]: j }))}
                                className={`w-full text-left px-4 py-3 rounded-xl text-sm transition-all duration-150 border ${selected[i] === j
                                        ? "border-neon-cyan/50 text-neon-cyan"
                                        : "border-dark-border text-gray-400 hover:border-gray-600 hover:text-gray-200"}`}
                                style={selected[i] === j ? {
                                    background: "rgba(0,212,255,0.08)",
                                    boxShadow: "0 0 15px rgba(0,212,255,0.1)",
                                } : { background: "rgba(255,255,255,0.02)" }}>
                                <span className="font-bold mr-2 opacity-60">{["A", "B", "C", "D"][j]}.</span>{opt}
                            </button>
                        ))}
                    </div>
                </div>
            ))}

            <div className="text-center pt-2">
                <button onClick={handleSubmit} disabled={submitting || answered < mcqs.length}
                    className="btn-neon px-10 py-3 text-base">
                    {submitting ? "Submitting..." : `Submit Quiz (${answered}/${mcqs.length})`}
                </button>
                {answered < mcqs.length && (
                    <p className="text-xs text-gray-700 mt-2">Answer all questions to submit</p>
                )}
            </div>
        </div>
    );
}
