import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";

const FEATURES = [
    { icon: "🎙️", title: "Upload Any Lecture", desc: "MP3, WAV, M4A · Hindi + English · Up to 100 MB", color: "#00D4FF" },
    { icon: "📝", title: "Structured Notes", desc: "AI Markdown notes with concepts and diagrams", color: "#8B5CF6" },
    { icon: "🃏", title: "Flashcards", desc: "Interactive 3D flip-cards for rapid revision", color: "#00FF87" },
    { icon: "✅", title: "MCQ Quiz", desc: "Auto-graded quiz with detailed explanations", color: "#FF0080" },
    { icon: "🎬", title: "Curated Resources", desc: "YouTube + docs + practice problems, auto-linked", color: "#FFBB00" },
    { icon: "⚡", title: "Under 3 Minutes", desc: "Full pipeline faster than brewing chai", color: "#00D4FF" },
];

const STEPS = [
    { n: "01", label: "Upload", desc: "Drop your lecture recording", color: "#00D4FF" },
    { n: "02", label: "Process", desc: "Whisper + Groq AI does the work", color: "#8B5CF6" },
    { n: "03", label: "Study", desc: "Notes, cards, quiz — ready to go", color: "#00FF87" },
];

export default function HomePage() {
    return (
        <div className="min-h-screen" style={{ background: "#07070f" }}>
            <Navbar />

            {/* Hero */}
            <section className="relative overflow-hidden">
                {/* Glow blobs */}
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] rounded-full opacity-20"
                        style={{ background: "radial-gradient(ellipse,#8B5CF6 0%,transparent 70%)", filter: "blur(60px)" }} />
                    <div className="absolute top-32 left-0 w-[400px] h-[300px] rounded-full opacity-15"
                        style={{ background: "radial-gradient(ellipse,#00D4FF 0%,transparent 70%)", filter: "blur(60px)" }} />
                </div>

                <div className="relative max-w-4xl mx-auto px-4 pt-24 pb-20 text-center">
                    <div className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-medium mb-8 border"
                        style={{ background: "rgba(0,212,255,0.08)", borderColor: "rgba(0,212,255,0.2)", color: "#00D4FF" }}>
                        🏆 AWS AI for Bharat Hackathon 2026
                    </div>

                    <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-[1.1] mb-6">
                        Turn lectures into<br />
                        <span className="text-gradient">study materials</span><br />
                        in under 3 minutes
                    </h1>

                    <p className="text-lg text-gray-400 mb-10 max-w-xl mx-auto leading-relaxed">
                        Upload your lecture recording → get structured notes, flashcards, MCQs,
                        and curated resources automatically. Supports Hindi + English.
                    </p>

                    <div className="flex items-center justify-center gap-4 flex-wrap">
                        <Link to="/signup" className="btn-neon py-3.5 px-8 text-base">
                            Get started free →
                        </Link>
                        <Link to="/login" className="btn-ghost py-3.5 px-7 text-base">
                            Sign in
                        </Link>
                    </div>

                    {/* Floating stat chips */}
                    <div className="flex justify-center gap-6 mt-14 flex-wrap">
                        {[
                            { n: "< 3 min", l: "Processing time" },
                            { n: "100%", l: "Free to use" },
                            { n: "Hi + En", l: "Language support" },
                        ].map((s, i) => (
                            <div key={i} className="glass px-5 py-3 text-center animate-float"
                                style={{ animationDelay: `${i * 0.5}s` }}>
                                <p className="text-neon-cyan font-bold text-lg">{s.n}</p>
                                <p className="text-gray-500 text-xs mt-0.5">{s.l}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* How it works */}
            <section className="max-w-4xl mx-auto px-4 py-20">
                <p className="text-xs font-bold text-center uppercase tracking-widest text-gray-600 mb-3">How it works</p>
                <h2 className="text-3xl font-bold text-center text-white mb-12">Three steps to smarter studying</h2>
                <div className="grid grid-cols-3 gap-6">
                    {STEPS.map((s, i) => (
                        <div key={i} className="glass-hover p-6 text-center">
                            <div className="text-4xl font-extrabold mb-3" style={{ color: s.color, opacity: 0.3 }}>{s.n}</div>
                            <h3 className="font-bold text-white text-lg mb-2">{s.label}</h3>
                            <p className="text-sm text-gray-500">{s.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Features */}
            <section className="max-w-5xl mx-auto px-4 pb-20">
                <h2 className="text-3xl font-bold text-center text-white mb-12">Everything you need</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {FEATURES.map((f, i) => (
                        <div key={i} className="glass-hover p-5 group">
                            <div className="text-3xl mb-3 group-hover:animate-float inline-block">{f.icon}</div>
                            <h3 className="font-semibold text-white mb-1 text-[15px]">{f.title}</h3>
                            <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA */}
            <section className="max-w-3xl mx-auto px-4 pb-24 text-center">
                <div className="glass p-12 relative overflow-hidden">
                    <div className="absolute inset-0 pointer-events-none"
                        style={{ background: "radial-gradient(ellipse at center,rgba(139,92,246,0.12) 0%,transparent 70%)" }} />
                    <h2 className="text-3xl font-extrabold text-white mb-3 relative">Ready to study smarter?</h2>
                    <p className="text-gray-400 mb-8 relative">Join students across India using LectureIQ.</p>
                    <Link to="/signup" className="btn-neon py-3.5 px-10 text-base">
                        Start for free →
                    </Link>
                </div>
            </section>

            <footer className="text-center text-xs text-gray-700 pb-8">
                Built with ❤️ by Team CodeShiksha · AWS AI for Bharat Hackathon 2026
            </footer>
        </div>
    );
}
