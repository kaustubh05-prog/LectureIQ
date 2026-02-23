import { useState } from "react";

export default function FlashcardViewer({ flashcards }) {
    const [current, setCurrent] = useState(0);
    const [flipped, setFlipped] = useState(false);
    const [done, setDone] = useState(new Set());

    if (!flashcards?.length)
        return <p className="text-center text-gray-600 py-16">No flashcards available.</p>;

    const card = flashcards[current];
    const total = flashcards.length;

    function goNext() { setFlipped(false); setTimeout(() => setCurrent(c => Math.min(c + 1, total - 1)), 150); }
    function goPrev() { setFlipped(false); setTimeout(() => setCurrent(c => Math.max(c - 1, 0)), 150); }
    function markDone() { setDone(d => new Set([...d, current])); if (current < total - 1) goNext(); }
    function reset() { setCurrent(0); setFlipped(false); setDone(new Set()); }

    return (
        <div className="flex flex-col items-center gap-6 py-8 px-4">
            {/* Progress */}
            <div className="w-full max-w-lg">
                <div className="flex justify-between text-xs mb-2">
                    <span className="text-gray-500">Card {current + 1} / {total}</span>
                    <span className="text-neon-green font-medium">{done.size} / {total} mastered</span>
                </div>
                <div className="neon-progress" style={{ height: "4px" }}>
                    <div className="neon-progress-bar"
                        style={{
                            width: `${(done.size / total) * 100}%`,
                            background: "linear-gradient(90deg,#00FF87,#00D4FF)",
                        }} />
                </div>
            </div>

            {/* Card */}
            <div className="w-full max-w-lg h-64 cursor-pointer select-none"
                style={{ perspective: "1200px" }}
                onClick={() => setFlipped(f => !f)}>
                <div className="relative w-full h-full transition-transform duration-500"
                    style={{ transformStyle: "preserve-3d", transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)" }}>

                    {/* Front */}
                    <div className="absolute inset-0 rounded-2xl p-7 flex flex-col items-center justify-center text-center"
                        style={{
                            backfaceVisibility: "hidden",
                            background: "linear-gradient(135deg,rgba(0,212,255,0.08) 0%,rgba(139,92,246,0.08) 100%)",
                            border: "1px solid rgba(0,212,255,0.2)",
                            boxShadow: "0 0 30px rgba(0,212,255,0.08)",
                        }}>
                        <span className="text-xs text-neon-cyan/60 uppercase tracking-widest mb-4">Question</span>
                        <p className="text-lg font-medium text-white leading-relaxed">{card.question}</p>
                        <span className="text-xs text-gray-700 mt-6">Tap to flip</span>
                    </div>

                    {/* Back */}
                    <div className="absolute inset-0 rounded-2xl p-7 flex flex-col items-center justify-center text-center"
                        style={{
                            backfaceVisibility: "hidden",
                            transform: "rotateY(180deg)",
                            background: "linear-gradient(135deg,rgba(139,92,246,0.12) 0%,rgba(0,212,255,0.08) 100%)",
                            border: "1px solid rgba(139,92,246,0.25)",
                            boxShadow: "0 0 30px rgba(139,92,246,0.1)",
                        }}>
                        <span className="text-xs text-neon-purple/70 uppercase tracking-widest mb-4">Answer</span>
                        <p className="text-base text-gray-100 leading-relaxed">{card.answer}</p>
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-3">
                <button onClick={goPrev} disabled={current === 0} className="btn-ghost px-5 py-2 text-sm">← Prev</button>

                <button onClick={markDone} disabled={done.has(current)}
                    className={`px-5 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${done.has(current)
                            ? "opacity-50 cursor-default text-neon-green border border-neon-green/30"
                            : "text-black"
                        }`}
                    style={!done.has(current) ? {
                        background: "linear-gradient(135deg,#00FF87,#00D4FF)",
                        boxShadow: "0 0 20px rgba(0,255,135,0.3)",
                    } : {}}>
                    {done.has(current) ? "✓ Mastered" : "Got it ✓"}
                </button>

                <button onClick={goNext} disabled={current === total - 1} className="btn-ghost px-5 py-2 text-sm">Next →</button>
            </div>

            {done.size === total && (
                <div className="text-center animate-slide-up">
                    <p className="text-neon-green font-bold text-lg mb-3">🎉 All {total} cards mastered!</p>
                    <button onClick={reset} className="btn-ghost text-sm">Start over</button>
                </div>
            )}
        </div>
    );
}
