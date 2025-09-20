# 🧪 LexLeaks Notification Test Setup

## Quick Test Steps

### 1. Configure VAPID Keys
Add these to your backend `.env` file:
```env
VAPID_PUBLIC_KEY=BBzBPZHNrYd4yMkW5THmC2vPYHfausBF5_eCaql-9eo8c0Y2ibr6O0znOXLZ7zAs9qSYf1GfHJIcaKF1XWo5BMY
VAPID_PRIVATE_KEY=gc-RA0w3RET4Zyd4HGAnk-L_KFtRO61NtxGO8f849xQ
```

### 2. Start Your Backend
```bash
cd backend-api
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Test VAPID Key Configuration
```bash
curl http://localhost:8000/api/notifications/vapid-key
```
Should return: `{"publicKey": "BBzBPZHNrYd4yMkW5THmC2vPYHfausBF5_eCaql-9eo8c0Y2ibr6O0znOXLZ7zAs9qSYf1GfHJIcaKF1XWo5BMY"}`

### 4. Get Admin Token
Login to your admin account and get the JWT token from the response.

### 5. Run the Test Script
```bash
python test_notification.py
```

### 6. Alternative: Manual Test
```bash
curl -X POST "http://localhost:8000/api/notifications/test/2" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Expected Results

### Success Response:
```json
{
  "sent_count": 1,
  "failed_count": 0,
  "success": true
}
```

### Test Notification Content:
- **Title**: "👥 Community Update - LexLeaks"
- **Body**: "🚀 Test notification from LexLeaks! Your push notifications are working perfectly."
- **Style**: "community"

## Troubleshooting

### If VAPID key fails:
- Check your `.env` file has the correct keys
- Restart your backend server
- Verify the keys are loaded: `curl http://localhost:8000/api/notifications/vapid-key`

### If no push subscriptions:
- Visit your frontend and allow notifications
- Check the browser console for subscription errors
- Verify HTTPS is working (required for push notifications)

### If test fails:
- Check backend logs for errors
- Verify user ID 2 exists in database
- Check if pywebpush is installed: `pip list | grep pywebpush`

## Database Check
```sql
-- Check users
SELECT id, username, email FROM users;

-- Check push subscriptions
SELECT ps.id, ps.user_id, ps.endpoint, ps.is_active, u.email 
FROM push_subscriptions ps 
LEFT JOIN users u ON ps.user_id = u.id;

-- Check sent notifications
SELECT * FROM notifications_sent ORDER BY sent_at DESC LIMIT 5;
```
