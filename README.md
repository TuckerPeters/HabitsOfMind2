# Habits of Mind Educational Platform

A comprehensive educational platform designed to support educators, students, and organizations in developing and implementing the 16 Habits of Mind framework. This platform provides AI-powered coaching tools, content management, certification programs, and community resources for transforming educational practices.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development](#development)
- [Deployment](#deployment)
- [Features](#features)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)

## Overview

The Habits of Mind platform serves a network of 100,000+ educators worldwide, offering:

- **AI-Powered Coaching Tools**: Interactive chat interfaces using OpenAI integration for personalized guidance
- **Content Management System**: Full-featured CMS for managing educational resources, events, and practitioner profiles
- **Certification & Badges**: Stripe-integrated payment system for certification programs
- **Resource Library**: Comprehensive collection of educational materials across multiple perspectives
- **Community Features**: Team directory, practitioner network, and collaborative tools
- **Multi-Perspective Content**: Tailored resources for teachers, students, parents, and employers

### The 16 Habits of Mind

The platform centers around 16 core intellectual behaviors:
1. Persisting
2. Managing Impulsivity
3. Listening with Understanding and Empathy
4. Thinking Flexibly
5. Thinking About Thinking (Metacognition)
6. Striving for Accuracy
7. Questioning and Posing Problems
8. Applying Past Knowledge to New Situations
9. Thinking and Communicating with Clarity and Precision
10. Gathering Data Through All Senses
11. Creating, Imagining, Innovating
12. Responding with Wonderment and Awe
13. Taking Responsible Risks
14. Finding Humor
15. Thinking Interdependently
16. Remaining Open to Continuous Learning

## Architecture

### System Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│   Frontend      │◄───────►│   Backend API    │◄───────►│   Firebase      │
│   (Netlify)     │  HTTPS  │   (Heroku)       │  Admin  │   Firestore     │
│   SvelteKit     │         │   Express.js     │   SDK   │   Storage       │
│                 │         │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     │
                            ┌────────┴────────┐
                            │                 │
                      ┌─────▼─────┐     ┌────▼────┐
                      │           │     │         │
                      │  OpenAI   │     │ Stripe  │
                      │    API    │     │   API   │
                      │           │     │         │
                      └───────────┘     └─────────┘
```

### Data Flow

**Frontend → Backend → Database**
1. User interacts with SvelteKit UI
2. Frontend makes authenticated API calls to backend
3. Backend validates JWT tokens and permissions
4. Backend queries/updates Firestore collections
5. Response returns through the chain with appropriate data

### Deployment Architecture

- **Frontend**: Static site on Netlify (CDN-distributed)
- **Backend**: Node.js app on Heroku
- **Database**: Firebase Firestore (NoSQL)
- **Storage**: Firebase Cloud Storage (images, files)
- **APIs**: OpenAI (AI features), Stripe (payments)

## Technology Stack

### Frontend
- **Framework**: SvelteKit 2.37.1 (Static site generation)
- **Build Tool**: Vite 5.4.19
- **Language**: JavaScript (with TypeScript checking)
- **Adapter**: @sveltejs/adapter-static
- **State Management**: Svelte stores (6 global stores)
- **HTTP Client**: Axios 1.6.8
- **Markdown**: Marked 16.3.0

### Backend
- **Runtime**: Node.js 22.20
- **Framework**: Express.js 4.18.3
- **Language**: JavaScript (ES Modules)
- **Database**: Firebase Firestore (18 collections)
- **Storage**: Firebase Cloud Storage
- **Authentication**: JWT (jsonwebtoken 9.0.2)
- **Password Hashing**: bcrypt 6.0.0
- **Validation**: Zod 3.22.4 schemas
- **Security**: Helmet 8.1.0, CORS, DOMPurify 2.29.0

### External Services
- **AI**: OpenAI API 4.80.1 (GPT models)
- **Payments**: Stripe 18.5.0
- **Hosting**: Netlify (frontend), Heroku (backend)

### Development Tools
- **Package Manager**: npm
- **Process Manager**: Nodemon (development)
- **File Upload**: Multer 2.0.0
- **Compression**: compression 1.7.4

## Project Structure

```
HabitsOfMind2/
├── frontend/                 # SvelteKit frontend application
│   ├── src/
│   │   ├── routes/          # 79 route pages (file-based routing)
│   │   │   ├── +page.svelte           # Homepage
│   │   │   ├── about/                 # About pages
│   │   │   ├── habits/                # 16 Habits of Mind pages
│   │   │   ├── resources/             # Resource library
│   │   │   ├── aichat/                # AI chat interface
│   │   │   ├── certification/         # Certification program
│   │   │   ├── events/                # Events calendar
│   │   │   ├── cms/                   # CMS admin interface
│   │   │   └── ...
│   │   ├── lib/
│   │   │   ├── stores/      # Global state management (6 stores)
│   │   │   │   ├── auth.js            # Authentication state
│   │   │   │   ├── admin.js           # Admin data
│   │   │   │   ├── aiChat.js          # Chat state
│   │   │   │   ├── content.js         # Content cache
│   │   │   │   ├── firebase.js        # Firebase instance
│   │   │   │   └── ui.js              # UI state
│   │   │   ├── api/         # API service layer (9 modules)
│   │   │   ├── components/  # Reusable UI components
│   │   │   └── utils/       # Utility functions
│   │   └── app.html         # HTML template
│   ├── static/              # Static assets (images, etc.)
│   ├── svelte.config.js     # SvelteKit configuration
│   ├── vite.config.js       # Vite bundler config
│   ├── netlify.toml         # Netlify deployment config
│   └── package.json
│
├── backend/                  # Express.js backend API
│   ├── src/
│   │   ├── routes/          # API route handlers
│   │   │   ├── admin.js              # Admin endpoints
│   │   │   ├── auth.js               # Authentication
│   │   │   ├── badges.js             # Badge management
│   │   │   ├── checkout.js           # Stripe checkout
│   │   │   ├── content.js            # Content CRUD
│   │   │   ├── events.js             # Event management
│   │   │   ├── practitioners.js      # Practitioner profiles
│   │   │   ├── resources.js          # Resource library
│   │   │   ├── teamDirectory.js      # Team management
│   │   │   └── ...
│   │   ├── controllers/     # Business logic controllers
│   │   ├── models/          # Data models & schemas
│   │   │   ├── Badge.js              # Badge schema
│   │   │   ├── Certification.js      # Certification schema
│   │   │   ├── Event.js              # Event schema
│   │   │   ├── Practitioner.js       # Practitioner schema
│   │   │   ├── Resource.js           # Resource schema
│   │   │   ├── User.js               # User schema
│   │   │   └── ...
│   │   ├── middleware/      # Express middleware
│   │   │   ├── auth.js               # JWT verification
│   │   │   ├── validation.js         # Zod validation
│   │   │   ├── sanitization.js       # XSS protection
│   │   │   ├── adminAuth.js          # Role-based access
│   │   │   └── errorHandler.js       # Error handling
│   │   ├── config/          # Configuration files
│   │   │   └── firebase.js           # Firebase admin setup
│   │   ├── utils/           # Utility functions
│   │   └── index.js         # Express app entry point
│   ├── package.json
│   └── Procfile             # Heroku deployment config
│
├── HabitsOfMind/            # Original content/reference
├── archives/                # Archived files
├── extracted_content/       # Processed content data
├── scripts/                 # Utility scripts
├── screenshots/             # Documentation screenshots
├── crawler_env/             # Python environment for crawler
├── .gitignore
└── README.md               # This file
```

## Getting Started

### Prerequisites

- Node.js 18+ (backend runs on 22.20 in production)
- npm or yarn
- Firebase account with Firestore database
- Firebase Admin SDK credentials
- OpenAI API key
- Stripe account (for payment features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd HabitsOfMind2
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   npm install
   ```

3. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Set up Firebase**
   - Create a Firebase project at https://console.firebase.google.com
   - Enable Firestore Database
   - Enable Firebase Storage
   - Download Admin SDK credentials JSON
   - Place credentials file in the root directory

5. **Configure environment variables**

   Create `backend/.env`:
   ```env
   PORT=3000
   NODE_ENV=development

   # Firebase
   FIREBASE_PROJECT_ID=your-project-id
   GOOGLE_APPLICATION_CREDENTIALS=../habitsofmind-firebase-adminsdk.json

   # JWT
   JWT_SECRET=your-jwt-secret-key

   # OpenAI
   OPENAI_API_KEY=your-openai-api-key

   # Stripe
   STRIPE_SECRET_KEY=your-stripe-secret-key
   STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

   # CORS
   FRONTEND_URL=http://localhost:5173
   ```

   Create `frontend/.env`:
   ```env
   VITE_API_URL=http://localhost:3000
   VITE_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

   # Firebase Client
   VITE_FIREBASE_API_KEY=your-firebase-api-key
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   VITE_FIREBASE_APP_ID=your-app-id
   ```

6. **Initialize Firestore Collections**

   The backend will create collections automatically on first use. Required collections:
   - users
   - habits
   - resources
   - events
   - certifications
   - badges
   - practitioners
   - teamDirectory
   - contentPages (CMS)
   - heroSections (CMS)
   - announcements (CMS)
   - testimonials (CMS)
   - teamMembers (CMS)
   - projects (CMS)
   - statistics (CMS)
   - FAQs (CMS)
   - impactMetrics (CMS)
   - aiMessages (chat history)

## Development

### Running Locally

1. **Start the backend server**
   ```bash
   cd backend
   npm run dev
   ```
   Backend runs on http://localhost:3000

2. **Start the frontend dev server**
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend runs on http://localhost:5173

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:3000
   - Health check: http://localhost:3000/health

### Development Workflow

**Frontend Development:**
```bash
cd frontend
npm run dev          # Start dev server with hot reload
npm run build        # Build for production
npm run preview      # Preview production build
npm run check        # Type checking
```

**Backend Development:**
```bash
cd backend
npm run dev          # Start with nodemon (auto-restart)
npm start            # Start production server
```

### API Testing

Use tools like Postman or curl to test endpoints:

```bash
# Health check
curl http://localhost:3000/health

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Get habits (authenticated)
curl http://localhost:3000/api/habits \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Deployment

### Frontend (Netlify)

The frontend is configured for automatic deployment via `netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = "build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Deployment Steps:**
1. Connect repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `build`
4. Add environment variables in Netlify dashboard
5. Deploy automatically on git push

**Production URL:** https://www.habitsofmindinstitute.org

### Backend (Heroku)

The backend is configured with a `Procfile`:

```
web: node src/index.js
```

**Deployment Steps:**
1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set Node version in package.json:
   ```json
   "engines": {
     "node": "22.x"
   }
   ```
5. Set environment variables:
   ```bash
   heroku config:set JWT_SECRET=your-secret
   heroku config:set OPENAI_API_KEY=your-key
   heroku config:set STRIPE_SECRET_KEY=your-key
   # ... etc
   ```
6. Deploy:
   ```bash
   cd backend
   git push heroku main
   ```
7. Scale: `heroku ps:scale web=1`

**Production URL:** https://habits-of-mind-backend-d01faabf0c5e.herokuapp.com

### Environment Variables (Production)

**Netlify Environment Variables:**
- `VITE_API_URL` = https://habits-of-mind-backend-d01faabf0c5e.herokuapp.com
- `VITE_STRIPE_PUBLISHABLE_KEY`
- Firebase config variables (VITE_FIREBASE_*)

**Heroku Environment Variables:**
- `PORT` (set automatically by Heroku)
- `NODE_ENV` = production
- `FIREBASE_PROJECT_ID`
- `JWT_SECRET`
- `OPENAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `FRONTEND_URL` = https://www.habitsofmindinstitute.org

## Features

### 1. AI-Powered Coaching Tools

**Location:** `/frontend/src/routes/aichat/`

Interactive chat interface using OpenAI's GPT models:
- Personalized educational guidance
- Context-aware responses based on Habits of Mind framework
- Real-time streaming responses
- Conversation history stored in Firestore
- Multiple coaching personas

**Backend:** `/backend/src/routes/openai.js`

### 2. Content Management System (CMS)

**Location:** `/frontend/src/routes/cms/`

Full-featured admin interface for managing site content:

- **Hero Sections** - Homepage and landing page heroes
- **Announcements** - Site-wide announcement banners
- **Testimonials** - User testimonials and success stories
- **Team Members** - Staff and leadership profiles
- **Projects** - Showcase educational projects
- **Statistics** - Impact metrics and data visualization
- **Content Pages** - Dynamic page content management
- **FAQs** - Frequently asked questions
- **Events** - Event calendar and registration
- **Resources** - Educational resource library
- **Practitioners** - Practitioner directory
- **Certifications** - Certification program management
- **Badges** - Achievement badge system
- **Team Directory** - Organization team listings
- **Habits** - 16 Habits of Mind content

**Access Control:**
- **super_admin**: Full access to all CMS features
- **admin**: Most features except sensitive operations
- **editor**: Content editing only

### 3. Certification & Badge System

**Location:** `/frontend/src/routes/certification/`

Stripe-integrated certification program:
- Multiple certification levels
- Secure payment processing
- Digital badge issuance
- Certificate generation
- Progress tracking

**Backend:** `/backend/src/routes/checkout.js`, `/backend/src/routes/badges.js`

### 4. Resource Library

**Location:** `/frontend/src/routes/resources/`

Comprehensive educational materials:
- Multi-format support (PDF, video, links)
- Categorized by perspective (teacher, student, parent, employer)
- Tag-based filtering
- Search functionality
- File upload and storage via Firebase Storage

**Backend:** `/backend/src/routes/resources.js`

### 5. Event Management

**Location:** `/frontend/src/routes/events/`

Event calendar and registration system:
- Event creation and editing
- Date-based filtering
- Registration tracking
- Event details pages
- Past and upcoming event views

**Backend:** `/backend/src/routes/events.js`

### 6. Community Features

**Practitioner Network:** `/frontend/src/routes/practitioners/`
- Public practitioner profiles
- Location-based directory
- Specialization filtering
- Contact information

**Team Directory:** `/frontend/src/routes/team-directory/`
- Organization team listings
- Department categorization
- Member profiles

### 7. Multi-Perspective Content

Content tailored for different audiences:
- **Teachers** - `/frontend/src/routes/habits/teachers/`
- **Students** - `/frontend/src/routes/habits/students/`
- **Parents** - `/frontend/src/routes/habits/parents/`
- **Employers** - `/frontend/src/routes/habits/employers/`

Each perspective offers customized guidance and resources.

## API Documentation

### Base URLs

- **Development:** http://localhost:3000
- **Production:** https://habits-of-mind-backend-d01faabf0c5e.herokuapp.com

### Authentication

Most endpoints require JWT authentication:

```
Authorization: Bearer <JWT_TOKEN>
```

Admin endpoints require additional role verification.

### Core Endpoints

#### Authentication
```
POST   /api/auth/register          Register new user
POST   /api/auth/login             Login user
GET    /api/auth/verify            Verify JWT token
```

#### Habits of Mind
```
GET    /api/habits                 Get all habits
GET    /api/habits/:id             Get single habit
POST   /api/habits                 Create habit (admin)
PUT    /api/habits/:id             Update habit (admin)
DELETE /api/habits/:id             Delete habit (admin)
```

#### Resources
```
GET    /api/resources              Get all resources
GET    /api/resources/:id          Get single resource
POST   /api/resources              Create resource (admin)
PUT    /api/resources/:id          Update resource (admin)
DELETE /api/resources/:id          Delete resource (admin)
POST   /api/resources/upload       Upload resource file
```

#### Events
```
GET    /api/events                 Get all events
GET    /api/events/:id             Get single event
POST   /api/events                 Create event (admin)
PUT    /api/events/:id             Update event (admin)
DELETE /api/events/:id             Delete event (admin)
```

#### Certifications
```
GET    /api/certifications         Get all certifications
GET    /api/certifications/:id     Get single certification
POST   /api/certifications         Create certification (admin)
PUT    /api/certifications/:id     Update certification (admin)
DELETE /api/certifications/:id     Delete certification (admin)
```

#### Badges
```
GET    /api/badges                 Get all badges
GET    /api/badges/:id             Get single badge
POST   /api/badges                 Create badge (admin)
PUT    /api/badges/:id             Update badge (admin)
DELETE /api/badges/:id             Delete badge (admin)
POST   /api/badges/issue           Issue badge to user (admin)
```

#### Practitioners
```
GET    /api/practitioners          Get all practitioners
GET    /api/practitioners/:id      Get single practitioner
POST   /api/practitioners          Create practitioner (admin)
PUT    /api/practitioners/:id      Update practitioner (admin)
DELETE /api/practitioners/:id      Delete practitioner (admin)
```

#### Team Directory
```
GET    /api/team-directory         Get team members
GET    /api/team-directory/:id     Get single member
POST   /api/team-directory         Create member (admin)
PUT    /api/team-directory/:id     Update member (admin)
DELETE /api/team-directory/:id     Delete member (admin)
```

#### CMS Content
```
GET    /api/content/hero-sections          Get hero sections
POST   /api/content/hero-sections          Create hero (admin)
PUT    /api/content/hero-sections/:id      Update hero (admin)
DELETE /api/content/hero-sections/:id      Delete hero (admin)

GET    /api/content/announcements          Get announcements
POST   /api/content/announcements          Create announcement (admin)
PUT    /api/content/announcements/:id      Update announcement (admin)
DELETE /api/content/announcements/:id      Delete announcement (admin)

GET    /api/content/testimonials           Get testimonials
POST   /api/content/testimonials           Create testimonial (admin)
PUT    /api/content/testimonials/:id       Update testimonial (admin)
DELETE /api/content/testimonials/:id       Delete testimonial (admin)

GET    /api/content/team-members           Get team members
POST   /api/content/team-members           Create team member (admin)
PUT    /api/content/team-members/:id       Update team member (admin)
DELETE /api/content/team-members/:id       Delete team member (admin)

GET    /api/content/projects               Get projects
POST   /api/content/projects               Create project (admin)
PUT    /api/content/projects/:id           Update project (admin)
DELETE /api/content/projects/:id           Delete project (admin)

GET    /api/content/statistics             Get statistics
POST   /api/content/statistics             Create statistic (admin)
PUT    /api/content/statistics/:id         Update statistic (admin)
DELETE /api/content/statistics/:id         Delete statistic (admin)

GET    /api/content/pages                  Get content pages
GET    /api/content/pages/:slug            Get page by slug
POST   /api/content/pages                  Create page (admin)
PUT    /api/content/pages/:id              Update page (admin)
DELETE /api/content/pages/:id              Delete page (admin)

GET    /api/content/faqs                   Get FAQs
POST   /api/content/faqs                   Create FAQ (admin)
PUT    /api/content/faqs/:id               Update FAQ (admin)
DELETE /api/content/faqs/:id               Delete FAQ (admin)
```

#### AI Chat
```
POST   /api/openai/chat            Send chat message (streaming response)
GET    /api/openai/history         Get chat history
DELETE /api/openai/history/:id     Clear chat history
```

#### Stripe Integration
```
POST   /api/checkout/create-session        Create Stripe checkout session
GET    /api/checkout/session/:sessionId    Get session details
POST   /api/checkout/webhook               Stripe webhook handler
```

#### Admin
```
GET    /api/admin/users            Get all users (admin)
GET    /api/admin/users/:id        Get user details (admin)
PUT    /api/admin/users/:id/role   Update user role (super_admin)
DELETE /api/admin/users/:id        Delete user (super_admin)
GET    /api/admin/stats            Get system statistics (admin)
```

#### Health & Utility
```
GET    /health                     Health check endpoint
GET    /                          API welcome message
```

### Response Format

Successful responses:
```json
{
  "success": true,
  "data": { /* response data */ }
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error message"
}
```

### Rate Limiting

API endpoints are protected with rate limiting:
- 100 requests per 15 minutes per IP
- Stricter limits on authentication endpoints

## Security

### Authentication & Authorization

**JWT Tokens:**
- Tokens issued on login with 24-hour expiration
- Tokens include user ID and role
- Verified via middleware on protected routes

**Password Security:**
- Passwords hashed with bcrypt (10 salt rounds)
- No plaintext password storage
- Secure password requirements enforced

**Role-Based Access Control (RBAC):**
- `super_admin`: Full system access
- `admin`: Most features, no user management
- `editor`: Content editing only
- `user`: Public access

### Security Middleware Stack

**Helmet.js:**
- Sets security-related HTTP headers
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security

**CORS:**
- Configured for specific frontend origin
- Credentials allowed for authenticated requests
- Preflight request handling

**Input Sanitization:**
- HTML content sanitized with DOMPurify
- XSS attack prevention
- Script tag removal

**Input Validation:**
- Zod schemas for type-safe validation
- Request body validation middleware
- Parameter sanitization

### Firebase Security

**Firestore Rules:**
- Admin SDK bypasses client rules
- Backend server has full access
- Client SDK not used for sensitive operations

**Storage Rules:**
- Authenticated uploads only
- File type restrictions
- Size limits enforced

### API Security

**Rate Limiting:**
- Express-rate-limit middleware
- Per-IP request tracking
- Configurable limits per endpoint

**Error Handling:**
- Generic error messages to clients
- Detailed logging for debugging
- No stack traces in production

### Environment Security

- Sensitive credentials in environment variables
- `.gitignore` configured for secrets
- Firebase Admin SDK credentials file excluded
- Separate dev/prod configurations

## Environment Variables

### Backend Required Variables

```env
# Server
PORT=3000
NODE_ENV=development|production

# Firebase
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Authentication
JWT_SECRET=your-secret-key-min-32-chars

# OpenAI
OPENAI_API_KEY=sk-...

# Stripe
STRIPE_SECRET_KEY=sk_test_... or sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_test_... or pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# CORS
FRONTEND_URL=https://www.habitsofmindinstitute.org
```

### Frontend Required Variables

```env
# API
VITE_API_URL=https://habits-of-mind-backend-d01faabf0c5e.herokuapp.com

# Stripe
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_... or pk_live_...

# Firebase Client
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
```

## Contributing

### Development Guidelines

1. **Code Style:**
   - Use ES6+ syntax
   - Follow existing naming conventions
   - Add comments for complex logic
   - Use meaningful variable names

2. **Component Guidelines:**
   - Keep components focused and reusable
   - Props should have clear names
   - Handle loading and error states
   - Add appropriate error boundaries

3. **API Guidelines:**
   - Use RESTful conventions
   - Return consistent response formats
   - Include proper error handling
   - Validate all inputs with Zod schemas
   - Document new endpoints

4. **Security Guidelines:**
   - Never commit secrets or credentials
   - Validate and sanitize all inputs
   - Use parameterized queries
   - Implement proper authentication checks
   - Test authorization thoroughly

5. **Testing:**
   - Test API endpoints with various inputs
   - Test error conditions
   - Verify authentication/authorization
   - Check responsive design
   - Test across browsers

### Git Workflow

1. Create feature branch from main
2. Make changes with clear commit messages
3. Test thoroughly in development
4. Create pull request with description
5. Review and address feedback
6. Merge when approved

### Adding New Features

**New Content Type:**
1. Create Firestore collection
2. Define Zod schema in `/backend/src/models/`
3. Create route handler in `/backend/src/routes/`
4. Add controller logic in `/backend/src/controllers/`
5. Create API service in `/frontend/src/lib/api/`
6. Build UI components in `/frontend/src/routes/`
7. Add to CMS if admin-manageable

**New API Endpoint:**
1. Define in appropriate route file
2. Add Zod validation schema
3. Implement controller logic
4. Add authentication/authorization middleware
5. Document in this README
6. Test thoroughly

**New UI Page:**
1. Create route directory in `/frontend/src/routes/`
2. Add `+page.svelte` file
3. Create necessary components
4. Connect to API services
5. Add to navigation if needed
6. Test responsive design

## Database Schema

### Firestore Collections

**users**
```javascript
{
  uid: string,
  email: string,
  displayName: string,
  role: 'user' | 'editor' | 'admin' | 'super_admin',
  createdAt: timestamp,
  updatedAt: timestamp
}
```

**habits**
```javascript
{
  id: string,
  name: string,
  description: string,
  icon: string,
  order: number,
  content: {
    teachers: string,
    students: string,
    parents: string,
    employers: string
  },
  createdAt: timestamp,
  updatedAt: timestamp
}
```

**resources**
```javascript
{
  id: string,
  title: string,
  description: string,
  type: 'pdf' | 'video' | 'link' | 'document',
  url: string,
  perspective: 'teacher' | 'student' | 'parent' | 'employer',
  tags: string[],
  habitIds: string[],
  createdAt: timestamp,
  updatedAt: timestamp
}
```

**events**
```javascript
{
  id: string,
  title: string,
  description: string,
  date: timestamp,
  location: string,
  type: string,
  registrationUrl: string,
  imageUrl: string,
  createdAt: timestamp,
  updatedAt: timestamp
}
```

**certifications**
```javascript
{
  id: string,
  name: string,
  description: string,
  level: number,
  price: number,
  stripePriceId: string,
  requirements: string[],
  benefits: string[],
  createdAt: timestamp,
  updatedAt: timestamp
}
```

**badges**
```javascript
{
  id: string,
  name: string,
  description: string,
  imageUrl: string,
  criteria: string[],
  certificationId: string,
  createdAt: timestamp,
  updatedAt: timestamp
}
```

**practitioners**
```javascript
{
  id: string,
  name: string,
  bio: string,
  location: string,
  specialization: string[],
  email: string,
  phone: string,
  website: string,
  imageUrl: string,
  certifications: string[],
  createdAt: timestamp,
  updatedAt: timestamp
}
```

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check that all environment variables are set
- Verify Firebase credentials file path
- Ensure port 3000 is not in use
- Check Node.js version (18+)

**Frontend build fails:**
- Clear node_modules and reinstall
- Check for missing environment variables
- Verify all imports are correct
- Run `npm run check` for type errors

**API requests fail:**
- Verify backend is running
- Check CORS configuration
- Verify JWT token is valid
- Check network tab for error details

**Firebase errors:**
- Verify Firebase project ID
- Check Admin SDK credentials
- Ensure Firestore is enabled
- Verify collection permissions

**Stripe integration issues:**
- Use test keys in development
- Check webhook secret is correct
- Verify Stripe account is active
- Test with Stripe CLI for webhooks

### Logging

**Backend Logs:**
```bash
heroku logs --tail                 # Production logs
npm run dev                        # Development logs to console
```

**Frontend Logs:**
- Check browser console for errors
- Network tab for API requests
- Netlify deploy logs in dashboard

## Support & Resources

### Documentation
- SvelteKit: https://kit.svelte.dev/docs
- Express.js: https://expressjs.com/
- Firebase: https://firebase.google.com/docs
- OpenAI: https://platform.openai.com/docs
- Stripe: https://stripe.com/docs

### Habits of Mind Framework
- Official Website: https://www.habitsofmindinstitute.org
- Research: Costa & Kallick publications
- Community: 100,000+ educators worldwide

### Project Contacts
- For technical issues, check the project repository
- For Habits of Mind content questions, visit the official website

---

**Last Updated:** October 2025
**Version:** 1.0.0
**Status:** Production (Deployed October 19, 2025)
