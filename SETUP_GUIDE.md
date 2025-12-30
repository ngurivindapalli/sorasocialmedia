# VideoHook Setup Guide

This guide will help you set up the social media posting and email notification features.

## Features Added

1. **Social Media Account Linking**: Connect Instagram, LinkedIn, X (Twitter), and TikTok accounts via OAuth
2. **Video Posting**: Post generated videos directly to connected social media accounts
3. **Email Notifications**: Receive email notifications when videos are posted

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here_optional

# Database Configuration
DATABASE_URL=sqlite:///./videohook.db

# JWT Secret Key (change this in production!)
JWT_SECRET_KEY=your-secret-key-change-in-production

# Base URL for OAuth callbacks
BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Instagram OAuth (Facebook Graph API)
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret

# LinkedIn OAuth
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

# X (Twitter) OAuth
X_CLIENT_ID=your_x_client_id
X_CLIENT_SECRET=your_x_client_secret

# TikTok OAuth
TIKTOK_CLIENT_ID=your_tiktok_client_id
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret

# Email Configuration (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=your_email@gmail.com
FROM_NAME=VideoHook
```

### 3. OAuth App Setup

#### Instagram (Facebook Graph API)
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Instagram Basic Display and Instagram Graph API products
4. Get Client ID and Client Secret
5. Add redirect URI: `http://localhost:8000/api/oauth/instagram/callback`

#### LinkedIn
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create a new app
3. Get Client ID and Client Secret
4. Add redirect URI: `http://localhost:8000/api/oauth/linkedin/callback`
5. Request `w_member_social` scope

#### X (Twitter)
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app
3. Enable OAuth 2.0
4. Get Client ID and Client Secret
5. Add redirect URI: `http://localhost:8000/api/oauth/x/callback`

#### TikTok
1. Go to [TikTok Developers](https://developers.tiktok.com/)
2. Create a new app
3. Get Client Key and Client Secret
4. Add redirect URI: `http://localhost:8000/api/oauth/tiktok/callback`

### 4. Email Setup (Gmail Example)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. Use this app password as `SMTP_PASSWORD`

### 5. Initialize Database

The database will be automatically created when you start the backend server. The SQLite database file will be created at `backend/videohook.db`.

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Variables (Optional)

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Start Backend

```bash
cd backend
python main.py
```

### Start Frontend

```bash
cd frontend
npm run dev
```

## Usage

### 1. Create Account

- Sign up with username, email, and password
- Email is required for notifications

### 2. Connect Social Media Accounts

- Go to Settings → Social Media Connections
- Click "Connect" for each platform you want to use
- Authorize the app on each platform

### 3. Post Videos

- After generating a video, click "Post to Social Media"
- Select which accounts to post to
- Add a caption (optional)
- Click "Post Video"

### 4. Email Notifications

- Email notifications are enabled by default
- Toggle them in Settings → Email Notifications
- You'll receive an email when a video is successfully posted

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### OAuth
- `GET /api/oauth/{platform}/authorize` - Initiate OAuth flow
- `GET /api/oauth/{platform}/callback` - OAuth callback

### Connections
- `GET /api/connections` - Get all connections
- `DELETE /api/connections/{id}` - Disconnect account

### Posting
- `POST /api/post/video` - Post video to social media
- `GET /api/posts/history` - Get post history

### Settings
- `PUT /api/user/email-notifications` - Update email preferences

## Notes

- OAuth tokens are stored in the database (encrypt in production!)
- Email notifications require SMTP configuration
- Some platforms may require additional API permissions
- Video URLs must be publicly accessible for posting

## Troubleshooting

### OAuth Issues
- Ensure redirect URIs match exactly
- Check that OAuth apps are approved (some platforms require approval)
- Verify client IDs and secrets are correct

### Email Issues
- Check SMTP credentials
- For Gmail, ensure App Password is used (not regular password)
- Check spam folder for notifications

### Database Issues
- Delete `videohook.db` to reset database
- Ensure SQLite is installed

## Production Considerations

1. **Security**:
   - Use strong JWT_SECRET_KEY
   - Encrypt OAuth tokens in database
   - Use HTTPS for OAuth callbacks
   - Implement rate limiting

2. **Database**:
   - Use PostgreSQL instead of SQLite
   - Set up database backups
   - Use connection pooling

3. **Email**:
   - Use professional email service (SendGrid, AWS SES)
   - Set up SPF/DKIM records
   - Monitor email delivery

4. **OAuth**:
   - Store OAuth states in Redis (not in-memory)
   - Implement token refresh
   - Handle token expiration





























