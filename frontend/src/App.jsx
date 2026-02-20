import { Routes, Route, Navigate } from "react-router-dom";
import useAuthStore from "./store/useAuthStore";

// Pages (stubs for now — Phase 2 fills these)
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import DashboardPage from "./pages/DashboardPage";
import UploadPage from "./pages/UploadPage";
import LectureDetailPage from "./pages/LectureDetailPage";

function PrivateRoute({ children }) {
    const token = useAuthStore((s) => s.token);
    return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
    return (
        <Routes>
            {/* Public */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />

            {/* Protected */}
            <Route
                path="/dashboard"
                element={<PrivateRoute><DashboardPage /></PrivateRoute>}
            />
            <Route
                path="/upload"
                element={<PrivateRoute><UploadPage /></PrivateRoute>}
            />
            <Route
                path="/lectures/:id"
                element={<PrivateRoute><LectureDetailPage /></PrivateRoute>}
            />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}
