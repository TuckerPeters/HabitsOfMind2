#!/bin/bash

# Deploy Firestore Rules Script
# This script deploys the Firestore security rules to your Firebase project

echo "🚀 Deploying Firestore Rules for Habits of Mind..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found!"
    echo "Please install Firebase CLI first:"
    echo "npm install -g firebase-tools"
    exit 1
fi

# Check if logged in to Firebase
if ! firebase projects:list &> /dev/null; then
    echo "🔐 Please login to Firebase first:"
    echo "firebase login"
    exit 1
fi

# Check if firestore.rules exists
if [ ! -f "firestore.rules" ]; then
    echo "❌ firestore.rules not found in current directory!"
    exit 1
fi

# Deploy the rules
echo "📤 Deploying Firestore security rules..."
firebase deploy --only firestore:rules --project habitsofmind-3a032

# Deploy indexes if they exist
if [ -f "firestore.indexes.json" ]; then
    echo "📤 Deploying Firestore indexes..."
    firebase deploy --only firestore:indexes --project habitsofmind-3a032
fi

echo "✅ Firestore rules deployed successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Test user authentication and profile creation"
echo "2. Verify subscription data is being saved correctly"
echo "3. Check that users can access their own data only"
echo ""
echo "🔗 View your rules in Firebase Console:"
echo "https://console.firebase.google.com/project/habitsofmind-3a032/firestore/rules"