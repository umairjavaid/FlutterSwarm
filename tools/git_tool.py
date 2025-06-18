"""
Git tool for version control operations.
"""

import os
import time
import json
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool, ToolResult, ToolStatus
from .terminal_tool import TerminalTool

class GitTool(BaseTool):
    """
    Tool for Git version control operations.
    """
    
    def __init__(self, repository_directory: Optional[str] = None):
        super().__init__(
            name="git",
            description="Perform Git version control operations",
            timeout=60
        )
        self.repository_directory = repository_directory or os.getcwd()
        self.terminal = TerminalTool(self.repository_directory)
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute Git operation.
        
        Args:
            operation: Type of operation (init, add, commit, push, pull, etc.)
            **kwargs: Operation-specific parameters
            
        Returns:
            ToolResult with operation outcome
        """
        self.validate_parameters(["operation"], operation=operation, **kwargs)
        
        start_time = time.time()
        
        try:
            if operation == "init":
                return await self._init_repository(**kwargs)
            elif operation == "status":
                return await self._get_status(**kwargs)
            elif operation == "add":
                return await self._add_files(**kwargs)
            elif operation == "commit":
                return await self._commit_changes(**kwargs)
            elif operation == "push":
                return await self._push_changes(**kwargs)
            elif operation == "pull":
                return await self._pull_changes(**kwargs)
            elif operation == "branch":
                return await self._manage_branches(**kwargs)
            elif operation == "log":
                return await self._get_log(**kwargs)
            elif operation == "diff":
                return await self._get_diff(**kwargs)
            elif operation == "clone":
                return await self._clone_repository(**kwargs)
            elif operation == "remote":
                return await self._manage_remotes(**kwargs)
            elif operation == "tag":
                return await self._manage_tags(**kwargs)
            elif operation == "reset":
                return await self._reset_changes(**kwargs)
            elif operation == "stash":
                return await self._manage_stash(**kwargs)
            else:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error=f"Unknown Git operation: {operation}",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Git operation '{operation}' failed: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    async def _init_repository(self, bare: bool = False, **kwargs) -> ToolResult:
        """Initialize a new Git repository."""
        command = "git init"
        if bare:
            command += " --bare"
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "repository_path": self.repository_directory,
                "bare": bare
            }
        
        return result
    
    async def _get_status(self, porcelain: bool = False, **kwargs) -> ToolResult:
        """Get repository status."""
        command = "git status"
        if porcelain:
            command += " --porcelain"
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS and porcelain:
            # Parse porcelain output
            changes = self._parse_porcelain_status(result.output)
            result.data = {
                "changes": changes,
                "modified_files": len([c for c in changes if c["status"] in ["M", "MM"]]),
                "added_files": len([c for c in changes if c["status"] in ["A", "AM"]]),
                "deleted_files": len([c for c in changes if c["status"] in ["D", "AD"]]),
                "untracked_files": len([c for c in changes if c["status"] == "??"])
            }
        
        return result
    
    async def _add_files(self, files: List[str] = None, all_files: bool = False, **kwargs) -> ToolResult:
        """Add files to staging area."""
        if all_files:
            command = "git add ."
        elif files:
            command = f"git add {' '.join(files)}"
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="No files specified and all_files is False"
            )
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "files": files or ["."],
                "all_files": all_files
            }
        
        return result
    
    async def _commit_changes(self, message: str, author: Optional[str] = None, **kwargs) -> ToolResult:
        """Commit staged changes."""
        if not message:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Commit message is required"
            )
        
        command = f'git commit -m "{message}"'
        if author:
            command += f' --author="{author}"'
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            # Extract commit hash from output
            commit_hash = self._extract_commit_hash(result.output)
            result.data = {
                "message": message,
                "author": author,
                "commit_hash": commit_hash
            }
        
        return result
    
    async def _push_changes(self, remote: str = "origin", branch: str = "main", 
                           force: bool = False, **kwargs) -> ToolResult:
        """Push changes to remote repository."""
        command = f"git push {remote} {branch}"
        if force:
            command += " --force"
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "remote": remote,
                "branch": branch,
                "force": force
            }
        
        return result
    
    async def _pull_changes(self, remote: str = "origin", branch: str = "main", **kwargs) -> ToolResult:
        """Pull changes from remote repository."""
        command = f"git pull {remote} {branch}"
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "remote": remote,
                "branch": branch
            }
        
        return result
    
    async def _manage_branches(self, action: str = "list", branch_name: Optional[str] = None, 
                              **kwargs) -> ToolResult:
        """Manage Git branches."""
        if action == "list":
            command = "git branch -a"
        elif action == "create":
            if not branch_name:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="Branch name required for create action"
                )
            command = f"git branch {branch_name}"
        elif action == "checkout":
            if not branch_name:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="Branch name required for checkout action"
                )
            command = f"git checkout {branch_name}"
        elif action == "delete":
            if not branch_name:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="Branch name required for delete action"
                )
            command = f"git branch -d {branch_name}"
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown branch action: {action}"
            )
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "action": action,
                "branch_name": branch_name
            }
        
        return result
    
    async def _get_log(self, max_count: int = 10, oneline: bool = False, **kwargs) -> ToolResult:
        """Get commit log."""
        command = f"git log --max-count={max_count}"
        if oneline:
            command += " --oneline"
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            commits = self._parse_log_output(result.output, oneline)
            result.data = {
                "commits": commits,
                "commit_count": len(commits),
                "max_count": max_count,
                "oneline": oneline
            }
        
        return result
    
    async def _get_diff(self, file_path: Optional[str] = None, staged: bool = False, **kwargs) -> ToolResult:
        """Get diff of changes."""
        command = "git diff"
        if staged:
            command += " --staged"
        if file_path:
            command += f" {file_path}"
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "file_path": file_path,
                "staged": staged,
                "has_changes": len(result.output.strip()) > 0
            }
        
        return result
    
    async def _clone_repository(self, url: str, directory: Optional[str] = None, **kwargs) -> ToolResult:
        """Clone a Git repository."""
        command = f"git clone {url}"
        if directory:
            command += f" {directory}"
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "url": url,
                "directory": directory
            }
        
        return result
    
    async def _manage_remotes(self, action: str = "list", name: Optional[str] = None, 
                             url: Optional[str] = None, **kwargs) -> ToolResult:
        """Manage Git remotes."""
        if action == "list":
            command = "git remote -v"
        elif action == "add":
            if not name or not url:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="Remote name and URL required for add action"
                )
            command = f"git remote add {name} {url}"
        elif action == "remove":
            if not name:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="Remote name required for remove action"
                )
            command = f"git remote remove {name}"
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown remote action: {action}"
            )
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "action": action,
                "name": name,
                "url": url
            }
        
        return result
    
    async def _manage_tags(self, action: str = "list", tag_name: Optional[str] = None, 
                          message: Optional[str] = None, **kwargs) -> ToolResult:
        """Manage Git tags."""
        if action == "list":
            command = "git tag"
        elif action == "create":
            if not tag_name:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="Tag name required for create action"
                )
            command = f"git tag {tag_name}"
            if message:
                command += f' -m "{message}"'
        elif action == "delete":
            if not tag_name:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="Tag name required for delete action"
                )
            command = f"git tag -d {tag_name}"
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown tag action: {action}"
            )
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "action": action,
                "tag_name": tag_name,
                "message": message
            }
        
        return result
    
    async def _reset_changes(self, mode: str = "mixed", target: str = "HEAD", **kwargs) -> ToolResult:
        """Reset changes."""
        valid_modes = ["soft", "mixed", "hard"]
        if mode not in valid_modes:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Invalid reset mode '{mode}'. Valid modes: {valid_modes}"
            )
        
        command = f"git reset --{mode} {target}"
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "mode": mode,
                "target": target
            }
        
        return result
    
    async def _manage_stash(self, action: str = "list", message: Optional[str] = None, **kwargs) -> ToolResult:
        """Manage Git stash."""
        if action == "list":
            command = "git stash list"
        elif action == "save":
            command = "git stash save"
            if message:
                command += f' "{message}"'
        elif action == "pop":
            command = "git stash pop"
        elif action == "apply":
            command = "git stash apply"
        elif action == "drop":
            command = "git stash drop"
        elif action == "clear":
            command = "git stash clear"
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown stash action: {action}"
            )
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "action": action,
                "message": message
            }
        
        return result
    
    def _parse_porcelain_status(self, output: str) -> List[Dict[str, str]]:
        """Parse git status --porcelain output."""
        changes = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if len(line) >= 3:
                status = line[:2]
                filename = line[3:]
                changes.append({
                    "status": status.strip(),
                    "filename": filename
                })
        
        return changes
    
    def _extract_commit_hash(self, output: str) -> Optional[str]:
        """Extract commit hash from commit output."""
        lines = output.split('\n')
        for line in lines:
            if 'commit' in line.lower() and ']' in line:
                # Look for pattern like [main abc1234]
                parts = line.split()
                for part in parts:
                    if part.startswith('[') and ']' in part:
                        # Extract hash between brackets
                        bracket_content = part[1:part.index(']')]
                        if ' ' in bracket_content:
                            return bracket_content.split()[-1]
        return None
    
    def _parse_log_output(self, output: str, oneline: bool) -> List[Dict[str, str]]:
        """Parse git log output."""
        commits = []
        
        if oneline:
            lines = output.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) >= 2:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1]
                        })
        else:
            # Parse full log format (simplified)
            lines = output.split('\n')
            current_commit = {}
            
            for line in lines:
                if line.startswith('commit '):
                    if current_commit:
                        commits.append(current_commit)
                    current_commit = {"hash": line.split()[1]}
                elif line.startswith('Author: '):
                    current_commit["author"] = line[8:]
                elif line.startswith('Date: '):
                    current_commit["date"] = line[6:]
                elif line.strip() and not line.startswith(' '):
                    # Commit message
                    current_commit["message"] = line.strip()
            
            if current_commit:
                commits.append(current_commit)
        
        return commits
    
    async def is_git_repository(self) -> bool:
        """Check if current directory is a Git repository."""
        result = await self.terminal.execute("git rev-parse --git-dir")
        return result.status == ToolStatus.SUCCESS
    
    async def get_current_branch(self) -> ToolResult:
        """Get current branch name."""
        result = await self.terminal.execute("git branch --show-current")
        return result
    
    async def get_remote_url(self, remote: str = "origin") -> ToolResult:
        """Get remote URL."""
        command = f"git remote get-url {remote}"
        return await self.terminal.execute(command)
    
    # Public methods for test and agent compatibility
    async def init(self, **kwargs):
        return await self.execute("init", **kwargs)
    
    async def add(self, files, **kwargs):
        return await self.execute("add", files=files, **kwargs)
    
    async def commit(self, message, **kwargs):
        return await self.execute("commit", message=message, **kwargs)
    
    async def status(self, **kwargs):
        return await self.execute("status", **kwargs)
    
    async def list_branches(self, **kwargs):
        return await self.execute("branches", action="list", **kwargs)
    
    async def create_branch(self, branch_name, **kwargs):
        return await self.execute("branches", action="create", branch_name=branch_name, **kwargs)
    
    async def checkout_branch(self, branch_name, **kwargs):
        return await self.execute("branches", action="checkout", branch_name=branch_name, **kwargs)
