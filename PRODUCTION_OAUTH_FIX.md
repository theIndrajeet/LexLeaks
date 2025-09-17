# Production OAuth Configuration Fix

## 🚨 Problem
When users visit `lexleaks.com` and try to login with Google, the OAuth flow redirects to `localhost` instead of the production server, causing the login to fail.

## 🔍 Root Cause
The Google OAuth configuration is set up for localhost development, but the production site needs different redirect URIs.

## ✅ Solution

### Step 1: Update Google OAuth Console (CRITICAL)
1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Select project: `563011146464`
3. Navigate to "Credentials" → "OAuth 2.0 Client IDs"
4. Edit your OAuth client
5. Add this redirect URI:
   ```
   https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/callback
   ```

### Step 2: Current OAuth Configuration
- **Client ID**: `563011146464-amf1oanmakqldefn1g6j7oh0mh6ejlbd.apps.googleusercontent.com`
- **Current redirect**: `http://localhost:3000/auth/callback` (WRONG for production)
- **Should be**: `https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/callback`

### Step 3: Environment Variables
The backend needs these environment variables set in Cloud Run:
```bash
FRONTEND_URL=https://lexleaks.com
GOOGLE_REDIRECT_URI=https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/callback
```

### Step 4: OAuth Flow
1. User visits: `https://lexleaks.com`
2. Clicks "Continue with Google"
3. Redirects to Google OAuth
4. Google redirects to: `https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/callback`
5. Backend processes and redirects to: `https://lexleaks.com/auth/callback`
6. Frontend completes authentication

## 🛠️ Files Updated
- `backend-api/app/google_oauth.py` - Updated default redirect URI
- `backend-api/.env.production` - Production environment variables
- `update_production_oauth.sh` - Script to update Cloud Run env vars

## 🚀 Quick Fix Commands
```bash
# Test current OAuth endpoint
curl https://lexleaks-api-563011146464.asia-south1.run.app/api/auth/google/login

# Update Cloud Run environment variables (if gcloud is configured)
./update_production_oauth.sh
```

## ⚠️ Important Notes
1. **Google OAuth Console must be updated first** - this is the most critical step
2. The Cloud Run deployment may need to be redeployed with correct environment variables
3. Both localhost and production redirect URIs should be configured in Google OAuth Console for development and production use

## 🎯 Expected Result
After completing these steps, users visiting `lexleaks.com` will be able to login with Google successfully, and the OAuth flow will work properly on the production server instead of trying to redirect to localhost.
