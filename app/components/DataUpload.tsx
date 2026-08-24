'use client';

import { useState } from 'react';
import Papa from 'papaparse';

interface DataUploadProps {
  onDataLoaded: (data: any[]) => void;
}

export default function DataUpload({ onDataLoaded }: DataUploadProps) {
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        onDataLoaded(results.data);
        alert(`Successfully loaded ${results.data.length} rows from ${file.name}!`);
      },
      error: (error) => {
        console.error('Error parsing file:', error);
        alert('Failed to parse file. Ensure it is a valid CSV export.');
      }
    });
  };

  return (
    <div className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md mb-6">
      <h3 className="text-lg font-semibold text-white mb-2">Import Real Telemetry Data</h3>
      <p className="text-xs text-gray-400 mb-4">Upload your daily sensor export (CSV format from Excel) to update charts dynamically.</p>
      
      <label className="flex flex-col items-center justify-center border-2 border-dashed border-white/20 rounded-xl p-6 cursor-pointer hover:border-electricBlue transition bg-black/20">
        <span className="text-sm text-gray-300 font-medium">{fileName ? `Loaded: ${fileName}` : 'Click to browse or drop your CSV file here'}</span>
        <input type="file" accept=".csv" onChange={handleFileUpload} className="hidden" />
      </label>
    </div>
  );
}