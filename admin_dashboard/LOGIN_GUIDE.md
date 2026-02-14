# Login Guide - HR Recruitment System

## 🔐 Login Methods

This system has **two different login methods** depending on your role:

---

## 1️⃣ Staff Login (Admin, HR, Interviewer)

**URL:** `http://localhost:5173/login` or `http://YOUR_IP:5173/login`

### Default Credentials:

| Role | Email | Password |
|------|-------|----------|
| **Super Admin** | admin@admin.com | password123 |
| **HR Manager** | hr@admin.com | password123 |
| **Interviewer** | interviewer@admin.com | password123 |

### How to Login:
1. Navigate to `/login` page
2. Enter your **email** and **password**
3. Click "Sign In"
4. You'll be redirected to the dashboard

### Staff Permissions:
- **Super Admin**: Full system access, user management, all features
- **HR Manager**: Job postings, candidate management, interview scheduling
- **Interviewer**: Interview access, candidate evaluation

---

## 2️⃣ Candidate Login (Interview Participants)

**URL:** `http://localhost:5173/interview` or `http://YOUR_IP:5173/interview`

### No Password Required! 🎯

Candidates authenticate using **only their name** - no email or password needed.

### How to Login:
1. Navigate to `/interview` page
2. Enter your **full name** (exactly as provided to HR)
3. Click "Authenticate"
4. If you have a scheduled interview, you'll be connected

### Requirements:
- ✅ Your interview must be scheduled by HR
- ✅ Your name must match what HR entered in the system
- ✅ Interview status must be "SCHEDULED" or "IN_PROGRESS"
- ✅ You must be in one of these candidate statuses:
  - SCHEDULED
  - EMAIL_SENT
  - APPROVED

### Example:
If HR scheduled an interview for "John Smith", the candidate simply enters:
```
Name: John Smith
```

---

## 🔧 Troubleshooting

### Staff Login Issues:

**Problem:** "Login failed. Please check your credentials."

**Solutions:**
1. Verify you're using the correct email and password
2. Make sure backend server is running (`python main.py`)
3. Check backend logs for errors
4. Verify database is connected (MongoDB should be running)
5. Try restarting the backend server

**Problem:** "OPTIONS /auth/login 400 Bad Request"

**Solutions:**
1. Backend has been updated to handle CORS properly
2. Restart backend server to apply fixes
3. Clear browser cache and try again

---

### Candidate Login Issues:

**Problem:** "No scheduled interview found for this name"

**Solutions:**
1. Verify your name spelling matches what HR entered
2. Check that HR has scheduled your interview
3. Contact HR to verify your interview status

**Problem:** "No active interview found for this candidate"

**Solutions:**
1. Your interview may have already been completed
2. Interview may not be scheduled yet
3. Contact HR to reschedule

---

## 🌐 Network Access

If accessing from another computer on the same network:

### Staff Login:
```
http://10.224.16.49:5173/login
```

### Candidate Interview:
```
http://10.224.16.49:5173/interview
```

**Note:** Replace `10.224.16.49` with your actual server IP address

---

## 🚀 Quick Start

### For Administrators:
```bash
# 1. Start backend
cd backend
python main.py

# 2. Start frontend (new terminal)
cd frontend
npm run dev

# 3. Login at http://localhost:5173/login
# Use: admin@admin.com / password123
```

### For Candidates:
```bash
# 1. Get your interview link from HR (email)
# 2. Click the link OR go to http://localhost:5173/interview
# 3. Enter your full name
# 4. Start your interview
```

---

## 📝 Password Reset (Staff)

Currently, passwords must be reset by system administrators through direct database access or backend code.

To change a staff password:
1. Contact system administrator
2. Administrator updates password in MongoDB or through backend script

---

## 🔒 Security Notes

### Current Setup (Development):
- ✅ JWT tokens for session management
- ✅ Password hashing (pbkdf2_sha256)
- ✅ CORS configured for all origins (*)
- ⚠️ Default passwords should be changed in production
- ⚠️ Candidate name-only auth is intentionally simple for UX

### Production Recommendations:
- Change all default passwords
- Restrict CORS to specific domains
- Add email verification for candidates
- Implement password reset flow
- Add rate limiting on auth endpoints
- Use HTTPS only
- Add 2FA for admin accounts

---

## 📞 Support

If you continue to have login issues:
1. Check backend console logs
2. Check browser console for errors
3. Verify MongoDB is running
4. Verify network connectivity
5. Contact system administrator
