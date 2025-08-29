# NotebookLM Video Generator - Frontend

A modern, sleek dark-themed frontend interface for an AI-powered video generation system that creates educational videos from questions and solutions.

## 🚀 Features

- **Modern Dark UI**: Sleek black theme with gradient accents and glass morphism effects
- **Responsive Design**: Fully responsive across all devices
- **Smooth Animations**: Framer Motion powered animations and transitions
- **Question Library**: Browse and select from a curated list of educational questions
- **Video Processing**: Real-time progress tracking for video generation
- **Result Viewing**: Comprehensive result page with video, script, and citations
- **Interactive Elements**: Hover effects, loading states, and smooth interactions

## 🛠️ Tech Stack

- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom dark theme
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **Notifications**: React Hot Toast
- **UI Components**: Headless UI

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Navbar.tsx     # Navigation component
├── pages/              # Page components
│   ├── HomePage.tsx    # Landing page
│   ├── QuestionsPage.tsx # Questions library
│   ├── ProcessingPage.tsx # Video generation progress
│   └── ResultPage.tsx  # Video results and playback
├── App.tsx             # Main app component with routing
├── main.tsx            # React entry point
└── index.css           # Global styles and Tailwind imports
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NotebookLM_Clone
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 📱 Pages Overview

### 🏠 Home Page
- Hero section with gradient text and call-to-action
- Feature highlights with animated icons
- Modern glass morphism design elements

### 📚 Questions Page
- Grid of educational questions with MCQ options
- Subject and difficulty tags
- Process buttons to start video generation
- Responsive card layout with hover effects

### ⚙️ Processing Page
- Real-time progress tracking for video generation
- Animated step indicators (Research → Content → Video)
- Progress bars and completion states
- Success confirmation with action buttons

### 🎬 Result Page
- Video player interface (placeholder)
- Tabbed content: Video, Script, Citations
- Download and share functionality
- Comprehensive result information

## 🎨 Design System

### Color Palette
- **Primary**: Blue gradients (`#0ea5e9` to `#0369a1`)
- **Accent**: Purple gradients (`#8b5cf6` to `#4c1d95`)
- **Dark**: Black to gray scale (`#0a0a0a` to `#8a8a8a`)
- **Text**: White and gray variations

### Components
- **Glass Effect**: Semi-transparent backgrounds with backdrop blur
- **Gradient Borders**: Subtle gradient borders for emphasis
- **Card Hover**: Scale and shadow effects on interaction
- **Smooth Transitions**: 200ms transitions for all interactive elements

## 🔧 Development

### Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Code Style
- TypeScript for type safety
- Tailwind CSS for styling
- Framer Motion for animations
- Component-based architecture

## 🌐 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📱 Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

## 🚧 Future Enhancements

- [ ] Real video player integration
- [ ] Backend API integration
- [ ] User authentication
- [ ] Video history and favorites
- [ ] Custom question creation
- [ ] Advanced video editing tools
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please open an issue in the repository.

---

**Built with ❤️ using React, TypeScript, and Tailwind CSS**
