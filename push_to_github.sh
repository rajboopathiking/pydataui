#!/bin/bash
# Push PyDataUI to a new GitHub repo
set -e

cd /Users/boopathiraj/Downloads/AI_Browsers/Full-Web-Framework

echo "📦 Staging all files..."
git add .

echo "📝 Committing..."
git commit -m "🚀 PyDataUI v0.1.0 — Full-stack Python framework powered by pyrustapi

A production-grade full-stack Python web framework where you write
pure Python and get complete web apps with auto-generated REST APIs.

- pyrustapi (Rust tokio/hyper) backend
- SSR + HTMX (zero JS for users)
- Reactive state management
- Auto-exposed REST APIs
- 50+ UI components
- Theme system + CSS framework
- CLI tooling
- 47 files | 4,010 lines of code"

echo "🌐 Creating GitHub repo..."
gh repo create pydataui --public --description "A production-grade full-stack Python framework powered by pyrustapi (Rust). Write Python, get web apps with auto-generated REST APIs." --source . --push

echo ""
echo "✅ Done! Repo: https://github.com/rajboopathiking/pydataui"
