import React, { useState, useEffect, useCallback } from 'react';
import { Play, Download, RefreshCw, Activity, AlertCircle, Loader2 } from 'lucide-react';
import StageCard from './StageCard';
import SystemLogs from './SystemLogs';
import { startProcess, getStatus, resetProcess, downloadResults, checkHealth } from '../services/api';

const Dashboard = () => {
  const [state, setState] = useState({
    stage: 'idle',
    person: '',
    transcript: '',
    summary: '',
    progress: 0,
    logs: [],
    error: '',
    is_processing: false
  });
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Check backend health
  const checkBackendHealth = useCallback(async () => {
    try {
      await checkHealth();
      setIsConnected(true);
    } catch (error) {
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 10000);
    return () => clearInterval(interval);
  }, [checkBackendHealth]);

  // Poll status when processing
  useEffect(() => {
    let pollInterval;
    
    if (state.is_processing || (state.stage !== 'idle' && state.stage !== 'complete')) {
      pollInterval = setInterval(async () => {
        try {
          const status = await getStatus();
          setState(status);
        } catch (error) {
          console.error('Failed to fetch status:', error);
        }
      }, 500);
    }

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [state.is_processing, state.stage]);

  const handleStart = async () => {
    setIsLoading(true);
    try {
      await startProcess();
      setState(prev => ({ ...prev, is_processing: true, stage: 'face' }));
    } catch (error) {
      console.error('Failed to start process:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to start process. Check if backend is running.',
        logs: [...prev.logs, {
          message: `❌ Error: ${error.message}`,
          type: 'error',
          timestamp: new Date().toLocaleTimeString()
        }]
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await resetProcess();
      setState({
        stage: 'idle',
        person: '',
        transcript: '',
        summary: '',
        progress: 0,
        logs: [],
        error: '',
        is_processing: false
      });
    } catch (error) {
      console.error('Failed to reset:', error);
    }
  };

  const handleDownload = async () => {
    try {
      await downloadResults();
    } catch (error) {
      console.error('Failed to download:', error);
      
      // Fallback: create file from current data
      const content = `Person: ${state.person}\nTranscript: ${state.transcript}\nSummary: ${state.summary}\n`;
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'final_output.txt';
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-5xl font-bold text-white mb-3 flex items-center justify-center gap-3">
            <Activity className="w-12 h-12 text-white animate-pulse-ring" />
            AI Pendant System
          </h1>
          <p className="text-white/70 text-lg">
            Real-time Face Recognition • Audio Transcription • AI Summarization
          </p>
          <div className="mt-4 inline-flex items-center gap-2 bg-slate-800 backdrop-blur px-4 py-2 rounded-full border border-white">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-white animate-pulse-ring' : 'bg-white/30'}`}></div>
            <span className="text-white text-sm">
              {isConnected ? 'Backend Connected' : 'Backend Offline'}
            </span>
          </div>
        </div>

        {/* Error Display */}
        {state.error && (
          <div className="bg-slate-800 border border-white rounded-xl p-4 mb-6 text-white flex items-center gap-3 animate-fade-in">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <div>
              <strong>Error:</strong> {state.error}
            </div>
          </div>
        )}

        {/* Main Control Panel */}
        <div className="bg-slate-900 rounded-2xl p-8 mb-6 border border-white shadow-2xl">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold text-white">Control Panel</h2>
              {state.is_processing && state.stage !== 'complete' && (
                <div className="flex items-center gap-2 bg-blue-900 border border-white px-4 py-2 rounded-lg">
                  <Loader2 className="w-4 h-4 text-white animate-spin" />
                  <span className="text-white text-sm font-medium">Processing...</span>
                </div>
              )}
            </div>

            <div className="flex gap-3">
              {state.stage === 'idle' && (
                <button
                  onClick={handleStart}
                  disabled={!isConnected || isLoading}
                  className="bg-blue-900 hover:bg-blue-800 text-white px-8 py-3 rounded-xl font-semibold flex items-center gap-2 transition-all transform hover:scale-105 shadow-lg border border-white disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Starting...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      Start Process
                    </>
                  )}
                </button>
              )}

              {state.stage === 'complete' && (
                <>
                  <button
                    onClick={handleDownload}
                    className="bg-blue-900 hover:bg-blue-800 text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-all shadow-lg hover:scale-105 border border-white"
                  >
                    <Download className="w-5 h-5" />
                    Download
                  </button>
                  <button
                    onClick={handleReset}
                    className="bg-slate-800 hover:bg-slate-700 text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-all shadow-lg hover:scale-105 border border-white"
                  >
                    <RefreshCw className="w-5 h-5" />
                    Reset
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Pipeline Stages */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <StageCard
              stage={state.stage}
              isActive={state.stage === 'face'}
              progress={state.progress}
              result={state.person}
              stageNumber={1}
            />
            <StageCard
              stage={state.stage}
              isActive={state.stage === 'audio'}
              progress={state.progress}
              result=""
              stageNumber={2}
            />
            <StageCard
              stage={state.stage}
              isActive={state.stage === 'summary'}
              progress={state.progress}
              result=""
              stageNumber={3}
            />
          </div>

          {/* Overall Progress */}
          {state.stage !== 'idle' && state.stage !== 'complete' && (
            <div className="bg-black/20 backdrop-blur rounded-xl p-4 border border-white/10 animate-fade-in">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">Overall Progress</span>
                <span className="text-white font-bold">
                  {state.stage === 'face' ? '33%' : state.stage === 'audio' ? '66%' : '99%'}
                </span>
              </div>
              <div className="bg-white/10 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 h-full transition-all duration-500"
                  style={{
                    width: state.stage === 'face' ? '33%' : state.stage === 'audio' ? '66%' : '99%'
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Results Display */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Transcript */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="w-6 h-6 text-blue-400" />
              <h3 className="text-xl font-bold text-white">Transcript</h3>
              {state.transcript && (
                <span className="ml-auto text-sm bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full border border-blue-400/30">
                  {state.transcript.split(' ').length} words
                </span>
              )}
            </div>
            <div className="bg-white/5 rounded-xl p-4 min-h-[180px] border border-white/10">
              {state.transcript ? (
                <p className="text-white leading-relaxed">{state.transcript}</p>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <Activity className="w-12 h-12 mb-3 opacity-30" />
                  <p className="italic">Transcript will appear here...</p>
                </div>
              )}
            </div>
          </div>

          {/* Summary */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-xl">
            <div className="flex items-center gap-3 mb-4">
              <Activity className="w-6 h-6 text-pink-400" />
              <h3 className="text-xl font-bold text-white">AI Summary</h3>
              {state.summary && (
                <span className="ml-auto text-sm bg-pink-500/20 text-pink-300 px-3 py-1 rounded-full border border-pink-400/30">
                  {state.summary.split(' ').length} words
                </span>
              )}
            </div>
            <div className="bg-white/5 rounded-xl p-4 min-h-[180px] border border-white/10">
              {state.summary ? (
                <p className="text-white leading-relaxed">{state.summary}</p>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <Activity className="w-12 h-12 mb-3 opacity-30" />
                  <p className="italic">Summary will appear here...</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* System Logs */}
        <SystemLogs logs={state.logs} />

        {/* Footer */}
        <div className="mt-8 text-center text-purple-200/60 text-sm">
          <p>Rever : AI Pendant System • Capstone Project</p>
          <p className="mt-1">Powered by Vosk, OpenCV & Facebook BART</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;