# LexLeaks - Whistleblowing Platform

A secure, full-stack platform for exposing corruption and misconduct in the legal industry. Built with FastAPI (backend) and Next.js (frontend).

## 🏗️ Project Structure

```
LexLeaks/
├── backend-api/                 # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application entry point
│   │   ├── database.py         # Database configuration
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── schemas.py          # Pydantic schemas
│   │   ├── crud.py             # Database operations
│   │   ├── auth.py             # Authentication utilities
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── posts.py        # Posts API endpoints
│   │       └── auth.py         # Authentication endpoints
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .gitignore
│
└── frontend-lexleaks/          # Next.js Frontend
    ├── app/
    │   ├── (public)/           # Public routes
    │   │   ├── page.tsx        # Home page
    │   │   ├── [slug]/         # Dynamic article pages
    │   │   ├── about/          # About page
    │   │   └── layout.tsx      # Public layout
    │   ├── (admin)/            # Admin routes
    │   │   ├── login/          # Login page
    │   │   ├── dashboard/      # Admin dashboard
    │   │   └── layout.tsx      # Admin layout
    │   ├── globals.css         # Global styles
    │   └── layout.tsx          # Root layout
    ├── components/
    │   └── PostCard.tsx        # Reusable components
    ├── lib/
    │   └── api.ts              # API utilities
    ├── package.json
    ├── tailwind.config.js
    └── tsconfig.json
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (local or Supabase)
- Git

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend-api
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Environment configuration:**
Create a `.env` file in `backend-api/`:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/lexleaks_db

# JWT Security
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeH.AtbZlNlH7WjYq

# Environment
ENVIRONMENT=development
```

5. **Generate password hash:**
```python
# Run this in Python to generate your admin password hash:
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("your_admin_password")
print(hashed)  # Use this in your .env file
```

6. **Run the backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend-lexleaks
```

2. **Install dependencies:**
```bash
npm install
```

3. **Environment configuration:**
Create a `.env.local` file in `frontend-lexleaks/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **Run the frontend:**
```bash
npm run dev
```

The website will be available at http://localhost:3000

### Initial Setup

1. **Create your first admin user:**
Visit http://localhost:8000/docs and use the `/api/auth/register` endpoint to create your admin user, or update the backend to create one automatically.

2. **Login to admin:**
Visit http://localhost:3000/admin/login and login with your admin credentials.

3. **Create your first post:**
Use the admin dashboard to create and publish your first leak.

## 🔧 Configuration

### Database Schema

The application uses PostgreSQL with the following main tables:

- **users**: Admin users and authors
- **posts**: Articles/leaks with title, content, status, etc.

### Authentication

- JWT tokens for admin authentication
- Secure cookie storage
- Protected admin routes
- Public API for published content

### Security Features

- CORS configuration for frontend-backend communication
- SQL injection protection via SQLAlchemy ORM
- Password hashing with bcrypt
- Environment variable protection
- Input validation with Pydantic

## 🎨 Features

### Frontend Features

- **Public Website:**
  - Homepage with latest published leaks
  - Individual article pages with clean URLs
  - About page explaining the mission
  - Responsive design with Tailwind CSS
  - SEO optimized with Next.js metadata

- **Admin Dashboard:**
  - Secure login system
  - Content management (create, edit, delete posts)
  - Draft/publish workflow
  - Rich text editor (ready for TipTap integration)
  - Statistics overview

### Backend Features

- **RESTful API:**
  - Post management endpoints
  - Authentication endpoints
  - Search functionality
  - Status filtering (draft/published/archived)

- **Security:**
  - JWT authentication
  - Protected admin endpoints
  - CORS configuration
  - Input validation

## 🐳 Docker Deployment

### Backend Docker

```bash
cd backend-api
docker build -t lexleaks-api .
docker run -p 8000:8000 --env-file .env lexleaks-api
```

### Environment for Production

Update your `.env` file for production:

```env
DATABASE_URL=postgresql://user:password@your-db-host:5432/lexleaks_production
SECRET_KEY=your-production-secret-key-very-long-and-random
ENVIRONMENT=production
```

## 📝 Usage

### Creating Content

1. Login to admin dashboard at `/admin/login`
2. Navigate to "Create New Post"
3. Write your article with title, content, and excerpt
4. Choose status: Draft (private) or Published (public)
5. Save and the post will be available with a SEO-friendly URL

### Managing Posts

- **Draft**: Private posts for preparation
- **Published**: Public posts visible on the website
- **Archived**: Hidden posts for backup

### API Usage

```javascript
// Get published posts
fetch('http://localhost:8000/api/posts/published')

// Get specific post by slug
fetch('http://localhost:8000/api/posts/slug/your-post-slug')

// Search posts
fetch('http://localhost:8000/api/posts/search?q=corruption')
```

## 🔒 Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **Database**: Use SSL connections in production
3. **JWT Secret**: Use a strong, random secret key
4. **CORS**: Update allowed origins for production domains
5. **HTTPS**: Always use HTTPS in production
6. **Rate Limiting**: Consider adding rate limiting for API endpoints

## 🚀 Deployment

### Backend Deployment (Google Cloud Run)

1. Build and push Docker image
2. Deploy to Cloud Run
3. Set environment variables in Cloud Run console
4. Connect to managed PostgreSQL database

### Frontend Deployment (Vercel/Netlify)

1. Connect GitHub repository
2. Set `NEXT_PUBLIC_API_URL` environment variable
3. Deploy automatically on commits

## 🛠️ Development

### Adding New Features

1. **Backend**: Add new endpoints in `routers/`
2. **Frontend**: Create new pages in `app/`
3. **Components**: Add reusable components in `components/`
4. **API**: Update `lib/api.ts` for new endpoints

### Rich Text Editor Integration

The project is ready for TipTap editor integration:

```bash
npm install @tiptap/react @tiptap/starter-kit
```

## 📋 TODO

- [ ] Rich text editor integration
- [ ] Image upload functionality  
- [ ] Email notifications
- [ ] Comment system
- [ ] Social sharing
- [ ] Advanced search filters
- [ ] User roles and permissions
- [ ] Analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and transparency purposes. Use responsibly and in accordance with local laws.

---

**⚠️ Important Security Note**: This platform is designed for legitimate whistleblowing. Always verify information before publishing and ensure you comply with applicable laws and regulations. 