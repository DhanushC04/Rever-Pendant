import React, { useEffect, useRef } from 'react';
import { Activity } from 'lucide-react';

const SystemLogs = ({ logs }) => {
  const logsEndRef = useRef(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getLogColor = (type) => {
    switch (type) {
      case 'success': return 'text-green-300';
      case 'error': return 'text-red-300';
      case 'warning': return 'text-yellow-300';
      default: return 'text-blue-300';
    }
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
      <div className="flex items-center gap-3 mb-4">
        <Activity className="w-6 h-6 text-green-400" />
        <h3 className="text-xl font-bold text-white">System Logs</h3>
        {logs.length > 0 && (
          <span className="ml-auto text-sm bg-green-500/20 text-green-300 px-3 py-1 rounded-full border border-green-400/30">
            {logs.length} entries
          </span>
        )}
      </div>
      <div className="bg-black/30 rounded-xl p-4 max-h-[300px] overflow-y-auto font-mono text-sm">
        {logs.length > 0 ? (
          <>
            {logs.map((log, idx) => (
              <div key={idx} className={`mb-2 animate-fade-in ${getLogColor(log.type)}`}>
                <span className="text-gray-400">[{log.timestamp}]</span> {log.message}
              </div>
            ))}
            <div ref={logsEndRef} />
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-32 text-gray-500">
            <Activity className="w-10 h-10 mb-2 opacity-30" />
            <p className="italic">System logs will appear here...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemLogs;