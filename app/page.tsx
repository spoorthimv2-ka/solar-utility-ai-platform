'use client';

import { useState } from 'react';
import { Menu } from 'lucide-react';
import MetricCard from './components/MetricCard';
import ComparisonChart from './components/ComparisonChart';
import { PowerBarChart, AirQualityPieChart, PressureAreaChart } from './components/UtilityCharts';
import Sidebar from './components/Sidebar';
import DataUpload from './components/DataUpload';
import { UtilityAgentChat } from '@/app/components/UtilityAgentChat';

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [telemetryData, setTelemetryData] = useState<any[]>([]);

  return (
    <div className="flex min-h-screen bg-[#0a0a0a] text-white">
      <Sidebar 
        isOpen={sidebarOpen} 
        setIsOpen={setSidebarOpen} 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
      />

      <main className="flex-1 p-8 lg:p-12 overflow-y-auto">
        <header className="mb-8 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setSidebarOpen(true)}
              className="p-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 hover:text-white hover:bg-white/10 transition cursor-pointer"
              aria-label="Open Menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-white/90">
                Automato Dashboard
              </h1>
              <p className="text-gray-400 mt-1">Live manufacturing telemetry & utility monitoring</p>
            </div>
          </div>
          <div className="px-4 py-2 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md text-sm text-electricBlue flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-electricBlue animate-pulse"></span>
            System Online {telemetryData.length > 0 && `(${telemetryData.length} records active)`}
          </div>
        </header>

        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <MetricCard title="Power Consumption" value="452.8" unit="kW" status="Optimal" />
              <MetricCard title="Air Quality" value="98" unit="AQI" status="Normal" />
              <MetricCard title="Flow Rate" value="1,240" unit="L/min" status="Stable" />
              <MetricCard title="System Pressure" value="6.4" unit="bar" status="Nominal" />
              <MetricCard title="Humidity" value="42" unit="%" status="Normal" />
              <MetricCard title="Temperature" value="24.5" unit="°C" status="Warning" />
            </div>

            <div className="p-6 rounded-2xl bg-white/5 backdrop-blur-lg border border-white/10">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-white">Unit-1 vs Unit-5 Comparative Analytics</h3>
                <span className="text-xs text-gray-400">Real-time Batch Stream</span>
              </div>
              <ComparisonChart />
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-white/90">Utility Breakdown Analytics Hub</h2>
              <span className="text-xs text-electricBlue px-3 py-1 rounded-lg bg-white/5 border border-white/10">
                {telemetryData.length > 0 ? 'Source: Uploaded CSV File' : 'Source: Default Fallback Stream'}
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="p-6 rounded-2xl bg-white/5 backdrop-blur-lg border border-white/10">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-sm font-semibold text-gray-200 uppercase tracking-wider">Power Trend</h3>
                  <span className="text-[10px] bg-electricBlue/10 text-electricBlue px-2 py-0.5 rounded border border-electricBlue/20">Dynamic</span>
                </div>
                <PowerBarChart data={telemetryData} />
              </div>

              <div className="p-6 rounded-2xl bg-white/5 backdrop-blur-lg border border-white/10">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-sm font-semibold text-gray-200 uppercase tracking-wider">Air Quality Ratio</h3>
                  <span className="text-[10px] bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded border border-purple-500/20">Dynamic</span>
                </div>
                <AirQualityPieChart data={telemetryData} />
              </div>

              <div className="p-6 rounded-2xl bg-white/5 backdrop-blur-lg border border-white/10">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-sm font-semibold text-gray-200 uppercase tracking-wider">Pressure Variance</h3>
                  <span className="text-[10px] bg-electricBlue/10 text-electricBlue px-2 py-0.5 rounded border border-electricBlue/20">Dynamic</span>
                </div>
                <PressureAreaChart data={telemetryData} />
              </div>
            </div>

            {/* AI Predictive Agent Chat Widget added here */}
            <div className="mt-6">
              <UtilityAgentChat data={telemetryData} />
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="p-8 rounded-2xl bg-white/5 border border-white/10 max-w-2xl">
            <h2 className="text-2xl font-bold mb-4 text-white">System Settings & Data Sync</h2>
            <p className="text-gray-400 mb-6 text-sm">Upload your latest Excel/CSV telemetry reports to update active chart metrics.</p>
            
            <DataUpload onDataLoaded={(data) => setTelemetryData(data)} />

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-300 mb-2">Telemetry Refresh Rate</label>
                <select className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm outline-none">
                  <option className="bg-black text-white">Every 3 seconds</option>
                  <option className="bg-black text-white">Every 5 seconds</option>
                  <option className="bg-black text-white">Real-time (WebSockets)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-2">Active Node Region</label>
                <input type="text" defaultValue="Industrial Sector - Unit 1 & 5" className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white text-sm outline-none" />
              </div>
              <button onClick={() => alert('Settings saved successfully!')} className="px-6 py-3 rounded-xl bg-electricBlue text-black font-semibold text-sm cursor-pointer hover:opacity-90 transition">
                Save Changes
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}