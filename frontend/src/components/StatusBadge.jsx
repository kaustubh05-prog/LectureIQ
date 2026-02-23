const STYLES = {
    uploading: { dot: "#00D4FF", bg: "rgba(0,212,255,0.1)", text: "#00D4FF", label: "Uploading", pulse: true },
    processing: { dot: "#FFBB00", bg: "rgba(255,187,0,0.1)", text: "#FFBB00", label: "Processing", pulse: true },
    completed: { dot: "#00FF87", bg: "rgba(0,255,135,0.1)", text: "#00FF87", label: "Ready", pulse: false },
    failed: { dot: "#FF4560", bg: "rgba(255,69,96,0.1)", text: "#FF4560", label: "Failed", pulse: false },
};

export default function StatusBadge({ status }) {
    const s = STYLES[status?.toLowerCase()] || STYLES.processing;
    return (
        <span className="nbadge" style={{ background: s.bg, color: s.text }}>
            <span className={`w-1.5 h-1.5 rounded-full inline-block ${s.pulse ? "animate-pulse" : ""}`}
                style={{ background: s.dot }} />
            {s.label}
        </span>
    );
}
