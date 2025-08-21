#!/bin/bash
# BBMap Website Deployment Script
# Deploys bbmap.org website with version synchronization
#
# Usage: ./deploy.sh
#
# This script will:
# 1. Check BBTools version
# 2. Update version across all website files
# 3. Commit and push to GitHub
# 4. Trigger Netlify auto-deployment

echo "================================"
echo "BBMap Website Deployment"
echo "================================"
echo ""

# Configuration
WEBSITE_DIR="/c/releases/bbmap_website"
BBTOOLS_DIR="/c/releases/bbmap"
GITHUB_REPO="bbmap-website"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Ensure we're in the website directory
cd "$WEBSITE_DIR"

# Step 1: Get current BBTools version
echo "Checking BBTools version..."
if [ -f "$BBTOOLS_DIR/README.md" ]; then
    BBTOOLS_VERSION=$(grep "Current Version:" "$BBTOOLS_DIR/README.md" | sed 's/.*\*\*\(.*\)\*\*.*/\1/')
    echo -e "BBTools version: ${GREEN}$BBTOOLS_VERSION${NC}"
else
    echo -e "${RED}ERROR: Cannot find BBTools README.md${NC}"
    exit 1
fi

# Get current website version
WEBSITE_VERSION=$(grep "Current Version:" index.html | sed 's/.*<\/strong> \(.*\)<.*/\1/' | head -1)
echo -e "Website version: ${YELLOW}$WEBSITE_VERSION${NC}"

# Step 2: Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}Uncommitted changes found:${NC}"
    git status --short
    echo ""
    read -p "Commit these changes before updating? (y/n): " COMMIT_FIRST
    
    if [ "$COMMIT_FIRST" = "y" ]; then
        git add .
        read -p "Commit message: " COMMIT_MSG
        git commit -m "$COMMIT_MSG"
    fi
fi

# Step 3: Version synchronization
if [ "$BBTOOLS_VERSION" != "$WEBSITE_VERSION" ]; then
    echo ""
    echo -e "${YELLOW}Version mismatch detected!${NC}"
    read -p "Update website from v$WEBSITE_VERSION to v$BBTOOLS_VERSION? (y/n): " UPDATE_VERSION
    
    if [ "$UPDATE_VERSION" = "y" ]; then
        echo "Updating version across all files..."
        
        # Update main page
        sed -i "s/<strong>Current Version:<\/strong> .*</<strong>Current Version:<\/strong> $BBTOOLS_VERSION</" index.html
        
        # Update version.json for future tool pages
        echo "{\"version\": \"$BBTOOLS_VERSION\", \"date\": \"$(date +%Y-%m-%d)\"}" > data/version.json
        
        # Update any existing tool pages
        if ls tools/*.html 1> /dev/null 2>&1; then
            for file in tools/*.html; do
                sed -i "s/BBTools v[0-9.]*/BBTools v$BBTOOLS_VERSION/" "$file"
            done
            echo "Updated $(ls tools/*.html | wc -l) tool pages"
        fi
        
        # Commit version update
        git add .
        git commit -m "Update version to $BBTOOLS_VERSION"
        echo -e "${GREEN}Version updated to $BBTOOLS_VERSION${NC}"
    fi
else
    echo -e "${GREEN}Version is already synchronized ($BBTOOLS_VERSION)${NC}"
fi

# Step 4: Push to GitHub
echo ""
echo -e "${YELLOW}Pushing to GitHub...${NC}"

# Initialize git if needed
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git remote add origin https://github.com/bbushnell/$GITHUB_REPO.git
    git branch -M main
fi

# Push changes
if git push origin main; then
    echo -e "${GREEN}Successfully pushed to GitHub${NC}"
    echo ""
    echo "========================================="
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo "========================================="
    echo ""
    echo "Netlify will auto-deploy in ~1-2 minutes"
    echo "Check status at: https://app.netlify.com"
    echo "Live site: https://bbmap.org"
else
    echo -e "${RED}Failed to push to GitHub${NC}"
    echo "Please check your credentials and network connection"
    exit 1
fi

# Step 5: Optional - Generate tool pages reminder
TOOL_COUNT=$(ls tools/*.html 2>/dev/null | wc -l)
SCRIPT_COUNT=$(ls "$BBTOOLS_DIR"/*.sh 2>/dev/null | wc -l)

if [ "$TOOL_COUNT" -lt "$SCRIPT_COUNT" ]; then
    echo ""
    echo -e "${YELLOW}Note: You have $TOOL_COUNT tool pages but $SCRIPT_COUNT shell scripts${NC}"
    echo "Run generate_tool_pages.py to create missing tool documentation"
fi

echo ""
echo "Deployment complete."