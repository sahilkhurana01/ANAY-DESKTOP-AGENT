import { motion } from 'framer-motion';
import { LayoutDashboard, Users, FileText, Link, Phone, DollarSign } from 'lucide-react';

interface NavigationBarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isOnline: boolean;
}

const NavigationBar = ({ activeTab, onTabChange, isOnline }: NavigationBarProps) => {
  const tabs = [
    { id: 'dashboard', label: 'DASHBOARD', icon: LayoutDashboard },
    { id: 'contacts', label: 'CONTACTS', icon: Users },
    { id: 'notes', label: 'NOTES', icon: FileText },
    { id: 'connect', label: 'CONNECT', icon: Link },
    { id: 'pricing', label: 'PRICING', icon: DollarSign },
  ];

  const statusItems = [
    { label: 'SYSTEM READY', active: true },
    { label: 'NET LINKED', active: isOnline },
    { label: 'LISTENING', active: false },
  ];

  return (
    <nav className="px-1 flex items-center justify-between overflow-x-auto custom-scrollbar">
      {/* Left - Navigation Tabs */}
      <div className="flex items-center gap-2 flex-shrink-0">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;

          return (
            <motion.button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`anay-nav-item flex items-center gap-2 py-1.5 px-3 md:px-4 ${isActive ? 'anay-nav-item-active' : ''
                }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="font-orbitron text-[10px] md:text-xs tracking-wider">
                {tab.label}
              </span>
            </motion.button>
          );
        })}
      </div>

      {/* Center - ANAY Branding */}
      <div className="flex items-center gap-3 px-4 rounded-xl">
        <div className="relative">
          <span className="text-sm md:text-xl font-orbitron font-black tracking-tighter text-cyan-400">
            ANAY
          </span>
          {isOnline && (
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="absolute -top-1 -right-4 flex items-center"
            >
              <div className="flex h-2 w-2 relative">
                <div className="animate-ping absolute inline-flex h-full w-full rounded-full bg-anay-green opacity-75"></div>
                <div className="relative inline-flex rounded-full h-2 w-2 bg-anay-green"></div>
              </div>
              <span className="ml-1 text-[7px] font-bold font-orbitron text-anay-green tracking-tighter">LIVE</span>
            </motion.div>
          )}
        </div>
        <div className="h-4 w-[1px] bg-white/10 hidden md:block" />
        <span className="text-[10px] md:text-xs font-light text-white tracking-[0.2em] hidden md:block uppercase opacity-50">
          Personal Assistant v2.0
        </span>
      </div>

      {/* Right - Status Indicators */}
      <div className="hidden lg:flex items-center gap-6 flex-shrink-0 opacity-80">
        <div className="flex flex-col items-end gap-0.5">
          <div className="flex items-center gap-2">
            <span className="text-[8px] text-foreground/40 font-orbitron uppercase tracking-widest">CONNECTIVITY</span>
            <div className={`h-1 w-8 rounded-full ${isOnline ? 'bg-anay-green/40' : 'bg-red-500/20'}`}>
              <motion.div
                className={`h-full rounded-full ${isOnline ? 'bg-anay-green' : 'bg-red-500'}`}
                animate={{ width: isOnline ? '100%' : '20%' }}
              />
            </div>
          </div>
          <span className={`text-[7px] font-orbitron font-bold tracking-[0.2em] ${isOnline ? 'text-anay-green' : 'text-red-500'}`}>
            {isOnline ? 'DATA LINK SECURE' : 'LINK OFFLINE'}
          </span>
        </div>

        {statusItems.map((item) => (
          <div
            key={item.label}
            className="flex items-center gap-2"
          >
            <span className="text-[9px] text-foreground/60 font-orbitron uppercase tracking-wider">
              {item.label}
            </span>
            <span className={`text-[10px] ${item.active ? 'text-anay-green' : 'text-muted-foreground'}`}>
              {item.active ? '🛰️' : '🔘'}
            </span>
          </div>
        ))}
      </div>
    </nav>
  );
};

export default NavigationBar;
