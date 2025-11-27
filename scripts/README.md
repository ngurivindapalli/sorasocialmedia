# Manual Posting Scripts

These scripts allow you to post videos to Instagram and LinkedIn using browser automation. Your credentials are used locally and never sent to any server.

## Installation

1. **Install Python** (if not already installed)

2. **Install Playwright**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

## Usage

### Instagram

```bash
python scripts/instagram_manual_poster.py --username YOUR_USERNAME --video path/to/video.mp4 --caption "Your caption"
```

**Shorthand:**
```bash
python scripts/instagram_manual_poster.py -u YOUR_USERNAME -v ./video.mp4 -c "Your caption"
```

### LinkedIn

```bash
python scripts/linkedin_manual_poster.py --username YOUR_EMAIL --video path/to/video.mp4 --caption "Your caption"
```

**Shorthand:**
```bash
python scripts/linkedin_manual_poster.py -u user@example.com -v ./video.mp4 -c "Your caption"
```

## How It Works

1. Opens a browser window (you can see what's happening)
2. Logs into Instagram/LinkedIn with your credentials
3. Creates a new post
4. Uploads your video
5. Adds your caption
6. Posts the video

## Important Notes

- ✅ **Secure**: Your password is only entered locally, never stored or sent anywhere
- ✅ **Visible**: Browser window opens so you can see the process
- ✅ **Simple**: Just provide username, video path, and caption
- ⚠️ **Manual**: You may need to help with some steps if the page structure changes
- ⚠️ **Rate Limits**: Don't use too frequently to avoid account restrictions

## Troubleshooting

### "Playwright not found"
```bash
pip install playwright
playwright install chromium
```

### "Video file not found"
Make sure the video path is correct. Use absolute path if relative doesn't work.

### "Login failed"
- Check your credentials
- Make sure 2FA is disabled (or use an app password)
- Try logging in manually first to ensure account isn't locked

### Script can't find buttons
- Instagram/LinkedIn may have updated their interface
- The browser window will stay open so you can complete the post manually
- Update the selectors in the script if needed

## Security

These scripts:
- ✅ Run entirely on your computer
- ✅ Never send your password to any server
- ✅ Only use credentials to log in through the official website
- ✅ Use browser automation (Playwright) that you control

## Alternatives

If browser automation doesn't work for you:
1. Use manual token entry (Instagram - already supported in VideoHook)
2. Use OAuth once to get a long-lived token
3. Use the official mobile/desktop apps to post manually



