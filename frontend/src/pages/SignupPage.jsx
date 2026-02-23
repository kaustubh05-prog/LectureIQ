import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { authService } from "../services/authService";
import useAuthStore from "../store/useAuthStore";
import Navbar from "../components/Navbar";

export default function SignupPage() {
    const [form, setForm] = useState({ name: "", email: "", password: "" });
    const [loading, setLoading] = useState(false);
    const { setAuth } = useAuthStore();
    const navigate = useNavigate();
    const change = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

    async function handleSubmit(e) {
        e.preventDefault();
        if (!form.name || !form.email || !form.password) { toast.error("Fill in all fields."); return; }
        if (form.password.length < 8) { toast.error("Password must be at least 8 characters."); return; }
        setLoading(true);
        try {
            const res = await authService.register(form.name, form.email, form.password);
            setAuth(res.data.user, res.data.token);
            toast.success(`Welcome to LectureIQ, ${res.data.user.name.split(" ")[0]}! 🎉`);
            navigate("/dashboard");
        } catch (err) {
            toast.error(err.response?.data?.detail || "Registration failed. Try again.");
        } finally { setLoading(false); }
    }

    return (
        <div className="min-h-screen" style={{ background: "#07070f" }}>
            <Navbar />
            <div className="fixed inset-0 pointer-events-none">
                <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full opacity-10"
                    style={{ background: "radial-gradient(ellipse,#00D4FF,transparent)", filter: "blur(100px)" }} />
                <div className="absolute bottom-0 left-0 w-[500px] h-[500px] rounded-full opacity-10"
                    style={{ background: "radial-gradient(ellipse,#8B5CF6,transparent)", filter: "blur(100px)" }} />
            </div>

            <div className="relative flex items-center justify-center px-4 py-16">
                <div className="w-full max-w-sm animate-slide-up">
                    <div className="text-center mb-8">
                        <div className="w-12 h-12 rounded-2xl mx-auto mb-4 flex items-center justify-center text-black font-bold text-lg"
                            style={{ background: "linear-gradient(135deg,#00D4FF,#8B5CF6)" }}>L</div>
                        <h1 className="text-2xl font-bold text-white">Create account</h1>
                        <p className="text-gray-500 text-sm mt-1">Free forever · No credit card needed</p>
                    </div>

                    <form onSubmit={handleSubmit} className="glass p-7 space-y-4">
                        {[
                            { name: "name", label: "Full name", type: "text", ph: "Rahul Sharma" },
                            { name: "email", label: "Email", type: "email", ph: "rahul@college.edu.in" },
                            { name: "password", label: "Password", type: "password", ph: "Min. 8 characters" },
                        ].map(f => (
                            <div key={f.name}>
                                <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wide">{f.label}</label>
                                <input type={f.type} name={f.name} value={form[f.name]} onChange={change}
                                    placeholder={f.ph} className="neon-input"
                                    autoComplete={f.name === "password" ? "new-password" : f.name} />
                            </div>
                        ))}
                        <button type="submit" disabled={loading} className="btn-neon w-full py-3 mt-2">
                            {loading ? "Creating account..." : "Create account →"}
                        </button>
                    </form>

                    <p className="text-center text-sm text-gray-600 mt-5">
                        Already have an account?{" "}
                        <Link to="/login" className="text-neon-cyan hover:underline font-medium">Sign in</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
