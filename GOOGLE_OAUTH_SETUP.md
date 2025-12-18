# Google OAuth Setup Guide

## The Issue
Google login is not working because OAuth credentials are not configured in Replit.

## Solution: Set Up Google OAuth

### Step 1: Create Google OAuth Credentials

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create or Select a Project:**
   - Click the project dropdown at the top
   - Click "New Project" or select existing project
   - Name it: "OppGrid" or "Project-Spark"

3. **Enable Google+ API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. **Create OAuth Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID"
   
5. **Configure OAuth Consent Screen (if first time):**
   - Click "CONFIGURE CONSENT SCREEN"
   - Select "External" (unless you have Google Workspace)
   - Click "Create"
   - Fill in:
     - App name: **OppGrid**
     - User support email: **your-email@gmail.com**
     - Developer contact: **your-email@gmail.com**
   - Click "Save and Continue"
   - Skip "Scopes" (click "Save and Continue")
   - Skip "Test users" (click "Save and Continue")

6. **Create OAuth Client ID:**
   - Application type: **Web application**
   - Name: **OppGrid Web Client**
   
7. **Add Authorized Redirect URIs:**
   - Click "+ Add URI" under "Authorized redirect URIs"
   - Add these URLs (replace with your actual Replit URL):
   
   ```
   https://your-repl-name.your-username.repl.co/api/v1/oauth/google/callback
   http://localhost:8000/api/v1/oauth/google/callback
   ```
   
   To find your Replit URL:
   - Open your Repl
   - Click the "Open in new tab" button
   - Copy the URL (it looks like: `https://xxxxx.replit.dev`)

8. **Save and Copy Credentials:**
   - Click "Create"
   - Copy the **Client ID** (starts with numbers, ends with `.apps.googleusercontent.com`)
   - Copy the **Client Secret** (random string)
   - Click "OK"

### Step 2: Configure Replit Secrets

1. **In your Replit project:**
   - Click the lock icon 🔒 in the left sidebar (or Tools → Secrets)

2. **Add Google OAuth credentials:**
   - Click "+ New Secret"
   - Key: `GOOGLE_CLIENT_ID`
   - Value: Paste your Client ID
   - Click "Add Secret"

   - Click "+ New Secret" again
   - Key: `GOOGLE_CLIENT_SECRET`
   - Value: Paste your Client Secret
   - Click "Add Secret"

### Step 3: Restart and Test

1. **Stop your Repl** (click the Stop button)

2. **Start your Repl** (click the Run button)

3. **Test Google Login:**
   - Go to your app URL
   - Click "Continue with Google"
   - You should be redirected to Google's login page
   - After signing in, you'll be redirected back to your app

### Step 4: Verify Configuration

Run this in the Replit Shell to verify:

```bash
python -c "import os; print('Google Client ID:', 'SET' if os.getenv('GOOGLE_CLIENT_ID') else 'NOT SET'); print('Google Client Secret:', 'SET' if os.getenv('GOOGLE_CLIENT_SECRET') else 'NOT SET')"
```

Expected output:
```
Google Client ID: SET
Google Client Secret: SET
```

---

## Troubleshooting

### Error: "Access blocked: This app's request is invalid"

**Cause:** Redirect URI mismatch

**Fix:**
1. Go back to Google Cloud Console → Credentials
2. Click your OAuth client ID
3. Make sure the redirect URI EXACTLY matches your Replit URL
4. Format: `https://YOUR-REPL-URL/api/v1/oauth/google/callback`
5. Save and try again

### Error: "redirect_uri_mismatch"

**Cause:** The redirect URI in Replit doesn't match what's in Google Console

**Fix:**
1. Check your Replit URL (it may have changed)
2. Update the redirect URI in Google Cloud Console
3. Format must be: `https://xxxxx.replit.dev/api/v1/oauth/google/callback`

### Error: "Invalid client"

**Cause:** Wrong Client ID or Client Secret

**Fix:**
1. Go to Google Cloud Console → Credentials
2. Click your OAuth client ID
3. Copy the Client ID again (click the copy icon)
4. Click "Download JSON" to get the secret
5. Update Replit Secrets with correct values

### Google Login Button Does Nothing

**Cause:** Backend server not running

**Fix:**
1. Check Replit console for errors
2. Make sure `python server.py` is running
3. Check database is initialized: `cd backend && python init_db.py`

### Error: "Google login not configured"

**Cause:** Secrets not set or server not restarted

**Fix:**
1. Verify secrets are set (see Step 4 above)
2. Stop and restart your Repl
3. Check server logs for configuration errors

---

## GitHub OAuth (Optional)

To also enable GitHub login, follow similar steps:

### GitHub Setup:

1. **Go to GitHub Settings:**
   - Visit: https://github.com/settings/developers

2. **Create OAuth App:**
   - Click "OAuth Apps" → "New OAuth App"
   - Application name: **OppGrid**
   - Homepage URL: Your Replit URL
   - Authorization callback URL: `https://YOUR-REPL-URL/api/v1/oauth/github/callback`
   - Click "Register application"

3. **Copy Credentials:**
   - Copy the **Client ID**
   - Click "Generate a new client secret"
   - Copy the **Client Secret**

4. **Add to Replit Secrets:**
   - `GITHUB_CLIENT_ID` = Your GitHub Client ID
   - `GITHUB_CLIENT_SECRET` = Your GitHub Client Secret

5. **Restart Repl** and test

---

## Testing Checklist

- [ ] Google OAuth credentials created in Google Cloud Console
- [ ] Redirect URI matches your Replit URL exactly
- [ ] `GOOGLE_CLIENT_ID` set in Replit Secrets
- [ ] `GOOGLE_CLIENT_SECRET` set in Replit Secrets
- [ ] Repl restarted after adding secrets
- [ ] Server running (`python server.py`)
- [ ] Database initialized (`backend/init_db.py`)
- [ ] "Continue with Google" button opens Google login page
- [ ] After Google login, redirects back to discover.html

---

## Security Notes

- **Never commit** OAuth credentials to Git
- Use **different credentials** for development and production
- Keep your **Client Secret** secure
- Regularly rotate secrets if compromised
- For production, move from "Testing" to "In Production" in Google Console

---

## Support

If you're still having issues, provide:
1. The exact error message you see
2. Browser console output (F12 → Console tab)
3. Replit console output
4. Screenshot of your Google Cloud Console redirect URI settings
