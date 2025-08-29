import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Play, 
  Download, 
  Share2, 
  BookOpen, 
  Globe,
  Clock,
  CheckCircle,
  ArrowLeft,
  ExternalLink,
  FileText,
  Video
} from 'lucide-react'
import toast from 'react-hot-toast'

const ResultPage = () => {
  const { questionId } = useParams()
  const [isPlaying, setIsPlaying] = useState(false)
  const [activeTab, setActiveTab] = useState<'video' | 'script' | 'citations'>('video')

  // Mock data - replace with actual API data
  const mockResult = {
    question: 'What is the derivative of x² with respect to x?',
    answer: '2x',
    subject: 'Calculus',
    duration: '3:45',
    videoUrl: '/sample-video.mp4', // Replace with actual video URL
    script: [
      {
        scene: 1,
        title: 'Introduction to Derivatives',
        content: 'In calculus, a derivative represents the rate of change of a function with respect to its variable. Today, we\'ll explore how to find the derivative of x².',
        duration: '0:00-0:15'
      },
      {
        scene: 2,
        title: 'Power Rule',
        content: 'The power rule states that for any function f(x) = xⁿ, the derivative f\'(x) = n·xⁿ⁻¹. For x², n = 2.',
        duration: '0:15-0:45'
      },
      {
        scene: 3,
        title: 'Calculating the Derivative',
        content: 'Applying the power rule: d/dx(x²) = 2·x²⁻¹ = 2x. Therefore, the derivative of x² is 2x.',
        duration: '0:45-1:15'
      },
      {
        scene: 4,
        title: 'Verification',
        content: 'We can verify this by checking that the derivative of 2x is indeed 2, which matches our expectation.',
        duration: '1:15-1:45'
      }
    ],
    citations: [
      {
        source: 'Calculus: Early Transcendentals',
        author: 'James Stewart',
        url: 'https://example.com/stewart-calculus',
        page: '156-158',
        relevance: 'Core derivative concepts and power rule'
      },
      {
        source: 'MIT OpenCourseWare - Single Variable Calculus',
        author: 'MIT Mathematics Department',
        url: 'https://ocw.mit.edu/courses/mathematics',
        page: 'Lecture 4',
        relevance: 'Derivative applications and examples'
      },
      {
        source: 'Khan Academy - Derivatives',
        author: 'Khan Academy',
        url: 'https://www.khanacademy.org/math/calculus-1',
        page: 'Power Rule Section',
        relevance: 'Interactive derivative tutorials'
      }
    ],
    generatedAt: '2024-01-15 14:30:00',
    processingTime: '2 minutes 15 seconds'
  }

  const handlePlayVideo = () => {
    setIsPlaying(true)
    // Add actual video player logic here
    toast.success('Video playback started!')
  }

  const handleDownload = () => {
    // Add actual download logic here
    toast.success('Download started!')
  }

  const handleShare = () => {
    // Add actual share logic here
    navigator.clipboard.writeText(window.location.href)
    toast.success('Link copied to clipboard!')
  }

  const tabs = [
    { id: 'video', label: 'Video', icon: Video },
    { id: 'script', label: 'Script', icon: FileText },
    { id: 'citations', label: 'Citations', icon: BookOpen }
  ]

  return (
    <div className="pt-16 min-h-screen bg-dark-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <Link
            to="/questions"
            className="inline-flex items-center space-x-2 text-gray-400 hover:text-white transition-colors mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Questions</span>
          </Link>

          <div className="glass-effect rounded-2xl p-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold mb-3 text-white">
                  {mockResult.question}
                </h1>
                <div className="flex flex-wrap gap-3">
                  <span className="px-3 py-1 rounded-full text-sm font-medium text-gray-300 bg-dark-300/40">
                    {mockResult.subject}
                  </span>
                  <span className="px-3 py-1 rounded-full text-sm font-medium text-green-400 bg-green-400/10">
                    Answer: {mockResult.answer}
                  </span>
                  <span className="px-3 py-1 rounded-full text-sm font-medium text-gray-400 bg-gray-400/10">
                    <Clock className="w-3 h-3 inline mr-1" />
                    {mockResult.duration}
                  </span>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={handlePlayVideo}
                  className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-200 to-primary-400 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-2xl hover:shadow-primary-200/25 transition-all duration-300 transform hover:scale-105"
                >
                  <Play className="w-5 h-5" />
                  <span>Play Video</span>
                </button>
                
                <button
                  onClick={handleDownload}
                  className="inline-flex items-center space-x-2 bg-dark-200/50 backdrop-blur-sm border border-dark-300/50 text-white px-6 py-3 rounded-xl font-semibold hover:bg-dark-300/50 transition-all duration-300"
                >
                  <Download className="w-5 h-5" />
                  <span>Download</span>
                </button>
                
                <button
                  onClick={handleShare}
                  className="inline-flex items-center space-x-2 bg-dark-200/50 backdrop-blur-sm border border-dark-300/50 text-white px-6 py-3 rounded-xl font-semibold hover:bg-dark-300/50 transition-all duration-300"
                >
                  <Share2 className="w-5 h-5" />
                  <span>Share</span>
                </button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mb-8"
        >
          <div className="flex space-x-1 bg-dark-200/50 backdrop-blur-sm border border-dark-300/50 rounded-xl p-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-300 text-white shadow-lg'
                      : 'text-gray-400 hover:text-white hover:bg-dark-300/50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </motion.div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {activeTab === 'video' && (
            <div className="glass-effect rounded-2xl p-6">
              <div className="aspect-video bg-dark-200 rounded-xl flex items-center justify-center mb-6">
                {isPlaying ? (
                  <div className="text-center">
                    <div className="w-20 h-20 border-4 border-primary-300 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-300">Video is playing...</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="w-24 h-24 bg-gradient-to-br from-primary-200 to-primary-400 rounded-full flex items-center justify-center mx-auto mb-4 cursor-pointer hover:scale-110 transition-transform" onClick={handlePlayVideo}>
                      <Play className="w-12 h-12 text-white ml-1" />
                    </div>
                    <p className="text-gray-300">Click to play video</p>
                  </div>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-400">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4" />
                  <span>Duration: {mockResult.duration}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Generated: {mockResult.generatedAt}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Video className="w-4 h-4" />
                  <span>Processing: {mockResult.processingTime}</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'script' && (
            <div className="glass-effect rounded-2xl p-6">
              <h3 className="text-2xl font-bold mb-6 text-white">Video Script</h3>
              <div className="space-y-6">
                {mockResult.script.map((scene, index) => (
                  <motion.div
                    key={scene.scene}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="border-l-4 border-primary-300 pl-6"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="text-lg font-semibold text-white">
                        Scene {scene.scene}: {scene.title}
                      </h4>
                      <span className="text-sm text-gray-400 bg-dark-300/50 px-2 py-1 rounded">
                        {scene.duration}
                      </span>
                    </div>
                    <p className="text-gray-300 leading-relaxed">
                      {scene.content}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'citations' && (
            <div className="glass-effect rounded-2xl p-6">
              <h3 className="text-2xl font-bold mb-6 text-white">Research Sources & Citations</h3>
              <div className="space-y-4">
                {mockResult.citations.map((citation, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="glass-effect rounded-xl p-4"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="text-lg font-semibold text-white">
                        {citation.source}
                      </h4>
                      <span className="text-sm text-gray-400 bg-dark-300/50 px-2 py-1 rounded">
                        p.{citation.page}
                      </span>
                    </div>
                    <p className="text-gray-400 mb-2">
                      <span className="text-gray-300">Author:</span> {citation.author}
                    </p>
                    <p className="text-gray-400 mb-3">
                      <span className="text-gray-300">Relevance:</span> {citation.relevance}
                    </p>
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-2 text-primary-300 hover:text-primary-200 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span>View Source</span>
                    </a>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        {/* Bottom Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-12 text-center"
        >
          <div className="glass-effect rounded-2xl p-8">
            <h3 className="text-2xl font-bold mb-4 text-white">
              Ready to Create Another Video?
            </h3>
            <p className="text-gray-300 mb-6">
              Generate more AI-powered educational content with our comprehensive question library.
            </p>
            <Link
              to="/questions"
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-200 to-primary-400 text-white px-8 py-4 rounded-xl font-semibold hover:shadow-2xl hover:shadow-primary-200/25 transition-all duration-300 transform hover:scale-105"
            >
              <BookOpen className="w-5 h-5" />
              <span>Browse More Questions</span>
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default ResultPage
