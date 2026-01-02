## 🔐 Security Notice

### Important: Protect Your Credentials

This project requires API keys and Google Cloud credentials. **NEVER commit these to Git!**

### Files That Must Stay Private

✅ **Already in .gitignore:**
- `.env` - Your environment variables and API keys
- `*.db` - Database files with your data
- `*-key.json` - Google Cloud service account keys
- `supply_chain.db` - SQLite database

### Before Pushing to GitHub

1. **Check your .env file is ignored:**
```bash
git status
# .env should NOT appear in the list
```

2. **Never commit these:**
- API keys (OpenWeatherMap, NewsAPI)
- Google Cloud credentials
- Database files
- Service account JSON files

3. **If you accidentally committed secrets:**
```bash
# Remove from Git history (use with caution)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/
```

### Use .env.example Instead

The repository includes `.env.example` as a template. Users should:
1. Copy `.env.example` to `.env`
2. Fill in their own credentials
3. Never commit `.env`

### Google Cloud Credentials

For production deployments:
- Use **Secret Manager** for API keys
- Use **Workload Identity** instead of service account keys
- Enable **audit logging** for access tracking

### Reporting Security Issues

If you discover a security vulnerability:
1. **DO NOT** open a public issue
2. Email: security@yourproject.com (if available)
3. Or open a private security advisory on GitHub

## 🛡️ Best Practices

- Rotate API keys regularly
- Use environment-specific credentials
- Enable 2FA on all cloud accounts
- Review access permissions quarterly
- Monitor usage for anomalies

---

**Remember: Security is everyone's responsibility!** 🔒
