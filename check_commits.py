#!/usr/bin/env python3
import subprocess

def run_git_command(cmd):
    """Run git command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def check_recent_commits():
    """Check what's in recent commits"""
    print("📋 Recent Commits (what's ready to push):")
    print("=" * 50)
    
    # Show recent commits
    code, commits, stderr = run_git_command("git log --oneline -10")
    if commits:
        for line in commits.split('\n'):
            print(f"  {line}")
    
    print(f"\n📁 Files in Latest Commit:")
    print("=" * 30)
    
    # Show files in latest commit
    code, files, stderr = run_git_command("git diff-tree --no-commit-id --name-only -r HEAD")
    if files:
        for file in files.split('\n'):
            if file.strip():
                print(f"  ✅ {file}")
    
    print(f"\n📝 Uncommitted Changes:")
    print("=" * 25)
    
    # Show uncommitted changes
    code, status, stderr = run_git_command("git status --porcelain")
    if status:
        for line in status.split('\n'):
            if line.strip():
                status_code = line[:2]
                filename = line[3:]
                if status_code == "??":
                    print(f"  🆕 {filename} (untracked)")
                elif status_code == " M":
                    print(f"  ✏️  {filename} (modified)")
                elif status_code == "A ":
                    print(f"  ➕ {filename} (added)")
    else:
        print("  (none)")

if __name__ == "__main__":
    check_recent_commits()