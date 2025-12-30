# Integrations Guide: Notion, Google Drive, and Jira

This guide explains how to integrate and use Notion, Google Drive, and Jira with the Aigis Marketing platform.

## Overview

All three integrations follow the same OAuth 2.0 pattern:
1. User initiates connection from the Brand Context page
2. OAuth flow redirects to the service provider
3. User authorizes the application
4. Callback saves tokens to the database
5. User can import content as brand context

## Quick Setup Checklist

### Notion
- [ ] Create Notion OAuth app at https://www.notion.so/my-integrations
- [ ] Get `NOTION_CLIENT_ID` and `NOTION_CLIENT_SECRET`
- [ ] Set `NOTION_REDIRECT_URI` in `.env`
- [ ] See `NOTION_OAUTH_SETUP.md` for details

### Google Drive
- [ ] Create Google Cloud project
- [ ] Enable Google Drive API
- [ ] Create OAuth 2.0 credentials
- [ ] Get `GOOGLE_DRIVE_CLIENT_ID` and `GOOGLE_DRIVE_CLIENT_SECRET`
- [ ] Set `GOOGLE_DRIVE_REDIRECT_URI` in `.env`
- [ ] See `GOOGLE_DRIVE_SETUP.md` for details

### Jira
- [ ] Create Atlassian app at https://developer.atlassian.com/console/myapps/
- [ ] Configure OAuth 2.0 (3LO)
- [ ] Get `JIRA_CLIENT_ID` and `JIRA_CLIENT_SECRET`
- [ ] Set `JIRA_REDIRECT_URI` in `.env`
- [ ] See `JIRA_SETUP.md` for details

## Environment Variables

Add all these to your `backend/.env` file:

```env
# Notion
NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret
NOTION_REDIRECT_URI=http://localhost:8000/api/integrations/notion/callback

# Google Drive
GOOGLE_DRIVE_CLIENT_ID=your_google_client_id
GOOGLE_DRIVE_CLIENT_SECRET=your_google_client_secret
GOOGLE_DRIVE_REDIRECT_URI=http://localhost:8000/api/integrations/google_drive/callback

# Jira
JIRA_CLIENT_ID=your_jira_client_id
JIRA_CLIENT_SECRET=your_jira_client_secret
JIRA_REDIRECT_URI=http://localhost:8000/api/integrations/jira/callback

# Common
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

## API Endpoints

### Authorization (All Platforms)
```
GET /api/integrations/{platform}/authorize
```
- Platforms: `notion`, `google_drive`, `jira`
- Returns: `{auth_url: string, state: string}`

### Callback (All Platforms)
```
GET /api/integrations/{platform}/callback?code=...&state=...
```
- Handles OAuth callback
- Saves tokens to database
- Redirects to frontend

### List Connections
```
GET /api/integrations
```
- Returns all active integrations for current user

### List Items

**Notion:**
```
GET /api/integrations/notion/pages
```
- Returns list of Notion pages

**Google Drive:**
```
GET /api/integrations/google-drive/files?mime_type=...
```
- Returns list of Google Drive files
- Optional `mime_type` filter

**Jira:**
```
GET /api/integrations/jira/issues?jql=...
```
- Returns list of Jira issues
- Optional `jql` query parameter for filtering

### Import Content
```
POST /api/integrations/import
```
Body:
```json
{
  "integration_id": 1,
  "item_ids": ["page-id-1", "page-id-2"],
  "collection": "documents"
}
```

- **Notion**: `item_ids` are page IDs
- **Google Drive**: `item_ids` are file IDs
- **Jira**: `item_ids` are issue keys (e.g., "PROJ-123")

### Disconnect
```
DELETE /api/integrations/{integration_id}
```
- Deactivates an integration connection

## What Gets Imported

### Notion
- Page title
- All page content (headings, paragraphs, lists, etc.)
- Formatted as markdown

### Google Drive
- Google Docs → Plain text
- Google Sheets → CSV
- Google Slides → Plain text
- PDFs → Binary (base64)
- Other files → Binary (base64)

### Jira
- Issue summary (title)
- Description (converted from ADF to markdown)
- Status, project, issue type, priority
- Assignee and reporter
- All comments
- Created and updated timestamps

## Use Cases

### Brand Context
Import documents, pages, and issues to build comprehensive brand context for:
- Marketing post generation
- Video script creation
- Content personalization
- Competitor analysis

### Content Discovery
- Find relevant Notion pages for content ideas
- Access Google Drive documents for reference
- Review Jira issues for product updates and features

### Automated Workflows
- Import product requirements from Jira
- Use brand guidelines from Google Drive
- Reference content strategy from Notion

## Token Management

All integrations support:
- **Access tokens**: Short-lived (typically 1 hour)
- **Refresh tokens**: Long-lived (for automatic renewal)
- **Automatic refresh**: Tokens are refreshed automatically when expired
- **User-specific**: Each user has their own tokens

## Security Notes

- Tokens are stored in the database (encrypt in production)
- OAuth state tokens prevent CSRF attacks
- Each user only sees their own content
- Read-only access requested (no write permissions)

## Troubleshooting

### Common Issues

1. **"OAuth not configured"**
   - Check environment variables are set
   - Verify client ID and secret are correct

2. **"Invalid redirect URI"**
   - Ensure redirect URI in service provider matches `.env`
   - Check for trailing slashes or protocol mismatches

3. **"No items found"**
   - Verify user has authorized the integration
   - Check user has content in their account
   - For Jira, verify JQL query is correct

4. **"Token expired"**
   - Integration should auto-refresh
   - If persistent, user may need to reconnect

5. **"Connection not found"**
   - User may have disconnected
   - Check integration is active in database

## Production Deployment

For production:

1. Update all redirect URIs to production URLs
2. Add production callback URLs to each service provider
3. Update `FRONTEND_URL` and `BACKEND_URL` in production environment
4. Enable token encryption in database
5. Set up proper CORS configuration
6. Request app approval if needed (especially for Jira)

## Next Steps

1. Set up each integration following their respective guides
2. Test OAuth flows in development
3. Import sample content to verify functionality
4. Deploy to production with updated URLs
5. Monitor token refresh and error logs

For detailed setup instructions, see:
- `NOTION_OAUTH_SETUP.md`
- `GOOGLE_DRIVE_SETUP.md`
- `JIRA_SETUP.md`





