# Notion OAuth Setup Guide

## Overview
The Notion integration now uses OAuth, allowing each user to connect their own Notion account instead of using a shared secret key.

## Required Environment Variables

Add these to your `backend/.env` file:

```env
# Notion OAuth Configuration
NOTION_CLIENT_ID=your_notion_oauth_client_id
NOTION_CLIENT_SECRET=your_notion_oauth_client_secret
NOTION_REDIRECT_URI=http://localhost:8000/api/integrations/notion/callback

# Frontend URL (for OAuth callback redirect)
FRONTEND_URL=http://localhost:3000

# Backend URL (for OAuth callback)
BACKEND_URL=http://localhost:8000
```

## Setting Up Notion OAuth

1. **Create a Notion Integration:**
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Give it a name (e.g., "Aigis Marketing")
   - Select your workspace
   - Set the integration type to "Public" (for OAuth)
   - Copy the **OAuth client ID** and **OAuth client secret**

2. **Configure OAuth Redirect URI:**
   - In your Notion integration settings, add the redirect URI:
     - For local development: `http://localhost:8000/api/integrations/notion/callback`
     - For production: `https://your-backend-domain.com/api/integrations/notion/callback`

3. **Set Required Capabilities:**
   - Enable "Read content" capability
   - Enable "Read user information" capability

4. **Add Environment Variables:**
   - Add `NOTION_CLIENT_ID` and `NOTION_CLIENT_SECRET` to your `.env` file
   - Set `NOTION_REDIRECT_URI` to match your callback URL
   - Set `FRONTEND_URL` to your frontend URL
   - Set `BACKEND_URL` to your backend URL

## How It Works

1. User clicks "Connect Notion" in the Brand Context page
2. User is redirected to Notion's OAuth page
3. User authorizes the integration
4. Notion redirects back to `/api/integrations/notion/callback`
5. Backend exchanges the code for an access token
6. Backend saves the token to the database (user-specific)
7. User is redirected back to the Brand Context page
8. User can now see and import their own Notion pages

## Important Notes

- **Remove `NOTION_SECRET`**: The old internal integration token is no longer used. Remove it from your `.env` file.
- **Each user has their own connection**: Each user connects their own Notion account, so they only see their own pages.
- **Token storage**: User tokens are stored securely in the `integration_connections` table in the database.

## Troubleshooting

- **"Notion OAuth not configured"**: Make sure `NOTION_CLIENT_ID` and `NOTION_CLIENT_SECRET` are set in your `.env` file.
- **"Invalid redirect URI"**: Make sure the redirect URI in your Notion integration settings matches `NOTION_REDIRECT_URI` in your `.env` file.
- **"No pages found"**: Make sure the user has authorized the integration and has pages in their Notion workspace.









