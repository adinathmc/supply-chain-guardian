# 🚀 Pre-Push Checklist

Use this checklist before pushing to GitHub:

## ✅ Security Check

- [ ] `.env` file is NOT tracked (should be in .gitignore)
- [ ] No API keys in code (check all .py files)
- [ ] No `*.db` or `*.sqlite` files tracked
- [ ] No service account JSON files tracked
- [ ] No credentials in commit history
- [ ] All secrets use environment variables

**Verify with:**
```bash
git status
# .env should NOT appear

git log --all --full-history --source --oneline -- .env
# Should show nothing

grep -r "API_KEY.*=" --include="*.py" .
# Should only show os.getenv() calls
```

## 📦 Code Quality

- [ ] All imports work correctly
- [ ] No syntax errors (`python -m py_compile *.py`)
- [ ] Database migrations work
- [ ] Sample data loads successfully
- [ ] All agents respond to queries

**Test with:**
```bash
python setup_database.py
python main.py
streamlit run ui/app.py
```

## 📝 Documentation

- [ ] README.md is up to date
- [ ] SETUP.md has correct instructions
- [ ] All new features documented
- [ ] .env.example includes all variables
- [ ] Comments explain complex logic

## 🧹 Clean Repository

- [ ] Remove debug print statements
- [ ] Remove commented-out code
- [ ] Remove unused imports
- [ ] No TODO comments (or track them in Issues)
- [ ] Proper file organization

## 📊 Files to Include

Make sure these exist and are current:
- [ ] README.md
- [ ] SETUP.md
- [ ] QUICKSTART.md
- [ ] CHECKLIST.md
- [ ] requirements.txt
- [ ] .gitignore
- [ ] .env.example (NOT .env)
- [ ] LICENSE
- [ ] CONTRIBUTING.md
- [ ] SECURITY.md

## 🚫 Files to NEVER Include

Double-check these are ignored:
- [ ] .env
- [ ] *.db, *.sqlite, *.sqlite3
- [ ] *-key.json, *-credentials.json
- [ ] __pycache__/, *.pyc
- [ ] virtualenv/, venv/, env/
- [ ] .vscode/ (optional)

## 🔍 Final Verification

```bash
# Check what will be committed
git status

# See differences
git diff

# Check .gitignore is working
git ls-files --others --ignored --exclude-standard

# Verify no secrets
git diff HEAD --name-only | xargs grep -l "sk-\|api[_-]key\|password\|secret" || echo "✅ No secrets found"
```

## 📤 Push Commands

Once everything is checked:

```bash
# First time setup
git init
git add .
git commit -m "Initial commit: Supply Chain Guardian v1.0"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/supply-chain-guardian.git
git push -u origin main

# Subsequent pushes
git add .
git commit -m "Your commit message"
git push
```

## 🏷️ Version Tagging (Optional)

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## ⚠️ If You Accidentally Committed Secrets

**STOP! Don't push yet!**

```bash
# Remove from last commit
git reset HEAD~1
# or
git rm --cached .env
git commit --amend

# If already pushed, you MUST:
# 1. Rotate all exposed credentials immediately
# 2. Use git filter-branch or BFG Repo-Cleaner
# 3. Force push (breaks history for collaborators)
```

## 🎯 Ready to Push?

All checkboxes marked? Run this final check:

```bash
echo "Checking for common issues..."
! git ls-files | grep -E '\.env$|\.db$|key\.json$' && echo "✅ No sensitive files" || echo "❌ FOUND SENSITIVE FILES!"
python -c "import database; import external_services; import alerting" && echo "✅ Imports work" || echo "❌ Import errors"
[ -f .env.example ] && echo "✅ .env.example exists" || echo "❌ Missing .env.example"
[ -f README.md ] && echo "✅ README.md exists" || echo "❌ Missing README.md"
echo "All checks complete!"
```

If all checks pass: **You're ready to push! 🚀**

---

**Remember:** Once pushed, assume all committed data is public forever, even if you delete it later!
