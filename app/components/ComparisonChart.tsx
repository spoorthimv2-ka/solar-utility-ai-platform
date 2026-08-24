'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const data = [
  { time: '00:00', unit1: 420, unit5: 390 },
  { time: '04:00', unit1: 380, unit5: 410 },
  { time: '08:00', unit1: 520, unit5: 480 },
  { time: '12:00', unit1: 610, unit5: 590 },
  { time: '16:00', unit1: 550, unit5: 530 },
  { time: '20:00', unit1: 470, unit5: 440 },
  { time: '24:00', unit1: 430, unit5: 410 },
];

export default function ComparisonChart() {
  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
          <XAxis dataKey="time" stroke="#9ca3af" textStyle={{ fontSize: '12px' }} />
          <YAxis stroke="#9ca3af" textStyle={{ fontSize: '12px' }} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0a0a0a', borderColor: '#ffffff20', borderRadius: '0.75rem', color: '#fff' }} 
          />
          <Legend />
          <Line type="monotone" dataKey="unit1" name="Unit-1 (kW)" stroke="#00f0ff" strokeWidth={3} dot={{ r: 4, fill: '#00f0ff' }} activeDot={{ r: 8 }} />
          <Line type="monotone" dataKey="unit5" name="Unit-5 (kW)" stroke="#a855f7" strokeWidth={3} dot={{ r: 4, fill: '#a855f7' }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}