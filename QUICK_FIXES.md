# Quick Reference: Most Critical Fixes

## Start Here - Top 5 Issues to Fix Immediately

### 1. 🔥 Add Firebase Configuration (2-4 hours)
**Why**: App literally won't run without it
**How**: Create example config file and deployment docs

```javascript
// Add to index.html before Firebase init
const firebaseConfig = window.__firebase_config ? JSON.parse(window.__firebase_config) : {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

---

### 2. 🛡️ Fix Security Holes (4-6 hours)
**Why**: 6-character keys can be brute-forced in minutes
**Critical Changes**:
- Use 16+ character secure random keys
- Add Firestore security rules
- Implement basic encryption

```javascript
// Better key generation
function generateSecureKey() {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return Array.from(array, b => b.toString(16).padStart(2, '0')).join('');
}
```

---

### 3. 💬 Add Error Messages (3-4 hours)
**Why**: Users have no idea when something breaks
**Add**:
- Loading spinners
- Error toast notifications
- Failed submission feedback

```javascript
const [error, setError] = React.useState(null);
const [loading, setLoading] = React.useState(false);

// In submitEcho function
try {
  setLoading(true);
  await db.collection(...).add(...);
  // success!
} catch (err) {
  setError('Failed to save. Please try again.');
  console.error(err);
} finally {
  setLoading(false);
}
```

---

### 4. 📖 Write Basic README (1-2 hours)
**Why**: No one can deploy or use this without instructions
**Include**:
- What Ditto is
- How to set up Firebase
- How to deploy
- How to use

---

### 5. ✅ Add Basic Tests (4-6 hours)
**Why**: No way to verify anything works
**Start With**:
- Sanctuary creation test
- Entry submission test
- Archive retrieval test

---

## Emergency Deployment Checklist

If you need to deploy RIGHT NOW:

- [ ] Create Firebase project at console.firebase.google.com
- [ ] Enable Firestore Database
- [ ] Enable Anonymous Authentication
- [ ] Copy Firebase config into index.html
- [ ] Deploy to Firebase Hosting or Netlify
- [ ] Test sanctuary creation
- [ ] Test entry submission
- [ ] Test archive viewing
- [ ] Share sanctuary key securely (encrypted message, not plaintext)
- [ ] Warn users this is a prototype with security limitations

---

## File Priority for Refactoring

When splitting the monolith:

1. **firebase.js** - Extract Firebase init and config
2. **encryption.js** - Add encryption utilities (NEW)
3. **components/SetupView.jsx** - Sanctuary setup
4. **components/Navigation.jsx** - Navigation UI
5. **services/firestore.js** - Database operations
6. Everything else

---

## Quick Security Audit

Current vulnerabilities (in order of severity):

| Issue | Severity | Fix Time |
|-------|----------|----------|
| Weak 6-char keys | CRITICAL | 1 hour |
| No encryption | CRITICAL | 4 hours |
| No Firestore rules | HIGH | 2 hours |
| Anonymous auth | HIGH | 3 hours |
| No input sanitization | MEDIUM | 2 hours |
| No HTTPS enforcement | MEDIUM | 1 hour |

---

## One-Day Sprint Plan

If you have 8 hours to make this production-worthy:

**Hour 1-2**: Firebase config + deployment docs
**Hour 3-4**: Better key generation + error handling
**Hour 5-6**: Basic Firestore security rules + README
**Hour 7-8**: Testing + bug fixes

This gets you to "minimally deployable" state.

---

**See IMPROVEMENT_PLAN.md for the complete roadmap**
