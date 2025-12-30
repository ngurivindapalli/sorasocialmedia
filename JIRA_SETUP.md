# Jira OAuth Setup Guide

## Overview
The Jira integration uses OAuth 2.0, allowing each user to connect their own Jira Cloud account and import issues as brand context.

## Required Environment Variables

Add these to your `backend/.env` file:

```env
# Jira OAuth Configuration
JIRA_CLIENT_ID=your_jira_oauth_client_id
JIRA_CLIENT_SECRET=your_jira_oauth_client_secret
JIRA_REDIRECT_URI=http://localhost:8000/api/integrations/jira/callback

# Frontend URL (for OAuth callback redirect)
FRONTEND_URL=http://localhost:3000

# Backend URL (for OAuth callback)
BACKEND_URL=http://localhost:8000
```

## Setting Up Jira OAuth

1. **Create an Atlassian App:**
   - Go to https://developer.atlassian.com/console/myapps/
   - Click **"Create"** → **"New app"**
   - Choose **"OAuth 2.0 (3LO)"** as the authentication method
   - Give your app a name (e.g., "Aigis Marketing")
   - Set the app type to **"Web application"**

2. **Configure OAuth Settings:**
   - In your app settings, go to **"Authorization"** or **"OAuth 2.0 (3LO)"**
   - Add authorized callback URLs:
     - For local development: `http://localhost:8000/api/integrations/jira/callback`
     - For production: `https://your-backend-domain.com/api/integrations/jira/callback`
   - Set the scopes/permissions:
     - `read:jira-work` - Read Jira issues and work items
     - `read:jira-user` - Read user information
     - `offline_access` - Refresh tokens for long-lived access

3. **Get Your Credentials:**
   - In your app settings, find the **"Client ID"** and **"Client secret"**
   - Copy these values

4. **Add Environment Variables:**
   - Add `JIRA_CLIENT_ID` and `JIRA_CLIENT_SECRET` to your `.env` file
   - Set `JIRA_REDIRECT_URI` to match your callback URL
   - Set `FRONTEND_URL` to your frontend URL
   - Set `BACKEND_URL` to your backend URL

5. **Request App Installation (for production):**
   - For production use, you'll need to request installation approval from Atlassian
   - Go to your app's **"Distribution"** section
   - Submit your app for review if you want it publicly available
   - For testing, you can install it directly in your own Jira instance

## How It Works

1. User clicks "Connect Jira" in the Brand Context page
2. User is redirected to Atlassian's OAuth page
3. User authorizes the integration and selects their Jira site
4. Atlassian redirects back to `/api/integrations/jira/callback`
5. Backend exchanges the code for access and refresh tokens
6. Backend gets the list of accessible Jira sites (cloud IDs)
7. Backend saves the tokens and cloud ID to the database (user-specific)
8. User is redirected back to the Brand Context page
9. User can now see and import issues from their Jira workspace

## Supported Features

- **List Issues**: Search and list Jira issues using JQL (Jira Query Language)
- **Import Issues**: Import issue content including:
  - Summary and description
  - Status, project, issue type, priority
  - Assignee and reporter information
  - Comments
  - Created and updated timestamps
- **Token Refresh**: Automatic token refresh using refresh tokens
- **Multi-Site Support**: Works with any Jira Cloud site the user has access to

## JQL Query Examples

You can use JQL (Jira Query Language) to filter issues when listing:

- `ORDER BY updated DESC` - Most recently updated issues (default)
- `project = "PROJ" AND status = "In Progress"` - Issues in a specific project and status
- `assignee = currentUser() AND status != Done` - Your open issues
- `created >= -30d` - Issues created in the last 30 days
- `text ~ "keyword"` - Issues containing a keyword

## Important Notes

- **Each user has their own connection**: Each user connects their own Jira account, so they only see their own issues.
- **Token refresh**: The integration automatically refreshes expired tokens using the refresh token.
- **Read-only access**: The integration only requests read-only access to issues.
- **Cloud ID**: The integration stores the Jira Cloud ID (site ID) during OAuth to identify which Jira instance to use.
- **Issue Keys**: When importing, use issue keys (e.g., "PROJ-123") not issue IDs.

## Troubleshooting

- **"Jira OAuth not configured"**: Make sure `JIRA_CLIENT_ID` and `JIRA_CLIENT_SECRET` are set in your `.env` file.
- **"Invalid redirect URI"**: Make sure the redirect URI in your Atlassian app settings matches `JIRA_REDIRECT_URI` in your `.env` file.
- **"No accessible Jira sites found"**: Make sure the user has access to at least one Jira Cloud site and has authorized the app.
- **"Jira cloud ID not found"**: The connection may be corrupted. Try disconnecting and reconnecting.
- **"Token expired"**: The integration should automatically refresh tokens. If not, the user may need to reconnect.
- **"No issues found"**: Check your JQL query if you're using one, or verify the user has issues in their Jira workspace.

## Production Deployment

When deploying to production:

1. Update `JIRA_REDIRECT_URI` in your production environment to your production backend URL
2. Add the production callback URL to your Atlassian app's authorized callback URLs
3. Update `FRONTEND_URL` and `BACKEND_URL` to your production URLs
4. If your app is not yet approved for public distribution, users will need to install it manually in their Jira instance

## API Endpoints

- `GET /api/integrations/jira/authorize` - Initiate OAuth flow
- `GET /api/integrations/jira/callback` - Handle OAuth callback
- `GET /api/integrations/jira/issues?jql=...` - List issues (optional JQL query)
- `POST /api/integrations/import` - Import issues to Hyperspell (use issue keys in `item_ids`)





