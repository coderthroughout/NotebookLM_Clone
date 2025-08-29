# NotebookLM Video Generator

A comprehensive AI-powered video generation system that creates educational videos from questions and solutions using web research and AI content generation.

## 🏗️ Project Structure

```
NotebookLM_Clone/
├── Frontend/           # React-based frontend application
│   ├── src/           # Source code
│   ├── package.json   # Frontend dependencies
│   └── README.md      # Frontend documentation
├── research/           # Python backend research modules
├── requirements.txt    # Backend dependencies
├── citations.db        # SQLite database (ignored by git)
├── .gitignore          # Git ignore rules
├── .gitattributes      # Line endings + binary file rules
├── .editorconfig       # Editor settings
└── README.md           # This file
```

## 🚀 Quick Start

### Frontend
```bash
cd Frontend
npm install
npm run dev
```

### Backend (Phase 1)
```bash
python -m pip install -r requirements.txt
$env:SERPAPI_API_KEY="<your_key>"
python -m research.cli Q001 "photosynthesis process explained for students" --db citations.db --k 8 --provider serpapi --hl en --gl us --cred-threshold 0.45
python -m research.cli Q001 --db citations.db --show-top 8
```

## 🔑 Environment
- `SERPAPI_API_KEY` – required for Phase 1 search via SerpAPI
- (Phase 2) `OPENAI_API_KEY` – for outline/script/slide generation

## 🧩 Phase 1 Status
- Web research: SerpAPI (with hl/gl), fallback DDG
- robots.txt respected, per-domain rate limiting
- Extraction via Trafilatura + filesystem cache
- Credibility scoring + whitelist
- SQLite persistence and CLI to view top citations

## 🎯 What We're Building

### Phase 1: Frontend Interface ✅
- Modern dark-themed React application
- Question library with MCQ options
- Video processing workflow
- Result viewing and management

### Phase 2: Backend AI Systems (In Progress)
- **Web Research Engine**: Automatically crawls authoritative sources
- **AI Content Generation**: Uses OpenAI APIs for script and slide creation
- **Video Rendering**: Generates educational videos with citations
- **Citation Management**: Tracks all sources and references

### Phase 3: Integration & Deployment
- Frontend-backend API integration
- Video processing pipeline
- Production deployment

## 🛠️ Technology Stack

### Frontend
- React 18 + TypeScript
- Tailwind CSS + Framer Motion
- Vite build system

### Backend (Planned)
- Python 3.11
- OpenAI API integration
- Web scraping and research
- Video generation (MoviePy/ffmpeg)

## 📱 Features

- **AI-Powered Research**: Automatic web crawling for authoritative sources
- **Smart Content Generation**: AI creates comprehensive scripts and slides
- **Educational Videos**: Professional-quality videos with proper citations
- **Modern UI/UX**: Sleek dark theme with smooth animations
- **Responsive Design**: Works on all devices

## 🔄 Development Workflow

1. **Frontend**: React development in `Frontend/` directory
2. **Backend**: Python development in root directory
3. **Integration**: API endpoints and data flow
4. **Testing**: End-to-end testing of video generation pipeline

## 📁 Directory Structure

- **`Frontend/`**: Complete React application
  - `src/components/`: Reusable UI components
  - `src/pages/`: Page components (Home, Questions, Processing, Results)
  - `src/App.tsx`: Main application component
  - Configuration files for build tools

- **`.venv/`**: Python virtual environment for backend development

## 🚧 Current Status

- ✅ **Frontend**: Complete and ready for development
- 🔄 **Backend**: Planning and architecture in progress
- ⏳ **Integration**: Not started
- ⏳ **Deployment**: Not started

## 🎯 Next Steps

1. **Complete Frontend**: Ensure all components are working properly
2. **Backend Architecture**: Design the AI systems and APIs
3. **Web Research Engine**: Build the citation and research system
4. **AI Integration**: Connect OpenAI APIs for content generation
5. **Video Pipeline**: Implement video rendering and generation
6. **Testing & Deployment**: End-to-end testing and production setup

## 🤝 Contributing

1. Frontend changes: Work in the `Frontend/` directory
2. Backend development: Work in the root directory
3. Follow the established code style and architecture
4. Test thoroughly before submitting changes

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ for AI-powered education**
