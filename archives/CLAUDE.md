# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Habits of Mind AI is an educational platform that uses AI to help students develop the 16 Habits of Mind framework by Arthur L. Costa and Bena Kallick. The platform guides students through thinking processes rather than providing direct answers.

## Architecture

This is a full-stack application with two main components:

### Backend (`backend/`)
- **Node.js/Express** server with TypeScript support
- **OpenAI GPT-4o integration** for AI-powered educational guidance
- **Firebase** integration for data storage and authentication
- **WebSocket support** for real-time features
- **Heroku deployment** with Procfile configuration

### Frontend 
- **Svelte 4** application (referenced in netlify.toml as "HabitsOfMindAI" directory)
- **Vite** build system
- **TypeScript** support
- **Netlify deployment**

## Key Features

The platform provides several AI-powered educational tools:
- **Habit Coach**: Personalized guidance applying specific habits to learning challenges
- **Problem Solver's Workshop**: Guided problem-solving with Habits of Mind prompts
- **Reflection Tool**: Feedback focused on thinking habits rather than content correctness
- **Lesson Planner**: Curriculum integration for educators
- **Curriculum Designer**: Comprehensive curriculum planning
- **Assessment Builder**: Assessments evaluating both content and thinking habits

## Development Commands

### Backend Development
```bash
cd backend

# Install dependencies
npm install

# Development server with auto-reload
npm run dev:watch

# Production start
npm start

# Linting
npm run lint

# Health check deployment
npm run check-deployment
```

### Testing (Backend)
```bash
# Run all tests
npm run test:run-all

# Quick test run (no coverage, no lint)
npm run test:run-quick

# Specific test suites
npm run test:basic
npm run test:premium
npm run test:problem-solver
npm run test:lesson-planner
npm run test:assessment-builder
npm run test:habit-coach
npm run test:self-assessment

# Integration tests
npm run test:integration

# Test coverage
npm run test:coverage
```

### Frontend Development
```bash
# Based on netlify.toml and README configuration
cd HabitsOfMindAI

# Install dependencies
npm install

# Development server
npm run dev

# Build for production  
npm run build

# Type checking
npm run check
```

## API Endpoints

The backend exposes several key endpoints:
- `/api/habit-coach` - Personalized habit coaching responses
- `/api/reflection` - Student work reflections
- `/api/lesson-plan` - Lesson plan generation
- `/api/problem-solver` - Problem-solving guidance
- `/api/self-assessment` - Self-assessment feedback
- `/api/curriculum-designer` - Curriculum planning
- `/health` - Health check endpoint

## Environment Configuration

### Backend (.env)
```
# Server
PORT=5000
NODE_ENV=development
CORS_ORIGIN=https://habitsofmindai.netlify.app,http://localhost:5173

# OpenAI
OPENAI_API_KEY=your_api_key_here
OPENAI_ORGANIZATION=your_org_id_here

# Auth0
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_AUDIENCE=https://habits-of-mind-api
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret

# Security (FERPA/COPPA compliance)
ENCRYPTION_KEY=your_strong_encryption_key_here
DATA_RETENTION_DAYS=365
```

### Frontend (.env)
```
# API Configuration
VITE_API_BASE_URL=http://localhost:3000/api  # development
VITE_API_BASE_URL=https://habits-of-mind-backend-251762ec444d.herokuapp.com/api  # production

# Firebase
VITE_FIREBASE_CONFIG={"apiKey":"...","projectId":"..."}
VITE_USE_EMULATOR=true  # development only

# Auth0
VITE_AUTH0_DOMAIN=your-tenant.us.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=https://habits-of-mind-api
VITE_AUTH0_CALLBACK_URL=http://localhost:5173  # development
```

## Firebase Configuration

Firebase is used for data storage and authentication:
- Firestore rules: `firestore.rules`
- Firestore indexes: `firestore.indexes.json` 
- Emulator ports: Auth (9099), Firestore (8080), UI (4000)

## Deployment

### Backend (Heroku)
- Deployed to: `https://habits-of-mind-backend-251762ec444d.herokuapp.com`
- Auto-deploys from main branch
- Uses `Procfile: web: node src/index.js`

### Frontend (Netlify) 
- Deployed to: `https://habitsofmindai.netlify.app`
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Base directory: `HabitsOfMindAI`

## Production Readiness Features

- **High Availability**: Fallback mechanisms when backend services unavailable
- **Responsive Design**: Desktop, tablet, and mobile support  
- **Accessibility**: WCAG guidelines consideration
- **Resilient Architecture**: Graceful degradation and error handling
- **Offline Capability**: Client-side fallbacks
- **Performance Optimization**: Compression, caching, asset optimization
- **Security**: FERPA/COPPA compliance with encryption and data retention policies

## Code Architecture

### Backend Structure
- `src/index.js` - Main Express server with WebSocket support
- `src/controllers/` - API endpoint handlers for each educational tool
- `src/services/` - Core business logic including OpenAI integration
- `src/routes/` - API route definitions and middleware
- `src/middleware/` - Security headers and error handling
- `src/config/` - Application configuration management
- `src/utils/` - Utility functions and helpers

### OpenAI Integration
The platform uses GPT-4o with custom prompts designed to:
1. Ask Socratic questions that prompt reflection
2. Guide students through problem-solving processes
3. Provide feedback on thinking habits vs. content correctness
4. Customize learning experiences based on individual needs

Each educational tool has tailored system instructions focusing on the specific Habits of Mind rather than giving direct answers.