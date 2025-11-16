# Quick Reference: Git Commands Cheat Sheet

## Setup & Configuration

### First-Time Setup
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.editor "vim"
```

### Check Configuration
```bash
git config --list
git config user.name
```

## Creating Repositories

### New Repository
```bash
git init
git init project-name
```

### Clone Existing
```bash
git clone https://github.com/user/repo.git
git clone https://github.com/user/repo.git custom-name
```

## Basic Workflow

### Check Status
```bash
git status
git status -s  # Short format
```

### Add Changes
```bash
git add file.txt
git add .
git add *.js
git add -A  # All changes
```

### Commit Changes
```bash
git commit -m "Commit message"
git commit -am "Add and commit tracked files"
git commit --amend  # Modify last commit
```

### View History
```bash
git log
git log --oneline
git log --graph --oneline --all
git log -n 5  # Last 5 commits
git log --author="John"
```

## Branching

### Create Branch
```bash
git branch feature-name
git checkout -b feature-name  # Create and switch
git switch -c feature-name  # Modern alternative
```

### Switch Branch
```bash
git checkout main
git switch main  # Modern alternative
```

### List Branches
```bash
git branch
git branch -a  # Include remote branches
git branch -v  # Show last commit
```

### Delete Branch
```bash
git branch -d feature-name  # Safe delete
git branch -D feature-name  # Force delete
```

### Rename Branch
```bash
git branch -m new-name
git branch -m old-name new-name
```

## Merging & Rebasing

### Merge Branch
```bash
git checkout main
git merge feature-branch
git merge --no-ff feature-branch  # Create merge commit
```

### Rebase
```bash
git rebase main
git rebase -i HEAD~3  # Interactive rebase last 3 commits
```

### Resolve Conflicts
```bash
# Edit conflicted files
git add resolved-file.txt
git commit
# Or abort
git merge --abort
git rebase --abort
```

## Remote Repositories

### Add Remote
```bash
git remote add origin https://github.com/user/repo.git
git remote add upstream https://github.com/original/repo.git
```

### View Remotes
```bash
git remote -v
git remote show origin
```

### Fetch & Pull
```bash
git fetch origin
git pull origin main
git pull --rebase origin main
```

### Push
```bash
git push origin main
git push -u origin feature-branch  # Set upstream
git push --force  # Dangerous!
git push --force-with-lease  # Safer force push
```

### Remove Remote
```bash
git remote remove origin
```

## Stashing

### Save Changes
```bash
git stash
git stash save "Description"
git stash -u  # Include untracked files
```

### List Stashes
```bash
git stash list
```

### Apply Stash
```bash
git stash apply
git stash apply stash@{2}
git stash pop  # Apply and remove
```

### Delete Stash
```bash
git stash drop stash@{0}
git stash clear  # Remove all stashes
```

## Undoing Changes

### Discard Working Directory Changes
```bash
git checkout -- file.txt
git restore file.txt  # Modern alternative
```

### Unstage Files
```bash
git reset HEAD file.txt
git restore --staged file.txt  # Modern alternative
```

### Undo Commits
```bash
git reset --soft HEAD~1  # Keep changes staged
git reset HEAD~1  # Keep changes unstaged
git reset --hard HEAD~1  # Discard changes (dangerous!)
```

### Revert Commit
```bash
git revert abc123  # Create new commit that undoes changes
git revert HEAD
```

## Viewing Changes

### Show Differences
```bash
git diff
git diff --staged
git diff main feature-branch
git diff HEAD~1 HEAD
```

### Show Commit Details
```bash
git show abc123
git show HEAD~2
```

### Blame (Who Changed What)
```bash
git blame file.txt
git blame -L 10,20 file.txt
```

## Tagging

### Create Tag
```bash
git tag v1.0.0
git tag -a v1.0.0 -m "Version 1.0.0"
git tag v1.0.0 abc123  # Tag specific commit
```

### List Tags
```bash
git tag
git tag -l "v1.*"
```

### Push Tags
```bash
git push origin v1.0.0
git push origin --tags  # Push all tags
```

### Delete Tag
```bash
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0  # Delete remote tag
```

## Cleaning

### Remove Untracked Files
```bash
git clean -n  # Dry run
git clean -f  # Remove files
git clean -fd  # Remove files and directories
```

## Advanced

### Cherry-Pick
```bash
git cherry-pick abc123
git cherry-pick abc123 def456
```

### Reflog
```bash
git reflog
git reset --hard HEAD@{2}  # Recover lost commits
```

### Submodules
```bash
git submodule add https://github.com/user/lib.git
git submodule update --init --recursive
git submodule update --remote
```

### Bisect (Find Bug)
```bash
git bisect start
git bisect bad  # Current commit is bad
git bisect good abc123  # Known good commit
# Test each commit
git bisect good/bad
git bisect reset  # When done
```

## Useful Aliases

Add to `~/.gitconfig`:

```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --graph --oneline --all
    amend = commit --amend --no-edit
```

## Tips

- **Check before push**: Always `git status` and `git diff` before pushing
- **Commit often**: Small, frequent commits are easier to manage
- **Write good messages**: Clear, descriptive commit messages help everyone
- **Branch for features**: Keep main/master stable
- **Pull before push**: Avoid conflicts by staying up to date
- **Use .gitignore**: Don't commit generated files, dependencies, or secrets

## Common Workflows

### Feature Branch Workflow
```bash
git checkout -b feature-xyz
# Make changes
git add .
git commit -m "Implement feature XYZ"
git push -u origin feature-xyz
# Create pull request
# After merge
git checkout main
git pull
git branch -d feature-xyz
```

### Fix Mistake in Last Commit
```bash
# Forgot to add file
git add forgotten-file.txt
git commit --amend --no-edit

# Fix commit message
git commit --amend -m "Better message"
```

### Sync Fork with Upstream
```bash
git remote add upstream https://github.com/original/repo.git
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```
