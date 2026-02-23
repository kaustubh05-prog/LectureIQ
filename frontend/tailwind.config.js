/** @type {import('tailwindcss').Config} */
export default {
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
        extend: {
            colors: {
                neon: {
                    cyan: "#00D4FF",
                    purple: "#8B5CF6",
                    green: "#00FF87",
                    pink: "#FF0080",
                },
                dark: {
                    bg: "#07070f",
                    surface: "#0d0d1a",
                    card: "#111124",
                    border: "#1e1e38",
                    hover: "#181830",
                },
            },
            boxShadow: {
                "neon-cyan": "0 0 20px rgba(0,212,255,0.35), 0 0 60px rgba(0,212,255,0.1)",
                "neon-purple": "0 0 20px rgba(139,92,246,0.35), 0 0 60px rgba(139,92,246,0.1)",
                "neon-green": "0 0 20px rgba(0,255,135,0.35)",
                "neon-sm": "0 0 10px rgba(0,212,255,0.2)",
                "glass": "0 8px 32px rgba(0,0,0,0.4)",
            },
            backgroundImage: {
                "gradient-hero": "radial-gradient(ellipse at 60% 0%, rgba(139,92,246,0.15) 0%, transparent 60%), radial-gradient(ellipse at 0% 80%, rgba(0,212,255,0.1) 0%, transparent 60%)",
                "gradient-neon": "linear-gradient(135deg, #00D4FF 0%, #8B5CF6 100%)",
                "gradient-card": "linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(139,92,246,0.06) 100%)",
                "gradient-text": "linear-gradient(135deg, #00D4FF 0%, #8B5CF6 50%, #FF0080 100%)",
            },
            animation: {
                "float": "float 6s ease-in-out infinite",
                "glow-pulse": "glowpulse 2.5s ease-in-out infinite alternate",
                "slide-up": "slideup 0.4s ease-out",
                "fade-in": "fadein 0.3s ease-out",
            },
            keyframes: {
                float: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-12px)" } },
                glowpulse: { from: { opacity: "0.6" }, to: { opacity: "1" } },
                slideup: { from: { transform: "translateY(16px)", opacity: "0" }, to: { transform: "translateY(0)", opacity: "1" } },
                fadein: { from: { opacity: "0" }, to: { opacity: "1" } },
            },
        },
    },
    plugins: [require("@tailwindcss/typography")],
};
