"""Pre-push verification script - Run this before pushing to GitHub"""
import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Check if a file exists."""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    required_text = " (REQUIRED)" if required else ""
    print(f"{status} {filepath}{required_text}")
    return exists

def check_file_not_tracked(filename):
    """Check if a file is NOT in git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", filename],
            capture_output=True,
            text=True,
            check=False
        )
        is_tracked = bool(result.stdout.strip())
        status = "❌ TRACKED!" if is_tracked else "✅ Not tracked"
        print(f"{status} {filename}")
        return not is_tracked
    except:
        print(f"⚠️  Could not check git status for {filename}")
        return True

def check_imports():
    """Check if main modules can be imported."""
    print("\n🔍 Testing imports...")
    modules = ["database", "external_services", "alerting", "main"]
    all_good = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            all_good = False
    
    return all_good

def main():
    """Run all pre-push checks."""
    print("=" * 60)
    print("🚀 Supply Chain Guardian - Pre-Push Verification")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Check required files exist
    print("\n📝 Required Files:")
    required_files = [
        "README.md",
        "requirements.txt",
        ".gitignore",
        ".env.example",
        "main.py",
        "database.py",
        "external_services.py",
        "alerting.py"
    ]
    
    for file in required_files:
        if not check_file_exists(file, required=True):
            all_checks_passed = False
    
    # Check optional documentation
    print("\n📚 Documentation:")
    optional_files = [
        "SETUP.md",
        "QUICKSTART.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "SECURITY.md"
    ]
    
    for file in optional_files:
        check_file_exists(file, required=False)
    
    # Check sensitive files are NOT tracked
    print("\n🔐 Security Check (these should NOT be tracked):")
    sensitive_files = [".env", "supply_chain.db", "*.db", "*-key.json"]
    
    for file in sensitive_files:
        if not check_file_not_tracked(file):
            all_checks_passed = False
            print(f"⚠️  WARNING: {file} is tracked! Remove it before pushing!")
    
    # Check imports
    if not check_imports():
        all_checks_passed = False
    
    # Check for API keys in code
    print("\n🔑 Checking for hardcoded secrets...")
    try:
        result = subprocess.run(
            ["grep", "-r", "-E", "api[_-]?key.*=.*['\"][^'\"]+['\"]", 
             "--include=*.py", "--exclude-dir=virtualenv", "."],
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout:
            print("❌ Found potential hardcoded API keys:")
            print(result.stdout)
            all_checks_passed = False
        else:
            print("✅ No hardcoded secrets found")
    except:
        print("⚠️  Could not check for secrets (grep not available)")
    
    # Final verdict
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✅ All checks passed! Ready to push to GitHub!")
        print("\nNext steps:")
        print("  git add .")
        print("  git commit -m 'Your commit message'")
        print("  git push")
    else:
        print("❌ Some checks failed! Please fix issues before pushing.")
        print("\nReview:")
        print("  - Remove any .env or .db files from git")
        print("  - Ensure all required files exist")
        print("  - Fix any import errors")
        print("  - Remove hardcoded API keys")
    print("=" * 60)
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
