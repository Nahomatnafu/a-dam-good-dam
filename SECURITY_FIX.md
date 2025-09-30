# 🔒 Security Fix - Remove API Key from Git History

## ⚠️ The Problem

The Google API key was committed to git in `config/ai_config.json`. This is a security risk because:
- Anyone with access to the repository can see the key
- The key is visible in the git history
- The key could be used to make unauthorized API calls

## ✅ What I've Done

1. **Created a template file**: `config/ai_config.json.example` (safe to commit)
2. **Updated .gitignore**: Added `config/ai_config.json` to prevent future commits
3. **Created this guide**: To help you remove the key from git history

## 🔧 Steps to Fix

### Step 1: Remove the File from Git (Keep Local Copy)

```bash
# Remove from git tracking but keep the local file
git rm --cached config/ai_config.json

# Commit this change
git commit -m "Remove API key file from git tracking"
```

### Step 2: Remove from Git History (IMPORTANT!)

The API key is still in your git history. You need to remove it:

**Option A: Using git filter-repo (Recommended)**

```bash
# Install git-filter-repo if you don't have it
# pip install git-filter-repo

# Remove the file from all history
git filter-repo --path config/ai_config.json --invert-paths

# Force push to remote (WARNING: This rewrites history!)
git push origin --force --all
```

**Option B: Using BFG Repo-Cleaner**

```bash
# Download BFG from https://rtyley.github.io/bfg-repo-cleaner/

# Remove the file from history
java -jar bfg.jar --delete-files ai_config.json

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push origin --force --all
```

**Option C: Manual with git filter-branch (Slower)**

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config/ai_config.json" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
```

### Step 3: Revoke and Regenerate the API Key

**IMPORTANT**: Even after removing from git, the old key was exposed. You should:

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your API key**: `AIzaSyBcEffoHhNRLKmurbqJZY0_tFiVtjc__Bg`
4. **Delete or Restrict it**
5. **Create a new API key**
6. **Update your local config**: Put the new key in `config/ai_config.json`

### Step 4: Verify the Fix

```bash
# Check that the file is ignored
git status
# Should NOT show config/ai_config.json as modified

# Check that it's in .gitignore
cat .gitignore | grep ai_config.json
# Should show: config/ai_config.json

# Verify it's not tracked
git ls-files | grep ai_config.json
# Should return nothing
```

### Step 5: Set Up for Other Users

Other users (or you on other machines) should:

```bash
# Copy the example file
cp config/ai_config.json.example config/ai_config.json

# Edit and add their API key
nano config/ai_config.json
# or
notepad config/ai_config.json
```

## 📋 Quick Command Summary

```bash
# 1. Remove from tracking
git rm --cached config/ai_config.json
git commit -m "Remove API key file from git tracking"

# 2. Remove from history (choose one method)
git filter-repo --path config/ai_config.json --invert-paths

# 3. Force push (WARNING: Rewrites history!)
git push origin --force --all

# 4. Revoke old API key and create new one at:
# https://console.cloud.google.com/apis/credentials

# 5. Update local config with new key
```

## ⚠️ Important Warnings

### Before Force Pushing:

1. **Coordinate with team members**: Force push rewrites history
2. **Backup your repository**: Just in case
3. **Notify collaborators**: They'll need to re-clone or reset their repos

### After Force Pushing:

Team members need to:
```bash
# Backup any local changes first!
git fetch origin
git reset --hard origin/main  # or your branch name
```

## 🔐 Best Practices Going Forward

### 1. Use Environment Variables

Instead of storing keys in files, use environment variables:

```python
import os

api_key = os.environ.get('GOOGLE_API_KEY')
if not api_key:
    # Fall back to config file
    api_key = config.get('google_api_key')
```

Set the environment variable:
```bash
# Windows
set GOOGLE_API_KEY=your_key_here

# Linux/Mac
export GOOGLE_API_KEY=your_key_here
```

### 2. Use .env Files (with python-dotenv)

```bash
pip install python-dotenv
```

Create `.env` file (already in .gitignore):
```
GOOGLE_API_KEY=your_key_here
```

Load in Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
```

### 3. Always Check Before Committing

```bash
# Review what you're about to commit
git diff --cached

# Check for sensitive data
git diff --cached | grep -i "api"
git diff --cached | grep -i "key"
git diff --cached | grep -i "password"
```

### 4. Use Pre-commit Hooks

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash

# Check for API keys
if git diff --cached | grep -i "AIza"; then
    echo "ERROR: Possible Google API key detected!"
    echo "Please remove sensitive data before committing."
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## 📁 File Structure After Fix

```
your-repo/
├── config/
│   ├── ai_config.json          ← NOT in git (ignored)
│   └── ai_config.json.example  ← IN git (template)
├── .gitignore                  ← Updated to ignore ai_config.json
└── SECURITY_FIX.md            ← This guide
```

## ✅ Verification Checklist

After completing the fix:

- [ ] `config/ai_config.json` is in `.gitignore`
- [ ] `config/ai_config.json.example` exists (template)
- [ ] Ran `git rm --cached config/ai_config.json`
- [ ] Committed the removal
- [ ] Removed from git history (filter-repo or BFG)
- [ ] Force pushed to remote
- [ ] Revoked old API key in Google Cloud Console
- [ ] Created new API key
- [ ] Updated local `config/ai_config.json` with new key
- [ ] Verified file is not tracked: `git ls-files | grep ai_config.json` returns nothing
- [ ] Tested that the application still works with new key

## 🆘 If You Need Help

### Check if the file is still in history:

```bash
git log --all --full-history -- config/ai_config.json
```

If this shows commits, the file is still in history and needs to be removed.

### Check if the file is tracked:

```bash
git ls-files | grep ai_config.json
```

If this shows the file, it's still being tracked.

### Check if .gitignore is working:

```bash
git check-ignore -v config/ai_config.json
```

Should show: `.gitignore:50:config/ai_config.json    config/ai_config.json`

## 📚 Additional Resources

- **Git Filter-Repo**: https://github.com/newren/git-filter-repo
- **BFG Repo-Cleaner**: https://rtyley.github.io/bfg-repo-cleaner/
- **GitHub Guide**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
- **Google API Key Security**: https://cloud.google.com/docs/authentication/api-keys

## 🎯 Summary

1. ✅ **Immediate**: Remove file from git tracking
2. ✅ **Critical**: Remove from git history
3. ✅ **Essential**: Revoke and regenerate API key
4. ✅ **Prevention**: Use .gitignore and template files
5. ✅ **Best Practice**: Use environment variables

**The most important step is revoking the old API key and creating a new one!**

---

**Need help with any of these steps? Let me know!**

