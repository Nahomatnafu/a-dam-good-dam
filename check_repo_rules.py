#!/usr/bin/env python3
"""
Help diagnose GitHub repository rule violations
"""

def check_common_issues():
    print("🔒 GitHub Repository Rule Violations")
    print("=" * 45)
    
    print("\n📋 Common Causes:")
    print("1. Branch protection rules on 'main'")
    print("2. Required pull request reviews")
    print("3. Required status checks (CI/CD)")
    print("4. Restricted push access")
    print("5. Organization policies")
    
    print("\n💡 Solutions:")
    print("=" * 15)
    
    print("\n🌿 Option 1: Use Feature Branch (Recommended)")
    print("   git checkout -b feature/sprint1-docs")
    print("   git push -u origin feature/sprint1-docs")
    print("   → Then create Pull Request on GitHub")
    
    print("\n⚙️  Option 2: Check Repository Settings")
    print("   1. Go to: https://github.com/Nahomatnafu/a-dam-good-dam/settings/branches")
    print("   2. Look for branch protection rules")
    print("   3. Temporarily disable or adjust rules")
    
    print("\n🔓 Option 3: Admin Override (if you're admin)")
    print("   git push --force-with-lease origin main")
    print("   ⚠️  Use only if you're sure!")
    
    print("\n👥 Option 4: Collaborate via Fork")
    print("   1. Fork the repository")
    print("   2. Push to your fork")
    print("   3. Create Pull Request from fork")

if __name__ == "__main__":
    check_common_issues()