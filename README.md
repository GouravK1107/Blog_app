# BlogApp - A Complete Django Blogging Platform

A feature-rich blogging platform built with Django that allows users to create, manage, and interact with blog posts, profiles, and social features.

## ✨ Features

### 👤 User Management
- Custom user profiles with bio, date of birth, and profile pictures
- Email verification system with OTP
- Multiple email address support
- Password change and reset functionality
- Account deletion with confirmation

### 📝 Blog Management
- Create, edit, delete blog posts
- Rich text content
- Category and tag system
- Blog image uploads
- Excerpts and full content
- Draft/publish toggle

### 🔍 Discoverability
- Public, followers-only, or private profile visibility options
- Trending blogs based on views
- Search blogs by title
- Filter by category
- Search users by name/username

### 💬 Social Features
- Like/unlike blog posts
- Nested comments with reply functionality
- Follow/unfollow users
- Follow requests for private profiles
- Real-time notification system for:
  - Likes
  - Comments
  - Replies
  - Follows
  - Follow requests
  - Trending blog alerts

### 📊 User Dashboard
- Personal blog management
- View stats: total blogs, likes, views, comments
- Profile settings and privacy controls

### 🔐 Security & Privacy
- Django authentication
- OTP-based email verification
- Session management
- Profile privacy controls

## 🛠️ Tech Stack

- **Backend:** Django 5.2
- **Database:** SQLite (development), PostgreSQL ready
- **Frontend:** HTML, CSS, JavaScript
- **Authentication:** Django Allauth with Google & GitHub OAuth
- **Email:** SMTP (Gmail)
- **File Storage:** Django media files
- **AJAX:** For like, comment, follow actions

## 📦 Installation

1. Clone the repository
```bash
git clone <your-repo-url>
cd blog_app
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install django django-allauth pillow
```

4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser
```bash
python manage.py createsuperuser
```

6. Run development server
```bash
python manage.py runserver
```

## 🔧 Configuration

### Environment Variables (Recommended)
Create a `.env` file with:
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
SECRET_KEY=your-django-secret-key
```

### Social Auth Setup
1. Google OAuth: Get credentials from Google Cloud Console
2. GitHub OAuth: Register OAuth app on GitHub
3. Update `SITE_ID` in settings.py

## 📁 Project Structure

```
blog_app/
├── blog/                    # Main blog app
│   ├── models.py            # Blog, Comment, Like, Follow models
│   ├── views.py             # All blog-related views
│   ├── urls.py              # Blog URL patterns
│   ├── forms.py             # Profile form
│   ├── utils.py             # OTP generation & email utilities
│   └── templates/blog/      # All HTML templates
├── user_account/            # User authentication app
│   ├── views.py             # Login/signup views
│   ├── urls.py              # Auth URLs
│   └── templates/account/   # Login/signup templates
└── blog_app/                # Project settings
    └── settings.py          # Main configuration
```

## 🌟 Key Features Explained

### 🔐 Authentication
- Custom login/signup with email instead of username
- Social login with Google and GitHub
- Session management and logout confirmation

### 📧 Email Verification
- OTP-based email verification
- Add multiple email addresses
- Set primary email
- Resend verification codes

### 👥 Following System
- Public profiles: direct follow
- Private profiles: follow requests need approval
- Follow/unfollow with AJAX
- Follow counts visible on profiles

### 🔔 Notifications
- Real-time notifications panel
- Mark all as read
- Clear all notifications
- Accept/reject follow requests from notifications

### 📱 Responsive Design
- Mobile-friendly interface
- Smooth modals for blog reading
- Filter and search functionality

## 👨‍💻 Author

Gourav K  
BCA Student | Backend & AI Enthusiast  
Focused on mastering Computer Vision & AI systems.

---

⭐ If you found this project useful, consider starring the repository!
