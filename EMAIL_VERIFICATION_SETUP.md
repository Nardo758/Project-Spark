# Email Verification Setup Guide

## Overview

The application now includes a complete email verification system using Resend API. Users must verify their email addresses after registration.

## Features

✅ **Registration Flow**
- New users receive a verification email immediately after signup
- Verification token expires after 24 hours
- Users marked as unverified until email is confirmed

✅ **Email Templates**
- Professional HTML email templates
- Branded with Friction theme colors
- Mobile-responsive design
- Plain text fallback

✅ **Endpoints**
- `POST /api/v1/auth/register` - Register and send verification email
- `POST /api/v1/auth/verify-email` - Verify email with token
- `POST /api/v1/auth/resend-verification` - Resend verification email

## Resend Setup

### 1. Create a Resend Account

1. Go to [https://resend.com](https://resend.com)
2. Sign up for a free account
3. Verify your email address

### 2. Get Your API Key

1. Log into your Resend dashboard
2. Navigate to **API Keys**
3. Click **Create API Key**
4. Give it a name (e.g., "Friction Production")
5. Copy the API key (starts with `re_`)

### 3. Configure Domain (Optional but Recommended)

**For Development:**
- Use the default sending domain (resend.dev)
- Emails will come from `onboarding@resend.dev`

**For Production:**
1. Navigate to **Domains** in Resend dashboard
2. Click **Add Domain**
3. Enter your domain (e.g., `friction.app`)
4. Add the DNS records Resend provides to your domain registrar
5. Wait for verification (usually 5-15 minutes)
6. Update `FROM_EMAIL` in your `.env` file

### 4. Set Environment Variables

Add these to your `.env` file:

```bash
# Email Configuration (Resend)
RESEND_API_KEY=re_your_actual_api_key_here
FROM_EMAIL=noreply@yourdomain.com

# Frontend URL (for verification links)
FRONTEND_URL=http://localhost:3000  # Change for production
```

### 5. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Testing Email Verification

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

### 2. Check Your Email

- Check the inbox for the email you registered with
- Look for an email from your configured `FROM_EMAIL`
- Subject: "Verify your email address - Friction"

### 3. Verify Email

Option A: Click the button in the email

Option B: Make API call with token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "token": "your_verification_token_here"
  }'
```

### 4. Resend Verification (if needed)

```bash
curl -X POST http://localhost:8000/api/v1/auth/resend-verification \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

## Email Templates

The system includes two email templates:

### Verification Email
- Sent immediately after registration
- Contains verification link that expires in 24 hours
- Styled with Friction branding

### Password Reset Email
- Ready for future implementation
- Contains reset link that expires in 1 hour
- Includes security warnings

## Database Schema

New fields added to `users` table:

```sql
- verification_token: VARCHAR(255) - Unique token for email verification
- verification_token_expires: TIMESTAMP - Token expiration time
- is_verified: BOOLEAN - Email verification status
```

## Security Features

✅ **Token Security**
- Tokens generated using `secrets.token_urlsafe(32)`
- 32-byte random tokens (43 characters URL-safe)
- Stored hashed in database

✅ **Expiration**
- Verification tokens expire after 24 hours
- Expired tokens cannot be used
- Users must request new token if expired

✅ **Rate Limiting** (Recommended)
- Consider adding rate limiting to resend endpoint
- Prevent email spam abuse

## Troubleshooting

### Email Not Receiving

1. **Check Resend Dashboard**
   - View **Logs** section
   - Check if email was sent successfully
   - Look for delivery errors

2. **Check Spam Folder**
   - Verification emails may land in spam initially
   - Mark as "Not Spam" to whitelist

3. **Verify API Key**
   - Ensure `RESEND_API_KEY` is correct
   - Check for extra spaces or quotes
   - Regenerate key if needed

4. **Check Domain Configuration**
   - For custom domains, verify DNS records
   - Use Resend's DNS verification tool
   - Allow time for DNS propagation

### Token Expired

```bash
# Resend verification email
curl -X POST http://localhost:8000/api/v1/auth/resend-verification \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Invalid Token Error

- Token may have been used already
- User might be already verified
- Token may have expired
- Request a new verification email

## Production Checklist

- [ ] Set up custom domain in Resend
- [ ] Configure DNS records for domain
- [ ] Update `FROM_EMAIL` to use custom domain
- [ ] Set `FRONTEND_URL` to production URL
- [ ] Secure `RESEND_API_KEY` in environment variables
- [ ] Test email delivery to various providers (Gmail, Outlook, etc.)
- [ ] Set up email monitoring/alerts in Resend dashboard
- [ ] Configure SPF, DKIM, DMARC records for better deliverability
- [ ] Add rate limiting to resend endpoint
- [ ] Set up email analytics tracking

## API Endpoints Reference

### POST /auth/register
Register new user and send verification email

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe",
  "bio": "Optional bio"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### POST /auth/verify-email
Verify email with token

**Request:**
```json
{
  "token": "verification_token_here"
}
```

**Response:**
```json
{
  "message": "Email verified successfully",
  "email": "user@example.com"
}
```

### POST /auth/resend-verification
Resend verification email

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Verification email sent successfully"
}
```

## Cost Considerations

**Resend Free Tier:**
- 3,000 emails/month
- 100 emails/day
- Perfect for development and small projects

**Paid Plans:**
- Start at $20/month for 50,000 emails
- Volume discounts available
- See [Resend Pricing](https://resend.com/pricing)

## Next Steps

1. Set up Resend account and API key
2. Configure environment variables
3. Test email verification flow
4. Implement frontend verification page
5. Add email verification requirement to protected routes
6. Consider adding password reset functionality (template already included)

## Support

- **Resend Documentation:** https://resend.com/docs
- **Resend Status:** https://status.resend.com
- **Support:** support@resend.com
