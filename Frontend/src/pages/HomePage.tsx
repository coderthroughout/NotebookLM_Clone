import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { 
  Video, 
  Brain, 
  Globe, 
  Zap, 
  ArrowRight, 
  Play,
  BookOpen,
  Sparkles
} from 'lucide-react'

const HomePage = () => {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Research',
      description: 'Automatically researches topics from authoritative web sources to build comprehensive knowledge bases.'
    },
    {
      icon: Video,
      title: 'Smart Video Generation',
      description: 'Creates educational videos with proper citations, visual elements, and structured content.'
    },
    {
      icon: Globe,
      title: 'Web Research Engine',
      description: 'Advanced citation engine that crawls the web to gather relevant materials and sources.'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Generate high-quality educational videos in minutes, not hours.'
    }
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  return (
    <div className="pt-16 min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-100/10 via-transparent to-accent-100/10"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="inline-flex items-center space-x-2 bg-dark-200/50 backdrop-blur-sm border border-dark-300/50 rounded-full px-4 py-2 mb-8"
            >
              <Sparkles className="w-4 h-4 text-primary-400" />
              <span className="text-sm text-gray-300">AI-Powered Video Generation</span>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">Transform Questions</span>
              <br />
              <span className="text-white">Into Videos</span>
            </h1>

            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Our AI system automatically researches topics, generates comprehensive content, 
              and creates educational videos with proper citations and visual elements.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/questions"
                className="group inline-flex items-center space-x-2 bg-gradient-to-r from-primary-300 to-primary-400 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-2xl hover:shadow-primary-400/25 transition-all duration-300 transform hover:scale-105"
              >
                <span>Get Started</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              
              <button className="inline-flex items-center space-x-2 bg-dark-200/60 backdrop-blur-sm border border-dark-300/60 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-dark-300/60 transition-all duration-300">
                <Play className="w-5 h-5" />
                <span>Watch Demo</span>
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-dark-100/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              How It <span className="gradient-text">Works</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              From question to video in three simple steps
            </p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8"
          >
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.title}
                  variants={itemVariants}
                  className="group"
                >
                  <div className="glass-effect rounded-2xl p-8 h-full card-hover">
                    <div className="w-16 h-16 bg-gradient-to-br from-primary-300 to-primary-400 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold mb-3 text-white">
                      {feature.title}
                    </h3>
                    <p className="text-gray-300 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </motion.div>
              )
            })}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to <span className="gradient-text">Create</span>?
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Start generating educational videos with AI-powered research and content creation.
            </p>
            <Link
              to="/questions"
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-50 to-accent-50 text-white px-10 py-4 rounded-xl font-semibold text-xl hover:shadow-2xl hover:shadow-primary-50/25 transition-all duration-300 transform hover:scale-105"
            >
              <BookOpen className="w-6 h-6" />
              <span>Browse Questions</span>
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
