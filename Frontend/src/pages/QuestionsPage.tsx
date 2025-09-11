import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Brain, 
  Clock, 
  CheckCircle, 
  XCircle,
  Video,
  Download,
  Eye,
  Sparkles
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import apiService, { Question, VideoStatusResponse } from '../services/api';
import VideoGenerationProgress from '../components/VideoGenerationProgress';
import VideoPlayer from '../components/VideoPlayer';

interface QuestionCardProps {
  question: Question;
  onGenerateVideo: (question: Question) => void;
  isGenerating: boolean;
  hasVideo: boolean;
  onViewVideo: (questionId: string) => void;
}

const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  onGenerateVideo,
  isGenerating,
  hasVideo,
  onViewVideo
}) => {
  const [showSolution, setShowSolution] = useState(false);

  return (
    <motion.div
      className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 border border-gray-700 hover:border-gray-600 transition-all duration-300"
      whileHover={{ y: -5, scale: 1.02 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <span className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-sm font-medium">
              {question.subject}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              question.difficulty === 'Beginner' ? 'bg-green-900 text-green-300' :
              question.difficulty === 'Intermediate' ? 'bg-yellow-900 text-yellow-300' :
              'bg-red-900 text-red-300'
            }`}>
              {question.difficulty}
            </span>
          </div>
          <h3 className="text-xl font-semibold text-white mb-3">
            {question.question}
          </h3>
        </div>
      </div>

      {/* MCQ Options */}
      <div className="space-y-3 mb-6">
        {question.options.map((option, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg border transition-all duration-200 ${
              index === question.correct_answer
                ? 'border-green-500 bg-green-900/20 text-green-300'
                : 'border-gray-600 bg-gray-800/50 text-gray-300 hover:border-gray-500'
            }`}
          >
            <span className="font-medium mr-3">{String.fromCharCode(65 + index)}.</span>
            {option}
          </div>
        ))}
      </div>

      {/* Solution Toggle */}
      <div className="mb-6">
        <button
          onClick={() => setShowSolution(!showSolution)}
          className="flex items-center space-x-2 text-blue-400 hover:text-blue-300 transition-colors duration-200"
        >
          <Brain className="w-4 h-4" />
          <span>{showSolution ? 'Hide Solution' : 'Show Solution'}</span>
        </button>
        
        <AnimatePresence>
          {showSolution && (
            <motion.div
              className="mt-3 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-blue-300 text-sm">
                <strong>Solution:</strong> {question.solution}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-3">
        {hasVideo ? (
          <motion.button
            onClick={() => onViewVideo(question.id)}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-medium flex items-center justify-center space-x-2 transition-all duration-200"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Eye className="w-5 h-5" />
            <span>View Video</span>
          </motion.button>
        ) : (
          <motion.button
            onClick={() => onGenerateVideo(question)}
            disabled={isGenerating}
            className={`flex-1 px-6 py-3 rounded-xl font-medium flex items-center justify-center space-x-2 transition-all duration-200 ${
              isGenerating
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white'
            }`}
            whileHover={!isGenerating ? { scale: 1.02 } : {}}
            whileTap={!isGenerating ? { scale: 0.98 } : {}}
          >
            {isGenerating ? (
              <>
                <Clock className="w-5 h-5 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Generate Video</span>
              </>
            )}
          </motion.button>
        )}

        {hasVideo && (
          <motion.button
            onClick={() => window.open(`http://localhost:8000/api/download-video/${question.id}`, '_blank')}
            className="px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-xl font-medium flex items-center space-x-2 transition-all duration-200"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Download className="w-5 h-5" />
          </motion.button>
        )}
      </div>
    </motion.div>
  );
};

const QuestionsPage: React.FC = () => {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingQuestion, setGeneratingQuestion] = useState<string | null>(null);
  const [showProgress, setShowProgress] = useState(false);
  const [showVideo, setShowVideo] = useState<string | null>(null);
  const [videoData, setVideoData] = useState<any>(null);

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const questionsData = await apiService.getQuestions();
      setQuestions(questionsData);
    } catch (error) {
      console.error('Failed to load questions:', error);
      toast.error('Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateVideo = async (question: Question) => {
    try {
      setGeneratingQuestion(question.id);
      setShowProgress(true);
      setShowVideo(null);

      const response = await apiService.generateVideo({
        question_id: question.id,
        question: question.question,
        solution: question.solution
      });

      if (response.status === 'started') {
        toast.success('Video generation started!');
      } else if (response.status === 'already_exists') {
        toast.success('Video already exists!');
        setGeneratingQuestion(null);
        setShowProgress(false);
      }
    } catch (error) {
      console.error('Failed to start video generation:', error);
      toast.error('Failed to start video generation');
      setGeneratingQuestion(null);
      setShowProgress(false);
    }
  };

  const handleVideoComplete = (status: VideoStatusResponse) => {
    setGeneratingQuestion(null);
    setShowProgress(false);
    toast.success('Video generation completed!');
    
    // Refresh questions to show video status
    loadQuestions();
  };

  const handleVideoError = (error: string) => {
    setGeneratingQuestion(null);
    setShowProgress(false);
    toast.error(`Video generation failed: ${error}`);
  };

  const handleViewVideo = async (questionId: string) => {
    try {
      const preview = await apiService.getVideoPreview(questionId);
      setVideoData(preview);
      setShowVideo(questionId);
    } catch (error) {
      console.error('Failed to load video preview:', error);
      toast.error('Failed to load video');
    }
  };

  const hasVideo = (questionId: string) => {
    // Check if video exists by trying to get preview
    return videoData?.question_id === questionId || false;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400 text-lg">Loading questions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <div className="container mx-auto px-6 py-8">
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Educational Questions
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Select a question to generate an AI-powered educational video. 
            Each video is created with research-backed content and professional presentation.
          </p>
        </motion.div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Questions List */}
          <div className="space-y-6">
            <motion.h2
              className="text-2xl font-semibold text-white mb-6"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              Available Questions
            </motion.h2>
            
            {questions.map((question, index) => (
              <QuestionCard
                key={question.id}
                question={question}
                onGenerateVideo={handleGenerateVideo}
                isGenerating={generatingQuestion === question.id}
                hasVideo={hasVideo(question.id)}
                onViewVideo={handleViewVideo}
              />
            ))}
          </div>

          {/* Right Panel - Progress or Video */}
          <div className="space-y-6">
            <AnimatePresence mode="wait">
              {showProgress && generatingQuestion && (
                <motion.div
                  key="progress"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                >
                  <VideoGenerationProgress
                    questionId={generatingQuestion}
                    onComplete={handleVideoComplete}
                    onError={handleVideoError}
                  />
                </motion.div>
              )}

              {showVideo && videoData && (
                <motion.div
                  key="video"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="mb-4">
                    <h3 className="text-xl font-semibold text-white mb-2">Generated Video</h3>
                    <p className="text-gray-400 text-sm">
                      Watch your AI-generated educational video
                    </p>
                  </div>
                  <VideoPlayer videoData={videoData} className="h-96" />
                </motion.div>
              )}

              {!showProgress && !showVideo && (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                  className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 border border-gray-700 text-center"
                >
                  <Video className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">
                    Ready to Generate Videos
                  </h3>
                  <p className="text-gray-400">
                    Select a question and click "Generate Video" to create an AI-powered educational video.
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionsPage;
