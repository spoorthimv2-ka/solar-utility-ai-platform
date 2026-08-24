'use client';

import { LayoutDashboard, BarChart3, Settings, LogOut, Power, X } from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function Sidebar({ isOpen, setIsOpen, activeTab, setActiveTab }: SidebarProps) {
  const handleLogout = () => {
    alert('Logged out successfully. Redirecting to login...');
  };

  const handleExitApp = () => {
    const confirmExit = window.confirm('Are you sure you want to exit the Automato system?');
    if (confirmExit) {
      window.location.href = 'about:blank';
    }
  };

  return (
    <>
      {isOpen && (
        <div 
          onClick={() => setIsOpen(false)} 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
        />
      )}

      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#0a0a0a]/95 border-r border-white/10 p-6 flex flex-col justify-between backdrop-blur-md transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0 md:static'
      }`}>
        <div>
          <div className="flex items-center justify-between mb-10">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-electricBlue/20 border border-electricBlue flex items-center justify-center text-electricBlue font-bold">
                A
              </div>
              <span className="text-xl font-bold tracking-tight text-white">Automato</span>
            </div>
            <button 
              onClick={() => setIsOpen(false)} 
              className="md:hidden text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <nav className="space-y-2">
            <button 
              onClick={() => { setActiveTab('dashboard'); setIsOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition cursor-pointer ${
                activeTab === 'dashboard' 
                  ? 'bg-electricBlue/10 text-electricBlue border border-electricBlue/20' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </button>

            <button 
              onClick={() => { setActiveTab('analytics'); setIsOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition cursor-pointer ${
                activeTab === 'analytics' 
                  ? 'bg-electricBlue/10 text-electricBlue border border-electricBlue/20' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              Analytics Hub
            </button>

            <button 
              onClick={() => { setActiveTab('settings'); setIsOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition cursor-pointer ${
                activeTab === 'settings' 
                  ? 'bg-electricBlue/10 text-electricBlue border border-electricBlue/20' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Settings className="w-4 h-4" />
              Settings
            </button>
          </nav>
        </div>

        <div className="space-y-2 pt-6 border-t border-white/10">
          <button 
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition text-sm text-left cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            Log Out
          </button>
          <button 
            onClick={handleExitApp}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition text-sm text-left cursor-pointer"
          >
            <Power className="w-4 h-4" />
            Exit App
          </button>
        </div>
      </aside>
    </>
  );
}