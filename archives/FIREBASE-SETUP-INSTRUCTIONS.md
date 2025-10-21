# Firebase Setup Instructions

## 🔥 Fix "Missing or insufficient permissions" Error

The error you're seeing indicates that Firestore security rules are not allowing users to read/write their profile data. Here's how to fix it:

## ✅ Step 1: Deploy Firestore Security Rules

I've created the proper security rules for your project. Deploy them using Firebase CLI:

### Option A: Use the deploy script (recommended)
```bash
cd /Users/tuckerpeters/HabitsOfMind2
./deploy-firestore-rules.sh
```

### Option B: Manual deployment
```bash
# Install Firebase CLI if you haven't already
npm install -g firebase-tools

# Login to Firebase
firebase login

# Deploy rules to your project
firebase deploy --only firestore:rules --project habitsofmind-3a032
firebase deploy --only firestore:indexes --project habitsofmind-3a032
```

## ✅ Step 2: Verify Security Rules

After deployment, check your Firebase Console:
1. Go to https://console.firebase.google.com/project/habitsofmind-3a032/firestore/rules
2. You should see the new rules that allow:
   - Users to read/write their own `/users/{userId}` documents
   - Users to read their own subscription data in `/customers/{userId}`
   - Public access to CMS content, events, etc.

## ✅ Step 3: Test the Fix

After deploying the rules:
1. Refresh your web app
2. Sign in with a user account
3. Go to `/account` page
4. Check browser console - the "Missing or insufficient permissions" error should be gone
5. User profile should load successfully

## 📋 What the Security Rules Allow

```javascript
// Users can read/write their own profile
/users/{userId} - read/write if authenticated user matches userId

// Stripe subscription data
/customers/{userId} - read/write if authenticated user matches userId
/customers/{userId}/subscriptions/{id} - read if authenticated user matches userId

// Public content (no authentication required)
/public/{document} - readable by everyone
/cms/{document} - readable by everyone
/events/{document} - readable by everyone
```

## 🚨 Common Issues

### Issue: Rules not taking effect
**Solution:** Wait 1-2 minutes after deployment for rules to propagate

### Issue: Still getting permissions error
**Solutions:**
1. Check Firebase Console rules tab to ensure deployment worked
2. Clear browser cache and cookies
3. Sign out and sign back in
4. Check that user is properly authenticated before accessing Firestore

### Issue: Subscription data not loading
**Cause:** User document doesn't exist yet
**Solution:** The auth store automatically creates user profiles on first login

## 🔧 Development vs Production

Your `.env` file is correctly configured:
- `VITE_USE_EMULATOR=false` - Using production Firestore
- `VITE_FIREBASE_CONFIG` - Points to your live project `habitsofmind-3a032`

## 🎯 Expected Behavior After Fix

1. **New users:** Profile automatically created in `/users/{userId}`
2. **Existing users:** Can read/update their profile data
3. **Subscription system:** Can store and retrieve subscription status
4. **Account page:** Shows user profile and subscription information
5. **No more Firebase errors** in browser console

## 📞 Need Help?

If you're still seeing issues after deploying the rules:
1. Check Firebase Console → Firestore → Rules tab
2. Look at browser Network tab for failed Firestore requests
3. Verify the user is authenticated (check `auth.currentUser`)

Deploy the rules and the Firebase permissions should be fixed! 🚀