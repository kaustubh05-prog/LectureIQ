const TYPE = {
    youtube: { icon: "▶", label: "YouTube", color: "#FF4560", bg: "rgba(255,69,96,0.08)" },
    documentation: { icon: "📄", label: "Documentation", color: "#00D4FF", bg: "rgba(0,212,255,0.08)" },
    practice: { icon: "💻", label: "Practice", color: "#00FF87", bg: "rgba(0,255,135,0.08)" },
};

export default function ResourceList({ resources }) {
    if (!resources?.length)
        return <p className="text-center text-gray-600 py-16">No resources found for this lecture.</p>;

    const grouped = resources.reduce((acc, r) => {
        const k = r.type || "other";
        (acc[k] = acc[k] || []).push(r);
        return acc;
    }, {});

    return (
        <div className="py-4 space-y-8">
            {Object.entries(grouped).map(([type, items]) => {
                const t = TYPE[type] || { icon: "🔗", label: type, color: "#8B5CF6", bg: "rgba(139,92,246,0.08)" };
                return (
                    <div key={type}>
                        <h3 className="text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2"
                            style={{ color: t.color }}>
                            {t.icon} {t.label}
                        </h3>
                        <div className="space-y-3">
                            {items.map((res) => (
                                <a key={res.id} href={res.url} target="_blank" rel="noopener noreferrer"
                                    className="flex items-start gap-4 p-4 rounded-2xl border border-dark-border transition-all duration-200 hover:scale-[1.01] group"
                                    style={{ background: t.bg }}>
                                    {res.thumbnail_url ? (
                                        <img src={res.thumbnail_url} alt="" className="w-28 h-16 object-cover rounded-xl shrink-0" />
                                    ) : (
                                        <div className="w-12 h-12 rounded-xl flex items-center justify-center text-xl shrink-0"
                                            style={{ background: t.bg, color: t.color, border: `1px solid ${t.color}30` }}>
                                            {t.icon}
                                        </div>
                                    )}
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-gray-200 line-clamp-2 leading-snug group-hover:text-white transition-colors">
                                            {res.title}
                                        </p>
                                        {res.topic && (
                                            <span className="nbadge mt-1.5 text-xs" style={{ background: `${t.color}15`, color: t.color }}>
                                                {res.topic}
                                            </span>
                                        )}
                                        <p className="text-xs text-gray-700 mt-1 truncate">{res.url}</p>
                                    </div>
                                    <svg className="w-4 h-4 text-gray-700 group-hover:text-neon-cyan shrink-0 mt-1 transition-colors"
                                        fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                            d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                    </svg>
                                </a>
                            ))}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
