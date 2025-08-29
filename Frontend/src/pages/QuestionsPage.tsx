import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  Play, 
  BookOpen, 
  Brain, 
  Clock, 
  CheckCircle,
  AlertCircle,
  ArrowRight
} from 'lucide-react'
import toast from 'react-hot-toast'

// Mock data - replace with actual API calls
const mockQuestions = [
  {
    id: '1',
    question: 'What is the derivative of x² with respect to x?',
    options: ['x', '2x', 'x²', '2x²'],
    correctAnswer: 1,
    subject: 'Calculus',
    difficulty: 'Easy',
    estimatedTime: '3-4 minutes'
  },
  {
    id: '2',
    question: 'Explain the concept of photosynthesis in plants.',
    options: ['Energy conversion', 'Water absorption', 'Nutrient transport', 'All of the above'],
    correctAnswer: 3,
    subject: 'Biology',
    difficulty: 'Medium',
    estimatedTime: '4-5 minutes'
  },
  {
    id: '3',
    question: 'What is the chemical formula for water?',
    options: ['H2O', 'CO2', 'O2', 'N2'],
    correctAnswer: 0,
    subject: 'Chemistry',
    difficulty: 'Easy',
    estimatedTime: '2-3 minutes'
  },
  {
    id: '4',
    question: 'Explain Newton\'s three laws of motion with examples.',
    options: ['Basic physics', 'Advanced mechanics', 'Classical mechanics', 'Quantum physics'],
    correctAnswer: 2,
    subject: 'Physics',
    difficulty: 'Hard',
    estimatedTime: '5-6 minutes'
  },
  {
    id: '5',
    question: 'What is the capital of France?',
    options: ['London', 'Berlin', 'Paris', 'Madrid'],
    correctAnswer: 2,
    subject: 'Geography',
    difficulty: 'Easy',
    estimatedTime: '1-2 minutes'
  },
  {
    id: '6',
    question: 'Explain the process of cellular respiration.',
    options: ['Energy production', 'Oxygen intake', 'Carbon dioxide release', 'All of the above'],
    correctAnswer: 3,
    subject: 'Biology',
    difficulty: 'Medium',
    estimatedTime: '4-5 minutes'
  }
]

const QuestionsPage = () => {
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: string]: number }>({})
  const [processingStates, setProcessingStates] = useState<{ [key: string]: 'idle' | 'processing' | 'completed' | 'error' }>({})
  const navigate = useNavigate()

  const handleOptionSelect = (questionId: string, optionIndex: number) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: optionIndex
    }))
  }

  const handleProcessQuestion = async (questionId: string) => {
    if (selectedAnswers[questionId] === undefined) {
      toast.error('Please select an answer before processing')
      return
    }

    // Update processing state
    setProcessingStates(prev => ({
      ...prev,
      [questionId]: 'processing'
    }))

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Navigate to processing page
      navigate(`/processing/${questionId}`)
    } catch (error) {
      setProcessingStates(prev => ({
        ...prev,
        [questionId]: 'error'
      }))
      toast.error('Failed to start processing')
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'text-green-400 bg-green-400/10'
      case 'medium': return 'text-yellow-400 bg-yellow-400/10'
      case 'hard': return 'text-red-400 bg-red-400/10'
      default: return 'text-gray-400 bg-gray-400/10'
    }
  }

  const getSubjectColor = (subject: string) => {
    const colors = [
      'text-blue-400 bg-blue-400/10',
      'text-purple-400 bg-purple-400/10',
      'text-green-400 bg-green-400/10',
      'text-orange-400 bg-orange-400/10',
      'text-pink-400 bg-pink-400/10'
    ]
    return colors[subject.length % colors.length]
  }

  return (
    <div className="pt-16 min-h-screen bg-dark-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Questions</span> Library
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Select a question, choose your answer, and generate an AI-powered educational video
          </p>
        </motion.div>

        {/* Questions Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {mockQuestions.map((question, index) => (
            <motion.div
              key={question.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="glass-effect rounded-2xl p-6 card-hover"
            >
              {/* Question Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {question.question}
                  </h3>
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSubjectColor(question.subject)}`}>
                      {question.subject}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(question.difficulty)}`}>
                      {question.difficulty}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-medium text-gray-400 bg-gray-400/10">
                      <Clock className="w-3 h-3 inline mr-1" />
                      {question.estimatedTime}
                    </span>
                  </div>
                </div>
              </div>

              {/* MCQ Options */}
              <div className="space-y-3 mb-6">
                {question.options.map((option, optionIndex) => (
                  <button
                    key={optionIndex}
                    onClick={() => handleOptionSelect(question.id, optionIndex)}
                    className={`w-full text-left p-3 rounded-lg border transition-all duration-200 ${
                      selectedAnswers[question.id] === optionIndex
                        ? 'border-primary-50 bg-primary-50/10 text-primary-50'
                        : 'border-dark-400 hover:border-dark-300 hover:bg-dark-300/20 text-gray-300 hover:text-white'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        selectedAnswers[question.id] === optionIndex
                          ? 'border-primary-50 bg-primary-50'
                          : 'border-dark-400'
                      }`}>
                        {selectedAnswers[question.id] === optionIndex && (
                          <CheckCircle className="w-3 h-3 text-white" />
                        )}
                      </div>
                      <span className="font-medium">{option}</span>
                    </div>
                  </button>
                ))}
              </div>

              {/* Process Button */}
              <button
                onClick={() => handleProcessQuestion(question.id)}
                disabled={processingStates[question.id] === 'processing' || selectedAnswers[question.id] === undefined}
                className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center space-x-2 ${
                  processingStates[question.id] === 'processing'
                    ? 'bg-dark-400 text-gray-500 cursor-not-allowed'
                    : selectedAnswers[question.id] !== undefined
                    ? 'bg-gradient-to-r from-primary-300 to-primary-400 text-white hover:shadow-2xl hover:shadow-primary-400/25 transform hover:scale-105'
                    : 'bg-dark-400 text-gray-500 cursor-not-allowed'
                }`}
              >
                {processingStates[question.id] === 'processing' ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    <span>Generate Video</span>
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>

              {/* Status Indicator */}
              {processingStates[question.id] === 'completed' && (
                <div className="mt-3 flex items-center justify-center text-green-400 text-sm">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Video generated successfully!
                </div>
              )}
              {processingStates[question.id] === 'error' && (
                <div className="mt-3 flex items-center justify-center text-red-400 text-sm">
                  <AlertCircle className="w-4 h-4 mr-2" />
                  Failed to generate video
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="text-center mt-16"
        >
          <div className="glass-effect rounded-2xl p-8 max-w-2xl mx-auto">
            <Brain className="w-16 h-16 text-primary-50 mx-auto mb-4" />
            <h3 className="text-2xl font-bold mb-3 text-white">
              Need More Questions?
            </h3>
            <p className="text-gray-300 mb-6">
              Our AI system can generate custom questions and create comprehensive educational videos for any topic.
            </p>
            <button className="bg-gradient-to-r from-primary-50 to-accent-50 text-white px-8 py-3 rounded-xl font-semibold hover:shadow-2xl hover:shadow-primary-50/25 transition-all duration-300 transform hover:scale-105">
              Request Custom Questions
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default QuestionsPage
