import { Link, useNavigate, useLocation } from "react-router-dom";
import useAuthStore from "../store/useAuthStore";
import toast from "react-hot-toast";

export default function Navbar() {
    const { user, logout } = useAuthStore();
    const navigate = useNavigate();
    const location = useLocation();

    function handleLogout() {
        logout();
        toast.success("Logged out");
        navigate("/");
    }

    const isActive = (path) => location.pathname === path;

    return (
        <nav
            className="sticky top-0 z-50 border-b border-dark-border"
            style={{ background: "rgba(7,7,15,0.85)", backdropFilter: "blur(20px)" }}
        >
            <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                {/* Logo */}
                <Link to={user ? "/dashboard" : "/"} className="flex items-center gap-2.5 group">
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center text-black font-bold text-sm"
                        style={{ background: "linear-gradient(135deg,#00D4FF,#8B5CF6)" }}>
                        L
                    </div>
                    <span className="font-bold text-base text-white">
                        Lecture<span className="text-gradient">IQ</span>
                    </span>
                </Link>

                {user ? (
                    <div className="flex items-center gap-1">
                        <Link
                            to="/dashboard"
                            className={`px-4 py-1.5 rounded-lg text-sm transition-all duration-150 ${isActive("/dashboard")
                                    ? "text-neon-cyan bg-neon-cyan/10"
                                    : "text-gray-400 hover:text-white hover:bg-white/5"
                                }`}
                        >
                            Dashboard
                        </Link>
                        <Link
                            to="/upload"
                            className={`px-4 py-1.5 rounded-lg text-sm transition-all duration-150 ${isActive("/upload")
                                    ? "text-neon-cyan bg-neon-cyan/10"
                                    : "text-gray-400 hover:text-white hover:bg-white/5"
                                }`}
                        >
                            Upload
                        </Link>
                        <div className="ml-3 pl-3 border-l border-dark-border flex items-center gap-3">
                            <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-black"
                                style={{ background: "linear-gradient(135deg,#00D4FF,#8B5CF6)" }}>
                                {user.name[0].toUpperCase()}
                            </div>
                            <button onClick={handleLogout}
                                className="text-xs text-gray-500 hover:text-red-400 transition-colors">
                                Logout
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center gap-3">
                        <Link to="/login" className="text-sm text-gray-400 hover:text-white transition-colors px-3 py-1.5">
                            Login
                        </Link>
                        <Link to="/signup" className="btn-neon text-sm py-2 px-5">
                            Get started →
                        </Link>
                    </div>
                )}
            </div>
        </nav>
    );
}
