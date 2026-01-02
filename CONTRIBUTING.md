# Team Collaboration Guide

**Note:** This is a private project for internal team use only.

## For Team Members

### Getting Started

1. **Clone the repository:**
```bash
git clone <repo-url>
cd supply-chain-guardian
```

2. **Set up your environment:**
```bash
python -m venv virtualenv
source virtualenv/Scripts/activate  # Windows
pip install -r requirements.txt
```

3. **Configure your .env:**
```bash
cp .env.example .env
# Add your API keys
```

4. **Test locally:**
```bash
python setup_database.py
python main.py
streamlit run ui/app.py
```

### Working on the Project

#### Branch Strategy
```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b bugfix/issue-description
```

#### Making Changes
- Test your changes locally before pushing
- Follow existing code patterns
- Add comments for complex logic
- Update documentation if needed

#### Committing Changes
```bash
git add .
git commit -m "Brief description of changes"
git push origin your-branch-name
```

### Code Guidelines

- Use Python 3.10+ features
- Keep functions focused and simple
- Add docstrings to new functions
- Test with both mock and real API data

### Known Issues

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for current bugs and limitations.

### Getting Help

- Check documentation files (README.md, SETUP.md, QUICKSTART.md)
- Ask in team chat/meetings
- Contact the project owner for access issues

### Confidentiality

⚠️ **Remember:** This is proprietary software.
- Do not share outside the team
- Do not commit API keys or credentials
- Keep .env files private
- Follow company security policies
