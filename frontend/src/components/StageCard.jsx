import React from 'react';
import { Camera, Mic, FileText, Loader2, CheckCircle } from 'lucide-react';
import AudioVisualizer from './AudioVisualizer';

const StageCard = ({ stage, isActive, progress, result, stageNumber }) => {
  const configs = {
    1: {
      icon: Camera,
      title: 'Face Recognition',
      color: 'blue',
      activeLabel: 'Scanning faces...',
      activeClasses: 'bg-blue-900 border-white',
      iconActiveClasses: 'text-white animate-pulse',
      progressClasses: 'bg-white',
      textClasses: 'text-white'
    },
    2: {
      icon: Mic,
      title: 'Audio Capture',
      color: 'blue',
      activeLabel: 'Recording audio...',
      activeClasses: 'bg-blue-900 border-white',
      iconActiveClasses: 'text-white animate-pulse',
      progressClasses: 'bg-white',
      textClasses: 'text-white'
    },
    3: {
      icon: FileText,
      title: 'AI Summary',
      color: 'blue',
      activeLabel: 'Generating...',
      activeClasses: 'bg-blue-900 border-white',
      iconActiveClasses: 'text-white animate-pulse',
      progressClasses: 'bg-white',
      textClasses: 'text-white'
    }
  };

  const config = configs[stageNumber];
  const Icon = config.icon;

  const getCardClass = () => {
    if (isActive) {
      return `p-6 rounded-xl border-2 ${config.activeClasses} scale-105 transition-all duration-300 shadow-xl`;
    }
    if (result && stageNumber === 1) {
      return 'p-6 rounded-xl border-2 bg-blue-900 border-white transition-all duration-300';
    }
    if ((stage === 'audio' || stage === 'summary' || stage === 'complete') && stageNumber < (stage === 'audio' ? 2 : stage === 'summary' ? 3 : 4)) {
      return 'p-6 rounded-xl border-2 bg-blue-900 border-white transition-all duration-300';
    }
    return 'p-6 rounded-xl border-2 bg-slate-900 border-white/30 transition-all duration-300';
  };

  const getIconClass = () => {
    if (isActive) return `w-8 h-8 ${config.iconActiveClasses}`;
    if (result && stageNumber === 1) return 'w-8 h-8 text-white';
    if ((stage === 'audio' || stage === 'summary' || stage === 'complete') && stageNumber < (stage === 'audio' ? 2 : stage === 'summary' ? 3 : 4)) {
      return 'w-8 h-8 text-white';
    }
    return 'w-8 h-8 text-white/50';
  };

  const shouldShowComplete = () => {
    if (stageNumber === 1 && result) return true;
    if (stageNumber === 2 && (stage === 'summary' || stage === 'complete')) return true;
    return false;
  };

  return (
    <div className={getCardClass()}>
      <div className="flex items-center gap-3 mb-3">
        <Icon className={getIconClass()} />
        <h3 className="text-xl font-bold text-white">{config.title}</h3>
      </div>

      {isActive && (
        <div className="mt-4">
          <div className="flex items-center gap-2 mb-3">
            <Loader2 className={`w-5 h-5 animate-spin ${config.iconActiveClasses.split(' ')[0]}`} />
            <span className={config.textClasses}>{config.activeLabel}</span>
          </div>
          
          {stageNumber === 2 && <AudioVisualizer isActive={isActive} />}
          
          <div className="bg-white/10 rounded-lg h-3 overflow-hidden mb-2">
            <div
              className={`bg-gradient-to-r ${config.progressClasses} h-full transition-all duration-300`}
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className={`${config.textClasses} text-sm`}>{progress}%</span>
        </div>
      )}

      {shouldShowComplete() && !isActive && (
        <div className="mt-4 bg-green-500/20 border border-green-400 rounded-lg p-3 animate-fade-in">
          <div className="flex items-center gap-2 text-green-300">
            <CheckCircle className="w-5 h-5" />
            {stageNumber === 1 && result ? (
              <div>
                <span className="font-semibold block">{result}</span>
                <span className="text-xs text-green-400">Confidence: 92%</span>
              </div>
            ) : (
              <div>
                <span className="font-semibold">Complete</span>
                {stageNumber === 2 && <span className="text-xs text-green-400 block">Duration: 30s</span>}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StageCard;