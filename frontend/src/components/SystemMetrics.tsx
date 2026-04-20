import { ReactNode, useEffect, useState } from "react";
import { Cpu, HardDrive, Mic, ShieldCheck } from "lucide-react";

import { api, DesktopState } from "@/lib/api";

interface SystemMetricsProps {
  isOnline?: boolean;
}

const SystemMetrics = ({ isOnline = true }: SystemMetricsProps) => {
  const [state, setState] = useState<DesktopState | null>(null);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const data = await api.getDesktopState();
        if (mounted) setState(data);
      } catch (error) {
        console.error(error);
      }
    };

    load();
    const timer = window.setInterval(load, 5000);
    return () => {
      mounted = false;
      window.clearInterval(timer);
    };
  }, []);

  const system = state?.system;

  return (
    <div className="anay-panel h-full p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-orbitron text-xs tracking-[0.35em] text-primary uppercase">System Core</p>
          <h2 className="text-2xl font-orbitron font-black text-white">Local Telemetry</h2>
        </div>
        <div className={`px-3 py-1 rounded-full text-[11px] tracking-[0.22em] uppercase font-orbitron border ${isOnline ? "border-emerald-400/20 bg-emerald-500/10 text-emerald-200" : "border-red-400/20 bg-red-500/10 text-red-200"}`}>
          {isOnline ? "LOCAL ONLINE" : "OFFLINE"}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <MetricCard icon={<Cpu className="w-4 h-4" />} label="CPU" value={`${system?.cpu_percent?.toFixed(0) ?? "--"}%`} />
        <MetricCard icon={<HardDrive className="w-4 h-4" />} label="Disk" value={`${system?.disk_percent?.toFixed(0) ?? "--"}%`} />
        <MetricCard icon={<ShieldCheck className="w-4 h-4" />} label="RAM" value={`${system?.ram_percent?.toFixed(0) ?? "--"}%`} />
        <MetricCard
          icon={<Mic className="w-4 h-4" />}
          label="Battery"
          value={
            system?.battery_percent != null
              ? `${system.battery_percent}%`
              : typeof system?.battery === "number"
                ? `${system.battery}%`
                : "N/A"
          }
        />
      </div>

      <div className="rounded-[1.4rem] border border-white/10 bg-black/20 p-4 space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-white/60">Voice stack</span>
          <span className="text-white">{state?.voice.mode ?? "push_to_talk"}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-white/60">Wake word</span>
          <span className={state?.wake_word.enabled ? "text-emerald-300" : "text-amber-300"}>
            {state?.wake_word.enabled ? state?.wake_word.wake_phrase : "Pending setup"}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-white/60">Host</span>
          <span className="text-white truncate max-w-[60%] text-right">{system?.hostname ?? "--"}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-white/60">Platform</span>
          <span className="text-white truncate max-w-[60%] text-right">{system?.platform ?? "--"}</span>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ icon, label, value }: { icon: ReactNode; label: string; value: string }) => (
  <div className="anay-metric-card">
    <div className="flex items-center justify-between text-white/55">
      {icon}
      <span className="font-orbitron text-[10px] tracking-[0.25em] uppercase">{label}</span>
    </div>
    <div className="mt-4 text-3xl font-orbitron font-black text-white">{value}</div>
  </div>
);

export default SystemMetrics;
