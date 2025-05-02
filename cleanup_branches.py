#!/usr/bin/env python3

import subprocess
import json
import sys

def run_command(command):
    """Run a shell command and return the output"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error: {result.stderr}")
        return None
    return result.stdout.strip()

def get_all_prs():
    """Get all PRs from GitHub"""
    pr_json = run_command("gh pr list --json headRefName,state,number,title,url --state all")
    if not pr_json:
        return []
    return json.loads(pr_json)

def get_local_branches():
    """Get all local branches"""
    branches = run_command("git branch --format='%(refname:short)'")
    if not branches:
        return []
    return [b for b in branches.split('\n') if b != 'main']

def get_remote_branches():
    """Get all remote branches"""
    branches = run_command("git branch -r --format='%(refname:short)'")
    if not branches:
        return []
    # Remove 'origin/' prefix and exclude 'origin/main'
    return [b.replace('origin/', '') for b in branches.split('\n') if b != 'origin/main' and b.startswith('origin/')]

def identify_merged_branches(prs, branches):
    """Identify branches that have merged PRs"""
    merged_branches = []
    for branch in branches:
        for pr in prs:
            if pr['headRefName'] == branch and pr['state'] == 'MERGED':
                merged_branches.append({
                    'branch': branch,
                    'pr_number': pr['number'],
                    'pr_title': pr['title'],
                    'pr_url': pr['url']
                })
                break
    return merged_branches

def main():
    print("Checking for branches with merged PRs that can be deleted...\n")
    
    # Get all PRs
    prs = get_all_prs()
    if not prs:
        print("Failed to retrieve PRs from GitHub.")
        return 1
    
    # Get local and remote branches
    local_branches = get_local_branches()
    remote_branches = get_remote_branches()
    
    # Identify merged branches
    merged_local_branches = identify_merged_branches(prs, local_branches)
    merged_remote_branches = identify_merged_branches(prs, remote_branches)
    
    # Display results
    if merged_local_branches:
        print("Local branches with merged PRs that can be deleted:")
        for branch in merged_local_branches:
            print(f"  - {branch['branch']} (PR #{branch['pr_number']}: {branch['pr_title']})")
        print()
    else:
        print("No local branches with merged PRs found.\n")
    
    if merged_remote_branches:
        print("Remote branches with merged PRs that can be deleted:")
        for branch in merged_remote_branches:
            print(f"  - {branch['branch']} (PR #{branch['pr_number']}: {branch['pr_title']})")
        print()
    else:
        print("No remote branches with merged PRs found.\n")
    
    # Ask for confirmation to delete branches
    if merged_local_branches or merged_remote_branches:
        confirm = input("Do you want to delete these branches? (y/n): ")
        if confirm.lower() == 'y':
            # Delete local branches
            for branch in merged_local_branches:
                branch_name = branch['branch']
                if branch_name == run_command("git rev-parse --abbrev-ref HEAD"):
                    print(f"Cannot delete the current branch: {branch_name}. Please checkout another branch first.")
                    continue
                print(f"Deleting local branch: {branch_name}")
                run_command(f"git branch -D {branch_name}")
            
            # Delete remote branches
            for branch in merged_remote_branches:
                branch_name = branch['branch']
                print(f"Deleting remote branch: {branch_name}")
                run_command(f"git push origin --delete {branch_name}")
            
            print("\nBranch cleanup completed.")
        else:
            print("\nBranch deletion cancelled.")
    else:
        print("No branches to delete.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
