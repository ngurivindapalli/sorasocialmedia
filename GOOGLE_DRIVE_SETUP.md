# Google Drive OAuth Setup Guide

## Overview
The Google Drive integration uses OAuth, allowing each user to connect their own Google Drive account and import documents as brand context.

## Required Environment Variables

Add these to your `backend/.env` file:

```env
# Google Drive OAuth Configuration
GOOGLE_DRIVE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_DRIVE_CLIENT_SECRET=your_google_oauth_client_secret
GOOGLE_DRIVE_REDIRECT_URI=http://localhost:8000/api/integrations/google_drive/callback

# Frontend URL (for OAuth callback redirect)
FRONTEND_URL=http://localhost:3000

# Backend URL (for OAuth callback)
BACKEND_URL=http://localhost:8000
```

## Setting Up Google Drive OAuth

1. **Create a Google Cloud Project:**
   - Go to https://console.cloud.google.com/
   - Create a new project or select an existing one
   - Enable the Google Drive API:
     - Go to "APIs & Services" > "Library"
     - Search for "Google Drive API"
     - Click "Enable"

2. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application" as the application type
   - Add authorized redirect URIs:
     - For local development: `http://localhost:8000/api/integrations/google_drive/callback`
     - For production: `https://your-backend-domain.com/api/integrations/google_drive/callback`
   - Copy the **Client ID** and **Client Secret**

3. **Configure OAuth Consent Screen:**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" (unless you have a Google Workspace)
   - Fill in the required information:
     - App name: "Aigis Marketing"
     - User support email: your email
     - Developer contact: your email
   - Add scopes:
     - `https://www.googleapis.com/auth/drive.readonly`
     - `https://www.googleapis.com/auth/drive.metadata.readonly`
   - Add test users (for testing before publishing)

4. **Add Environment Variables:**
   - Add `GOOGLE_DRIVE_CLIENT_ID` and `GOOGLE_DRIVE_CLIENT_SECRET` to your `.env` file
   - Set `GOOGLE_DRIVE_REDIRECT_URI` to match your callback URL
   - Set `FRONTEND_URL` to your frontend URL
   - Set `BACKEND_URL` to your backend URL

## How It Works

1. User clicks "Connect Google Drive" in the Brand Context page
2. User is redirected to Google's OAuth page
3. User authorizes the integration
4. Google redirects back to `/api/integrations/google_drive/callback`
5. Backend exchanges the code for access and refresh tokens
6. Backend saves the tokens to the database (user-specific)
7. User is redirected back to the Brand Context page
8. User can now see and import files from their Google Drive

## Supported File Types

- **Google Docs** - Exported as plain text
- **Google Sheets** - Exported as CSV
- **Google Slides** - Exported as plain text
- **PDF files** - Downloaded directly
- **Text files** - Downloaded directly
- **Other document types** - Downloaded as binary (base64 encoded)

## Important Notes

- **Each user has their own connection**: Each user connects their own Google Drive account, so they only see their own files.
- **Token refresh**: The integration automatically refreshes expired tokens using the refresh token.
- **Read-only access**: The integration only requests read-only access to files.

## Troubleshooting

- **"Google Drive OAuth not configured"**: Make sure `GOOGLE_DRIVE_CLIENT_ID` and `GOOGLE_DRIVE_CLIENT_SECRET` are set in your `.env` file.
- **"Invalid redirect URI"**: Make sure the redirect URI in your Google Cloud Console matches `GOOGLE_DRIVE_REDIRECT_URI` in your `.env` file.
- **"No files found"**: Make sure the user has authorized the integration and has files in their Google Drive.
- **"Token expired"**: The integration should automatically refresh tokens. If not, the user may need to reconnect.






