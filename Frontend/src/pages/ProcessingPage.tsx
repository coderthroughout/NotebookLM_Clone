import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Brain, 
  Globe, 
  Video, 
  CheckCircle, 
  Clock,
  ArrowRight,
  Play,
  Download
} from 'lucide-react'
import toast from 'react-hot-toast'

const ProcessingPage = () => {
  const { questionId } = useParams()
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [isComplete, setIsComplete] = useState(false)

  const steps = [
    {
      id: 'research',
      title: 'Web Research & Citation',
      description: 'AI is researching the topic from authoritative sources',
      icon: Globe,
      duration: 3000
    },
    {
      id: 'content',
      title: 'Content Generation',
      description: 'Generating comprehensive script and slide content',
      icon: Brain,
      duration: 4000
    },
    {
      id: 'video',
      title: 'Video Rendering',
      description: 'Creating final video with animations and effects',
      icon: Video,
      duration: 5000
    }
  ]

  useEffect(() => {
    if (isComplete) return

    const runSteps = async () => {
      for (let i = 0; i < steps.length; i++) {
        setCurrentStep(i)
        setProgress(0)
        
        // Simulate step progress
        const stepDuration = steps[i].duration
        const interval = 100
        const stepsCount = stepDuration / interval
        
        for (let j = 0; j <= stepsCount; j++) {
          await new Promise(resolve => setTimeout(resolve, interval))
          setProgress((j / stepsCount) * 100)
        }
        
        // Small pause between steps
        await new Promise(resolve => setTimeout(resolve, 500))
      }
      
      setIsComplete(true)
      toast.success('Video generated successfully!')
    }

    runSteps()
  }, [isComplete])

  const handleViewResult = () => {
    navigate(`/result/${questionId}`)
  }

  const handleDownload = () => {
    // Simulate download
    toast.success('Download started!')
  }

  return (
    <div className="pt-16 min-h-screen bg-dark-50 flex items-center justify-center">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Generating</span> Your Video
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Our AI is researching, creating content, and rendering your educational video
          </p>
        </motion.div>

        {/* Progress Steps */}
        <div className="space-y-6 mb-12">
          {steps.map((step, index) => {
            const Icon = step.icon
            const isActive = index === currentStep
            const isCompleted = index < currentStep
            const isPending = index > currentStep

            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className={`relative glass-effect rounded-2xl p-6 transition-all duration-300 ${
                  isActive ? 'border-primary-400/50 bg-primary-400/5' : ''
                }`}
              >
                <div className="flex items-center space-x-4">
                  {/* Step Icon */}
                  <div className={`w-16 h-16 rounded-xl flex items-center justify-center transition-all duration-300 ${
                    isCompleted 
                      ? 'bg-green-500 text-white' 
                      : isActive 
                      ? 'bg-primary-400 text-white' 
                      : 'bg-dark-400 text-gray-500'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="w-8 h-8" />
                    ) : (
                      <Icon className="w-8 h-8" />
                    )}
                  </div>

                  {/* Step Content */}
                  <div className="flex-1 text-left">
                    <h3 className={`text-xl font-semibold mb-2 transition-colors duration-300 ${
                      isCompleted ? 'text-green-400' : isActive ? 'text-primary-400' : 'text-gray-400'
                    }`}>
                      {step.title}
                    </h3>
                    <p className="text-gray-300 mb-3">
                      {step.description}
                    </p>
                    
                    {/* Progress Bar */}
                    {isActive && (
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.1 }}
                        className="h-2 bg-dark-400 rounded-full overflow-hidden"
                      >
                        <div className="h-full bg-gradient-to-r from-primary-300 to-primary-400 rounded-full" />
                      </motion.div>
                    )}
                    
                    {isCompleted && (
                      <div className="flex items-center text-green-400 text-sm">
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Completed
                      </div>
                    )}
                  </div>

                  {/* Step Status */}
                  <div className="text-right">
                    {isActive && (
                      <div className="flex items-center space-x-2 text-primary-400">
                        <Clock className="w-4 h-4" />
                        <span className="text-sm">Processing...</span>
                      </div>
                    )}
                    {isCompleted && (
                      <div className="text-green-400 text-sm">✓ Done</div>
                    )}
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Completion State */}
        <AnimatePresence>
          {isComplete && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="text-center"
            >
              <div className="glass-effect rounded-2xl p-8 mb-8">
                <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-green-400 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-3xl font-bold mb-4 text-white">
                  Video Generated Successfully!
                </h2>
                <p className="text-gray-300 mb-6">
                  Your AI-powered educational video is ready. Watch it now or download for offline viewing.
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <button
                    onClick={handleViewResult}
                    className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-300 to-primary-400 text-white px-8 py-4 rounded-xl font-semibold hover:shadow-2xl hover:shadow-primary-400/25 transition-all duration-300 transform hover:scale-105"
                  >
                    <Play className="w-5 h-5" />
                    <span>Watch Video</span>
                    <ArrowRight className="w-5 h-5" />
                  </button>
                  
                  <button
                    onClick={handleDownload}
                    className="inline-flex items-center space-x-2 bg-dark-200/50 backdrop-blur-sm border border-dark-300/50 text-white px-8 py-4 rounded-xl font-semibold hover:bg-dark-300/50 transition-all duration-300"
                  >
                    <Download className="w-5 h-5" />
                    <span>Download MP4</span>
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Processing State */}
        {!isComplete && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center"
          >
            <div className="glass-effect rounded-2xl p-8">
              <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-300">
                Please wait while we process your request. This may take a few minutes.
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default ProcessingPage
