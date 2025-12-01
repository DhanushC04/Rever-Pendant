import React, { useEffect, useRef } from 'react';
import { Activity } from 'lucide-react';

const SystemLogs = ({ logs }) => {
  const logsEndRef = useRef(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getLogColor = (type) => {
    switch (type) {
      case 'success': return 'text-white';
      case 'error': return 'text-white';
      case 'warning': return 'text-white';
      default: return 'text-white';
    }
  };

  return (
    <div className="bg-slate-900 rounded-2xl p-6 border border-white shadow-xl">
      <div className="flex items-center gap-3 mb-4">
        <Activity className="w-6 h-6 text-white" />
        <h3 className="text-xl font-bold text-white">System Logs</h3>
        {logs.length > 0 && (
          <span className="ml-auto text-sm bg-blue-900 text-white px-3 py-1 rounded-full border border-white">
            {logs.length} entries
          </span>
        )}
      </div>
      <div className="bg-slate-950 rounded-xl p-4 max-h-[300px] overflow-y-auto font-mono text-sm">
        {logs.length > 0 ? (
          <>
            {logs.map((log, idx) => (
              <div key={idx} className={`mb-2 animate-fade-in ${getLogColor(log.type)}`}>
                <span className="text-white/60">[{log.timestamp}]</span> {log.message}
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