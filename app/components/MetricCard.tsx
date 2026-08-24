interface MetricCardProps {
  title: string;
  value: string;
  unit: string;
  status?: string;
}

export default function MetricCard({ title, value, unit, status }: MetricCardProps) {
  return (
    <div className="flex flex-col justify-between p-6 rounded-2xl 
                    bg-white/5 backdrop-blur-lg border border-white/10 
                    transition-all duration-300 hover:shadow-glow-hover hover:border-electricBlue/50">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wider">
          {title}
        </h3>
        {status && (
          <span className="px-2 py-1 text-xs rounded-full bg-electricBlue/10 text-electricBlue border border-electricBlue/30">
            {status}
          </span>
        )}
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-4xl font-bold text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.5)]">
          {value}
        </span>
        <span className="text-electricBlue font-semibold">
          {unit}
        </span>
      </div>
    </div>
  );
}