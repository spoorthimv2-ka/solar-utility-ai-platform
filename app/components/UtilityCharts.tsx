'use client';

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, AreaChart, Area, Cell } from 'recharts';

export function PowerBarChart({ data }: { data?: any[] }) {
  let chartData = [];
  let stats = { avg: 0, highest: 0, lowest: 0, highestDate: '-', lowestDate: '-' };

  if (data && data.length > 0) {
    const row = data[0];
    chartData = Object.keys(row)
      .filter(key => key.includes('/2026') || key.includes('/2025'))
      .map(date => {
        const val = parseFloat(String(row[date]).replace(/,/g, '')) || 0;
        return { name: date, kW: val };
      });

    const activeValues = chartData.filter(d => d.kW > 0);
    if (activeValues.length > 0) {
      const values = activeValues.map(d => d.kW);
      const sum = values.reduce((acc, curr) => acc + curr, 0);
      stats.avg = Math.round(sum / values.length);
      
      const maxObj = activeValues.reduce((max, curr) => curr.kW > max.kW ? curr : max, activeValues[0]);
      const minObj = activeValues.reduce((min, curr) => curr.kW < min.kW ? curr : min, activeValues[0]);

      stats.highest = maxObj.kW;
      stats.highestDate = maxObj.name;
      stats.lowest = minObj.kW;
      stats.lowestDate = minObj.name;
    }
  } else {
    chartData = [{ name: 'Mon', kW: 400 }, { name: 'Tue', kW: 300 }, { name: 'Wed', kW: 600 }];
    stats = { avg: 433, highest: 600, lowest: 300, highestDate: 'Wed', lowestDate: 'Tue' };
  }

  return (
    <div>
      <div className="grid grid-cols-3 gap-2 mb-4 p-3 rounded-xl bg-black/40 border border-white/10 text-center">
        <div>
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Average</div>
          <div className="text-sm font-bold text-electricBlue">{stats.avg.toLocaleString()} <span className="text-[10px] font-normal">kW</span></div>
        </div>
        <div className="border-x border-white/10">
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Highest</div>
          <div className="text-sm font-bold text-emerald-400">{stats.highest.toLocaleString()} <span className="text-[10px] font-normal">kW</span></div>
          <div className="text-[9px] text-gray-500">{stats.highestDate}</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Lowest</div>
          <div className="text-sm font-bold text-purple-400">{stats.lowest.toLocaleString()} <span className="text-[10px] font-normal">kW</span></div>
          <div className="text-[9px] text-gray-500">{stats.lowestDate}</div>
        </div>
      </div>

      <div className="flex justify-between text-xs text-gray-400 mb-2">
        <span>X-Axis: Date</span>
        <span>Y-Axis: Daily Consumption</span>
      </div>
      <ResponsiveContainer width="100%" height={170}>
        <BarChart data={chartData}>
          <XAxis dataKey="name" stroke="#6b7280" fontSize={10} />
          <YAxis stroke="#6b7280" fontSize={10} />
          <Tooltip contentStyle={{ backgroundColor: '#0a0a0a', borderColor: '#ffffff20', borderRadius: '0.75rem', color: '#fff' }} />
          <Bar dataKey="kW" fill="#00f0ff" radius={[4, 4, 0, 0]} name="Consumption" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function AirQualityPieChart({ data }: { data?: any[] }) {
  let chartData = [];
  let stats = { avg: 0, highest: 0, lowest: 0, highestDate: '-', lowestDate: '-' };

  if (data && data.length > 2) {
    const row = data[2];
    chartData = Object.keys(row)
      .filter(key => key.includes('/2026') || key.includes('/2025'))
      .map(date => {
        const val = parseFloat(String(row[date]).replace(/,/g, '')) || 0;
        return { name: date, value: val };
      });

    const activeValues = chartData.filter(d => d.value > 0);
    if (activeValues.length > 0) {
      const values = activeValues.map(d => d.value);
      const sum = values.reduce((acc, curr) => acc + curr, 0);
      stats.avg = Math.round(sum / values.length);

      const maxObj = activeValues.reduce((max, curr) => curr.value > max.value ? curr : max, activeValues[0]);
      const minObj = activeValues.reduce((min, curr) => curr.value < min.value ? curr : min, activeValues[0]);

      stats.highest = maxObj.value;
      stats.highestDate = maxObj.name;
      stats.lowest = minObj.value;
      stats.lowestDate = minObj.name;
    }
  } else {
    chartData = [{ name: '1/8/2026', value: 70 }, { name: '2/8/2026', value: 30 }];
    stats = { avg: 50, highest: 70, lowest: 30, highestDate: '1/8/2026', lowestDate: '2/8/2026' };
  }

  return (
    <div>
      <div className="grid grid-cols-3 gap-2 mb-4 p-3 rounded-xl bg-black/40 border border-white/10 text-center">
        <div>
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Average</div>
          <div className="text-sm font-bold text-electricBlue">{stats.avg.toLocaleString()}</div>
        </div>
        <div className="border-x border-white/10">
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Highest</div>
          <div className="text-sm font-bold text-emerald-400">{stats.highest.toLocaleString()}</div>
          <div className="text-[9px] text-gray-500">{stats.highestDate}</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Lowest</div>
          <div className="text-sm font-bold text-purple-400">{stats.lowest.toLocaleString()}</div>
          <div className="text-[9px] text-gray-500">{stats.lowestDate}</div>
        </div>
      </div>

      <div className="flex justify-between text-xs text-gray-400 mb-2">
        <span>X-Axis: Date</span>
        <span>Y-Axis: Metric Value</span>
      </div>
      <ResponsiveContainer width="100%" height={170}>
        <AreaChart data={chartData}>
          <XAxis dataKey="name" stroke="#6b7280" fontSize={10} />
          <YAxis stroke="#6b7280" fontSize={10} />
          <Tooltip contentStyle={{ backgroundColor: '#0a0a0a', borderColor: '#ffffff20', borderRadius: '0.75rem', color: '#fff' }} />
          <Area type="monotone" dataKey="value" stroke="#00f0ff" fill="#00f0ff" fillOpacity={0.2} name="Value" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PressureAreaChart({ data }: { data?: any[] }) {
  let chartData = [];
  let stats = { avg: 0, highest: 0, lowest: 0, highestDate: '-', lowestDate: '-' };

  if (data && data.length > 1) {
    const row = data[1];
    chartData = Object.keys(row)
      .filter(key => key.includes('/2026') || key.includes('/2025'))
      .map(date => {
        const val = parseFloat(String(row[date]).replace(/,/g, '')) / 10000 || 0;
        return { name: date, bar: parseFloat(val.toFixed(2)) };
      });

    const activeValues = chartData.filter(d => d.bar > 0);
    if (activeValues.length > 0) {
      const values = activeValues.map(d => d.bar);
      const sum = values.reduce((acc, curr) => acc + curr, 0);
      stats.avg = parseFloat((sum / values.length).toFixed(2));

      const maxObj = activeValues.reduce((max, curr) => curr.bar > max.bar ? curr : max, activeValues[0]);
      const minObj = activeValues.reduce((min, curr) => curr.bar < min.bar ? curr : min, activeValues[0]);

      stats.highest = maxObj.bar;
      stats.highestDate = maxObj.name;
      stats.lowest = minObj.bar;
      stats.lowestDate = minObj.name;
    }
  } else {
    chartData = [{ name: '00:00', bar: 6.1 }, { name: '06:00', bar: 6.4 }, { name: '12:00', bar: 6.8 }];
    stats = { avg: 6.43, highest: 6.8, lowest: 6.1, highestDate: '12:00', lowestDate: '00:00' };
  }

  return (
    <div>
      <div className="grid grid-cols-3 gap-2 mb-4 p-3 rounded-xl bg-black/40 border border-white/10 text-center">
        <div>
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Average</div>
          <div className="text-sm font-bold text-electricBlue">{stats.avg} <span className="text-[10px] font-normal">bar</span></div>
        </div>
        <div className="border-x border-white/10">
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Highest</div>
          <div className="text-sm font-bold text-emerald-400">{stats.highest} <span className="text-[10px] font-normal">bar</span></div>
          <div className="text-[9px] text-gray-500">{stats.highestDate}</div>
        </div>
        <div>
          <div className="text-[10px] text-gray-400 uppercase tracking-wider">Lowest</div>
          <div className="text-sm font-bold text-purple-400">{stats.lowest} <span className="text-[10px] font-normal">bar</span></div>
          <div className="text-[9px] text-gray-500">{stats.lowestDate}</div>
        </div>
      </div>

      <div className="flex justify-between text-xs text-gray-400 mb-2">
        <span>X-Axis: Date</span>
        <span>Y-Axis: Scaled Variance</span>
      </div>
      <ResponsiveContainer width="100%" height={170}>
        <AreaChart data={chartData}>
          <XAxis dataKey="name" stroke="#6b7280" fontSize={10} />
          <YAxis stroke="#6b7280" fontSize={10} />
          <Tooltip contentStyle={{ backgroundColor: '#0a0a0a', borderColor: '#ffffff20', borderRadius: '0.75rem', color: '#fff' }} />
          <Area type="monotone" dataKey="bar" stroke="#a855f7" fill="#a855f7" fillOpacity={0.3} name="Variance" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}