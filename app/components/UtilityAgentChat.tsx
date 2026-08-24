'use client';

import { useState } from 'react';

export function UtilityAgentChat({ data }: { data?: any[] }) {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'agent'; text: string }>>([
    { role: 'agent', text: "Hey! I'm your Utility Data Assistant. Ask me anything about power trends, peaks, air quality, or future predictions." }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userQuery = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userQuery }]);
    setLoading(true);

    try {
      const res = await fetch('/api/utility-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userQuery, data })
      });
      const json = await res.json();
      setMessages(prev => [...prev, { role: 'agent', text: json.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'agent', text: "Error connecting to the analytical agent." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl bg-black/40 border border-white/10 p-4 flex flex-col h-[350px]">
      <div className="text-xs font-semibold text-electricBlue uppercase tracking-wider mb-3">AI Utility & Predictive Agent</div>
      
      {/* Chat Messages Log */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-2 text-xs">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-xl ${m.role === 'user' ? 'bg-electricBlue/20 text-white border border-electricBlue/30' : 'bg-white/5 text-gray-300 border border-white/10'}`}>
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white/5 text-gray-400 p-3 rounded-xl animate-pulse">Analyzing dataset patterns...</div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="mt-3 flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask e.g. Which date had the highest power?"
          className="flex-1 bg-black/60 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-electricBlue"
        />
        <button 
          type="submit" 
          disabled={loading}
          className="bg-electricBlue text-black font-semibold px-4 py-2 rounded-xl text-xs hover:opacity-90 transition"
        >
          Ask
        </button>
      </form>
    </div>
  );
}