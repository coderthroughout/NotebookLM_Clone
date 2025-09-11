import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  CheckCircle, 
  XCircle, 
  Clock, 
  FileVideo, 
  Loader2,
  Sparkles,
  Brain,
  Video,
  Download
} from 'lucide-react';
import { VideoStatusResponse } from '../services/api';

interface VideoGenerationProgressProps {
  questionId: string;
  onComplete: (status: VideoStatusResponse) => void;
  onError: (error: string) => void;
  className?: string;
}

const VideoGenerationProgress: React.FC<VideoGenerationProgressProps> = ({
  questionId,
  onComplete,
  onError,
  className = ''
}) => {
  const [status, setStatus] = useState<VideoStatusResponse | null>(null);
  const [isPolling, setIsPolling] = useState(true);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isPolling) {
      interval = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPolling]);

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/video-status/${questionId}`);
        if (response.ok) {
          const statusData: VideoStatusResponse = await response.json();
          setStatus(statusData);

          if (statusData.status === 'completed') {
            setIsPolling(false);
            onComplete(statusData);
          } else if (statusData.status === 'failed') {
            setIsPolling(false);
            onError(statusData.error || 'Video generation failed');
          }
        }
      } catch (error) {
        console.error('Failed to poll video status:', error);
      }
    };

    // Poll immediately, then every 2 seconds
    pollStatus();
    const interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, [questionId, onComplete, onError]);

  const getStepIcon = (step: string) => {
    if (step.includes('content')) return <Brain className="w-5 h-5" />;
    if (step.includes('script')) return <FileVideo className="w-5 h-5" />;
    if (step.includes('slides')) return <Sparkles className="w-5 h-5" />;
    if (step.includes('video')) return <Video className="w-5 h-5" />;
    if (step.includes('completed')) return <CheckCircle className="w-5 h-5" />;
    return <Loader2 className="w-5 h-5" />;
  };

  const getStepColor = (step: string) => {
    if (step.includes('completed')) return 'text-green-500';
    if (step.includes('failed')) return 'text-red-500';
    if (step.includes('video')) return 'text-blue-500';
    if (step.includes('slides')) return 'text-purple-500';
    if (step.includes('script')) return 'text-yellow-500';
    if (step.includes('content')) return 'text-indigo-500';
    return 'text-gray-400';
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressColor = () => {
    if (!status) return 'from-blue-500 to-purple-500';
    if (status.status === 'completed') return 'from-green-500 to-emerald-500';
    if (status.status === 'failed') return 'from-red-500 to-pink-500';
    return 'from-blue-500 to-purple-500';
  };

  const getStatusIcon = () => {
    if (!status) return <Loader2 className="w-6 h-6 animate-spin" />;
    
    switch (status.status) {
      case 'queued':
        return <Clock className="w-6 h-6 text-yellow-500" />;
      case 'running':
        return <Loader2 className="w-6 h-6 animate-spin text-blue-500" />;
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-500" />;
      default:
        return <Loader2 className="w-6 h-6 animate-spin" />;
    }
  };

  const getStatusText = () => {
    if (!status) return 'Initializing...';
    
    switch (status.status) {
      case 'queued':
        return 'Queued for processing';
      case 'running':
        return 'Generating video...';
      case 'completed':
        return 'Video generation completed!';
      case 'failed':
        return 'Video generation failed';
      default:
        return 'Unknown status';
    }
  };

  return (
    <motion.div
      className={`bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6 border border-gray-700 ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {getStatusIcon()}
          <div>
            <h3 className="text-xl font-semibold text-white">Video Generation</h3>
            <p className="text-gray-400 text-sm">Question ID: {questionId}</p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-2xl font-bold text-white">{formatTime(elapsedTime)}</div>
          <div className="text-gray-400 text-sm">Elapsed Time</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-400 mb-2">
          <span>Progress</span>
          <span>{status?.progress?.toFixed(1) || 0}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
          <motion.div
            className={`h-full bg-gradient-to-r ${getProgressColor()} rounded-full`}
            initial={{ width: 0 }}
            animate={{ width: `${status?.progress || 0}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Status */}
      <div className="mb-6">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
          <span className="text-white font-medium">{getStatusText()}</span>
        </div>
        
        {status?.current_step && (
          <div className="flex items-center space-x-3 text-gray-300">
            {getStepIcon(status.current_step)}
            <span className="text-sm">{status.current_step}</span>
          </div>
        )}
      </div>

      {/* Current Step Details */}
      <AnimatePresence>
        {status?.current_step && (
          <motion.div
            className="bg-gray-800 rounded-lg p-4 border border-gray-700"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex items-center space-x-3">
              <div className={`${getStepColor(status.current_step)}`}>
                {getStepIcon(status.current_step)}
              </div>
              <div>
                <div className="text-white font-medium">Current Step</div>
                <div className="text-gray-400 text-sm">{status.current_step}</div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Display */}
      {status?.error && (
        <motion.div
          className="mt-4 bg-red-900/20 border border-red-500/30 rounded-lg p-4"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="flex items-center space-x-3">
            <XCircle className="w-5 h-5 text-red-400" />
            <div>
              <div className="text-red-400 font-medium">Error</div>
              <div className="text-red-300 text-sm">{status.error}</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Success Display */}
      {status?.status === 'completed' && (
        <motion.div
          className="mt-4 bg-green-900/20 border border-green-500/30 rounded-lg p-4"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <div>
                <div className="text-green-400 font-medium">Success!</div>
                <div className="text-green-300 text-sm">Your video is ready</div>
              </div>
            </div>
            
            <motion.button
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center space-x-2 transition-all duration-200"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => window.open(`http://localhost:8000/api/download-video/${questionId}`, '_blank')}
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </motion.button>
          </div>
        </motion.div>
      )}

      {/* Estimated Time */}
      {status?.status === 'running' && (
        <div className="mt-4 text-center">
          <div className="text-gray-400 text-sm">
            Estimated completion: {formatTime(Math.max(0, 120 - elapsedTime))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default VideoGenerationProgress;
