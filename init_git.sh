
#!/bin/bash
set -e

echo "Starting Git Initialization..."

# Initialize
if [ -d ".git" ]; then
    echo "Git repository already initialized."
else
    git init
    echo "Git repository initialized."
fi

# Configure user if not set (local only)
if [ -z "$(git config user.name)" ]; then
    echo "Configuring local git user identity..."
    git config user.name "Kaikai0Database"
    git config user.email "user@example.com"
fi

# Add files
echo "Adding files to staging..."
git add .

# Commit
if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
else
    echo "Committing changes..."
    git commit -m "feat: 完善行動端響應式佈局並準備雲端部署"
fi

# Remote configuration
REMOTE_URL="https://github.com/Kaikai0Database/pleasure-monitoring-platform.git"
if git remote | grep -q "^origin$"; then
    echo "Remote 'origin' exists. Updating URL to $REMOTE_URL"
    git remote set-url origin "$REMOTE_URL"
else
    echo "Adding remote 'origin' with URL $REMOTE_URL"
    git remote add origin "$REMOTE_URL"
fi

# Branch rename
echo "Renaming branch to main..."
git branch -M main

# Push attempt
echo "Attempting to push to remote..."
if git push -u origin main; then
    echo "Push successful!"
else
    echo "⚠️ Push failed. This is expected if authentication credentials are not cached."
    echo "Please run 'git push -u origin main' manually in your terminal."
fi
