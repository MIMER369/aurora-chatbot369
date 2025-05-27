# AURORA - E-Commerce AI Assistant

AURORA is an intelligent e-commerce chatbot that provides customer support using natural language processing. It features a sophisticated FAQ matching system powered by NLTK and optional OpenAI integration for enhanced responses.

## 🚀 Features

- **Intelligent FAQ Matching**: Uses TF-IDF vectorization and cosine similarity for accurate question matching
- **Multi-Interface Support**: Both Flask web interface and Streamlit dashboard
- **Real-time Chat**: Interactive chat interface with typing indicators and smooth animations
- **Analytics & Logging**: Comprehensive chat session and message tracking
- **Category-based Navigation**: Organized FAQ categories for better user experience
- **Sentiment Analysis**: Built-in sentiment analysis for user messages
- **OpenAI Integration**: Optional GPT integration for complex queries
- **Responsive Design**: Matrix-themed Aurora interface with modern styling

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **NLP**: NLTK, scikit-learn
- **Database**: PostgreSQL (production) / SQLite (development)
- **Optional**: OpenAI API, Streamlit
- **Deployment**: Gunicorn WSGI server

## 📋 Prerequisites

- Python 3.11 or higher
- pip package manager
- PostgreSQL (for production deployment)

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd aurora-chatbot
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the `.env.example` file to `.env` and configure your settings:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
- Set a strong `SECRET_KEY`
- Configure your database URL
- Add OpenAI API key if you want AI-enhanced responses

### 5. Initialize Database

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. Run the Application

For development:
```bash
python app.py
```

For production with Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

## 🚀 Deployment Options

### Heroku Deployment

1. Create a new Heroku app:
```bash
heroku create your-aurora-app
```

2. Add PostgreSQL addon:
```bash
heroku addons:create heroku-postgresql:mini
```

3. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set OPENAI_API_KEY=your-openai-key  # Optional
```

4. Deploy:
```bash
git push heroku main
```

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Vercel Deployment

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Configure environment variables in Vercel dashboard

### DigitalOcean App Platform

1. Create new app from GitHub repository
2. Configure environment variables
3. Deploy with automatic scaling

## 🔑 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Yes | - |
| `DATABASE_URL` | Database connection string | No | `sqlite:///aurora.db` |
| `OPENAI_API_KEY` | OpenAI API key for enhanced responses | No | - |
| `FLASK_ENV` | Flask environment (development/production) | No | `production` |
| `DEBUG` | Enable debug mode | No | `False` |
| `HOST` | Host to bind to | No | `0.0.0.0` |
| `PORT` | Port to bind to | No | `5000` |

## 📊 Database Setup

### Development (SQLite)
No additional setup required. Database file is created automatically.

### Production (PostgreSQL)

For PostgreSQL, ensure your `DATABASE_URL` follows this format:
```
postgresql://username:password@hostname:port/database_name
```

### Database Migration

The app automatically creates tables on first run. For manual setup:

```python
from app import app, db
with app.app_context():
    db.create_all()
```
