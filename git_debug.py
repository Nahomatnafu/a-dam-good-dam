#!/usr/bin/env python3
import subprocess
import sys

def run_git_command(cmd):
    """Run git command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def diagnose_git_issue():
    """Diagnose common git push issues"""
    print("🔍 Diagnosing Git Push Issue...")
    print("=" * 40)
    
    # Check current status
    code, stdout, stderr = run_git_command("git status --porcelain")
    if stdout:
        print("📝 Uncommitted changes:")
        print(stdout)
    else:
        print("✅ Working directory clean")
    
    # Check current branch
    code, branch, stderr = run_git_command("git branch --show-current")
    print(f"🌿 Current branch: {branch}")
    
    # Check remote
    code, remote, stderr = run_git_command("git remote -v")
    if remote:
        print(f"🌐 Remote configured:")
        print(remote)
    else:
        print("❌ No remote configured!")
        return "no_remote"
    
    # Check if branch exists on remote
    code, remote_branches, stderr = run_git_command("git branch -r")
    remote_branch = f"origin/{branch}"
    
    if remote_branch in remote_branches:
        print(f"✅ Remote branch exists: {remote_branch}")
        
        # Check if we're behind
        code, behind, stderr = run_git_command(f"git rev-list --count HEAD..origin/{branch}")
        if behind and behind != "0":
            print(f"⚠️  You're {behind} commits behind remote")
            return "behind"
        
        # Check if we're ahead
        code, ahead, stderr = run_git_command(f"git rev-list --count origin/{branch}..HEAD")
        if ahead and ahead != "0":
            print(f"📤 You're {ahead} commits ahead of remote")
            return "ahead"
            
    else:
        print(f"❌ Remote branch doesn't exist: {remote_branch}")
        return "no_remote_branch"
    
    return "unknown"

if __name__ == "__main__":
    issue = diagnose_git_issue()
    
    print("\n" + "=" * 40)
    print("💡 Suggested Solutions:")
    
    if issue == "no_remote":
        print("1. Add remote: git remote add origin <your-repo-url>")
        print("2. Push with upstream: git push -u origin main")
        
    elif issue == "behind":
        print("1. Pull first: git pull origin main")
        print("2. Then push: git push origin main")
        print("3. Or force push (careful!): git push --force-with-lease")
        
    elif issue == "no_remote_branch":
        print("1. Push with upstream: git push -u origin main")
        print("2. Or push current branch: git push -u origin $(git branch --show-current)")
        
    elif issue == "ahead":
        print("1. Try: git push origin main")
        print("2. If rejected, check for conflicts")
        
    else:
        print("1. Check the exact error message")
        print("2. Try: git push -v origin main (verbose output)")
        print("3. Check repository permissions")