import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { authService } from "../services/authService";
import useAuthStore from "../store/useAuthStore";
import Navbar from "../components/Navbar";

export default function LoginPage() {
    const [form, setForm] = useState({ email: "", password: "" });
    const [loading, setLoading] = useState(false);
    const { setAuth } = useAuthStore();
    const navigate = useNavigate();
    const change = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

    async function handleSubmit(e) {
        e.preventDefault();
        if (!form.email || !form.password) { toast.error("Fill in all fields."); return; }
        setLoading(true);
        try {
            const res = await authService.login(form.email, form.password);
            setAuth(res.data.user, res.data.token);
            toast.success(`Welcome back, ${res.data.user.name.split(" ")[0]}! 👋`);
            navigate("/dashboard");
        } catch (err) {
            toast.error(err.response?.data?.detail || "Invalid email or password.");
        } finally { setLoading(false); }
    }

    return (
        <div className="min-h-screen" style={{ background: "#07070f" }}>
            <Navbar />
            {/* Glow */}
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-1/4 right-1/4 w-96 h-96 rounded-full opacity-10"
                    style={{ background: "radial-gradient(ellipse,#8B5CF6,transparent)", filter: "blur(80px)" }} />
                <div className="absolute bottom-1/4 left-1/4 w-96 h-96 rounded-full opacity-10"
                    style={{ background: "radial-gradient(ellipse,#00D4FF,transparent)", filter: "blur(80px)" }} />
            </div>

            <div className="relative flex items-center justify-center px-4 py-20">
                <div className="w-full max-w-sm animate-slide-up">
                    <div className="text-center mb-8">
                        <div className="w-12 h-12 rounded-2xl mx-auto mb-4 flex items-center justify-center text-black font-bold text-lg"
                            style={{ background: "linear-gradient(135deg,#00D4FF,#8B5CF6)" }}>L</div>
                        <h1 className="text-2xl font-bold text-white">Welcome back</h1>
                        <p className="text-gray-500 text-sm mt-1">Sign in to LectureIQ</p>
                    </div>

                    <form onSubmit={handleSubmit} className="glass p-7 space-y-4">
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wide">Email</label>
                            <input type="email" name="email" value={form.email} onChange={change}
                                placeholder="you@college.edu.in" className="neon-input" autoComplete="email" />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wide">Password</label>
                            <input type="password" name="password" value={form.password} onChange={change}
                                placeholder="••••••••" className="neon-input" autoComplete="current-password" />
                        </div>
                        <button type="submit" disabled={loading} className="btn-neon w-full py-3 mt-2">
                            {loading ? "Signing in..." : "Sign in →"}
                        </button>
                    </form>

                    <p className="text-center text-sm text-gray-600 mt-5">
                        Don't have an account?{" "}
                        <Link to="/signup" className="text-neon-cyan hover:underline font-medium">Sign up free</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
