function Sk({ className = "" }) {
    return <div className={`rounded-xl animate-pulse ${className}`}
        style={{ background: "rgba(255,255,255,0.06)" }} />;
}

export function LectureCardSkeleton() {
    return (
        <div className="glass p-5 space-y-3">
            <div className="flex justify-between">
                <Sk className="h-5 w-1/2" />
                <Sk className="h-5 w-16" />
            </div>
            <Sk className="h-4 w-1/3" />
            <Sk className="h-2 w-full" />
        </div>
    );
}

export function NotesSkeleton() {
    return (
        <div className="space-y-3 p-6">
            {[80, 55, 90, 40, 70, 60, 45].map((w, i) => (
                <Sk key={i} className="h-4" style={{ width: `${w}%` }} />
            ))}
        </div>
    );
}
