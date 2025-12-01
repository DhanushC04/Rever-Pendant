import React, { useEffect, useState } from 'react';

const AudioVisualizer = ({ isActive }) => {
  const [bars, setBars] = useState(Array(25).fill(0));

  useEffect(() => {
    if (!isActive) return;

    const interval = setInterval(() => {
      setBars(prev => prev.map((_, i) => 
        Math.abs(Math.sin((Date.now() * 0.01 + i * 10) * 0.1)) * 100
      ));
    }, 100);

    return () => clearInterval(interval);
  }, [isActive]);

  if (!isActive) return null;

  return (
    <div className="flex gap-1 items-end h-20 mb-3 bg-slate-950 rounded-lg p-2">
      {bars.map((height, i) => (
        <div
          key={i}
          className="flex-1 bg-white rounded-t transition-all duration-100"
          style={{ height: `${height}%` }}
        />
      ))}
    </div>
  );
};

export default AudioVisualizer;