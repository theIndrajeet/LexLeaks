# 🗞️ LexLeaks

> **A vintage-styled document leak platform built in just 13 hours** ⚡

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Built with](https://img.shields.io/badge/built%20with-Next.js%20%2B%20FastAPI-black)
![Time to Build](https://img.shields.io/badge/built%20in-13%20hours-ff69b4)

## 🎯 What is LexLeaks?

LexLeaks is a modern document leak platform with a vintage newspaper aesthetic. Think WikiLeaks meets The New York Times circa 1920. Features include:

- 📰 **Vintage Newspaper Theme** - Complete with sepia tones, drop caps, and typewriter animations
- 🌓 **Dark Mode** - Elegant dark theme with parchment-like colors
- 📄 **Document Viewer** - Built-in PDF viewer with redaction tools
- 📊 **Impact Tracking** - Track real-world outcomes from leaked documents
- 🔍 **Advanced Search** - Filter by date, category, verification status
- 🌍 **Multi-language Support** - 10 languages out of the box
- 🔐 **Admin Dashboard** - Secure content management system
- ✨ **Beautiful Animations** - Typewriter effects, smooth transitions

**Live Demo**: [https://lexleaks.com](https://lexleaks.com)

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL (or Supabase account)

### Frontend Setup

```bash
cd frontend-lexleaks

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Run development server
npm run dev
```

Visit `http://localhost:3000` 🎉

### Backend Setup

```bash
cd ../backend-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

API available at `http://localhost:8000` 🚀

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14.2.30 with TypeScript
- **Styling**: Tailwind CSS with custom vintage theme
- **State Management**: React Context API
- **Animations**: CSS animations + Framer Motion
- **Icons**: Lucide React
- **PDF Viewer**: react-pdf with custom controls

### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL (Supabase)
- **Authentication**: JWT tokens
- **Migrations**: Alembic

### Infrastructure
- **Frontend Hosting**: Netlify
- **Backend Hosting**: Google Cloud Run
- **Database**: Supabase
- **CDN**: Netlify Edge

## ⚡ The 13-Hour Sprint

Yes, this entire platform was built in a single 13-hour coding session. Here's what was accomplished:

**Hours 1-3**: Core architecture, database models, API endpoints  
**Hours 4-6**: Frontend setup, routing, component library  
**Hours 7-9**: Vintage theme, animations, dark mode  
**Hours 10-12**: Advanced features (search, filters, document viewer)  
**Hour 13**: Deployment, testing, polish  

### Features Built in Those 13 Hours:

- ✅ Complete authentication system
- ✅ Admin dashboard with CRUD operations
- ✅ Vintage newspaper theme with dark mode
- ✅ Typewriter animations
- ✅ Advanced search with filters
- ✅ Document viewer with redaction tools
- ✅ Impact tracking system
- ✅ Multi-language support (10 languages)
- ✅ Responsive design
- ✅ SEO optimization
- ✅ Production deployment

## 🎨 Design Philosophy

LexLeaks combines modern web technologies with vintage newspaper aesthetics:

- **Typography**: Georgia serif font with authentic drop caps
- **Colors**: Sepia tones (#f5f0e6) with burgundy accents (#8B0000)
- **Dark Mode**: Parchment-inspired (#1a1612 background, #f5f2ed text)
- **Animations**: Subtle typewriter effect on headlines
- **Layout**: Classic newspaper column structure

## 📁 Project Structure

```
LexLeaks/
├── frontend-lexleaks/     # Next.js frontend
│   ├── app/              # App router pages
│   ├── components/       # React components
│   ├── contexts/         # React contexts
│   └── public/           # Static assets
├── backend-api/          # FastAPI backend
│   ├── app/              # Application code
│   ├── alembic/          # Database migrations
│   └── requirements.txt  # Python dependencies
└── docs/                 # Documentation
```

## 🔧 Configuration

### Environment Variables

Frontend (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Backend (`.env`):
```bash
DATABASE_URL=postgresql://user:password@localhost/lexleaks
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🚢 Deployment

### Frontend (Netlify)

```bash
# Build command
npm run build

# Publish directory
.next
```

### Backend (Google Cloud Run)

```bash
# Build and deploy
gcloud run deploy backend-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## 📝 API Documentation

FastAPI provides automatic API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ☕ and determination
- Inspired by vintage newspapers and modern leak platforms
- Special thanks to the open source community

---

<p align="center">
  <strong>Built in 13 hours. Because sometimes you just need to ship.</strong>
</p>

<p align="center">
  <a href="https://lexleaks.com">Live Demo</a> •
  <a href="https://github.com/theIndrajeet/LexLeaks/issues">Report Bug</a> •
  <a href="https://github.com/theIndrajeet/LexLeaks/pulls">Contribute</a>
</p> 