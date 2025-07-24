import sys
import os
import traceback
import base64
from typing import Any, List, Dict
from mcp.server.fastmcp import FastMCP
from atlassian import Jira
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

class JiraOps:
    def __init__(self) -> None:
        # Load env variables
        load_dotenv()

        # Initialize MCP server
        self.mcp = FastMCP("JIRA OPS...")
        print("MCP Server initialized", file=sys.stderr)
        
        # Initialize Confluence Client
        self._init_jira()


        # Register MCP tools
        self._register_tools()


    def _init_jira(self):
        """Initialize the Jira client with API credentials"""
        try:
            self.jira_url = os.getenv("JIRA_URL")
            self.jira_username = os.getenv("JIRA_USERNAME")
            self.jira_api_token = os.getenv("JIRA_API_TOKEN")

            if not all([self.jira_url, self.jira_username, self.jira_api_token]):
                raise ValueError("Missing Jira credentials in environment variables")

            self.jira = Jira(
                url=self.jira_url,
                username=self.jira_username,
                password=self.jira_api_token
            )
            print(f"Jira client initialized successfully", file=sys.stderr)
            print(f"Using Jira URL: {self.jira_url}", file=sys.stderr)
        except Exception as e:
            print(f"Error initializing Jira client: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)


    def _register_tools(self):
        """Register MCP tools for various GitHub operations"""
        mcp = self.mcp
        jira = self.jira
        
        # PR Analysis Tools
        @self.mcp.tool()
        async def get_projects(self) -> Dict[str, Any]:
            """List all Jira projects"""
            try:
                projects = jira.projects()
                project_list = [
                    {"key": project.key, "name": project.name}
                    for project in projects
                ]
                return {"projects": project_list}
            except Exception as e:
                print(f"Error fetching projects: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {"error": str(e)}

        @self.mcp.tool()
        async def get_epics(self, project_key: str) -> Dict[str, Any]:
            """List all Jira epics in a given project"""
            try:
                jql = f'project = "{project_key}" AND issuetype = Epic'
                epics = jira.jql(jql).get('issues', [])
                epic_list = [
                    {"key": epic['key'], "summary": epic['fields'].get('summary', '')}
                    for epic in epics
                ]
                return {"epics": epic_list}
            except Exception as e:
                print(f"Error fetching epics for project {project_key}: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {"error": str(e)}

        @self.mcp.tool()
        async def get_tasks(self, project_key: str) -> Dict[str, Any]:
            """List all Jira tasks in a given project, including assignee and status"""
            try:
                jql = f'project = "{project_key}" AND issuetype = Task'
                tasks = jira.jql(jql).get('issues', [])
                task_list = [
                    {
                        "key": task['key'],
                        "summary": task['fields'].get('summary', ''),
                        "assignee": (task['fields'].get('assignee') or {}).get('displayName') if task['fields'].get('assignee') else None,
                        "status": (task['fields'].get('status') or {}).get('name') if task['fields'].get('status') else None
                    }
                    for task in tasks
                ]
                return {"tasks": task_list}
            except Exception as e:
                print(f"Error fetching tasks for project {project_key}: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {"error": str(e)}

        @self.mcp.tool()
        async def get_backlog(self, project_key: str) -> Dict[str, Any]:
            """List all backlog issues in a given Jira project, including assignee and status"""
            try:
                jql = f'project = "{project_key}" AND statusCategory = "To Do"'
                issues = jira.jql(jql).get('issues', [])
                backlog_list = [
                    {
                        "key": issue['key'],
                        "summary": issue['fields'].get('summary', ''),
                        "assignee": (issue['fields'].get('assignee') or {}).get('displayName') if issue['fields'].get('assignee') else None,
                        "status": (issue['fields'].get('status') or {}).get('name') if issue['fields'].get('status') else None
                    }
                    for issue in issues
                ]
                return {"backlog": backlog_list}
            except Exception as e:
                print(f"Error fetching backlog for project {project_key}: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {"error": str(e)}

        @self.mcp.tool()
        async def get_active_sprints(self, project_key: str) -> Dict[str, Any]:
            """List all active sprints in a given Jira project"""
            try:
                # Get all boards for the project
                boards = jira.get_all_boards(project_key=project_key)
                active_sprints = []
                for board in boards:
                    board_id = board.get('id')
                    sprints = jira.get_all_sprints(board_id)
                    for sprint in sprints:
                        if sprint.get('state') == 'active':
                            active_sprints.append({
                                "id": sprint.get('id'),
                                "name": sprint.get('name'),
                                "state": sprint.get('state')
                            })
                return {"active_sprints": active_sprints}
            except Exception as e:
                print(f"Error fetching active sprints for project {project_key}: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {"error": str(e)}

        @self.mcp.tool()
        async def transition_task(self, task_key: str, target_status: str) -> Dict[str, Any]:
            """Transition a Jira task to a specified status (e.g., Ready for Dev, In Progress, Blocked, In Review, Done)"""
            try:
                # Get all possible transitions for the task
                transitions = jira.get_issue_transitions(task_key)
                # Find the transition id for the target status
                transition_id = None
                for t in transitions:
                    if t.get('to', {}).get('name', '').lower() == target_status.lower():
                        transition_id = t.get('id')
                        break
                if not transition_id:
                    return {"error": f"No transition found to status '{target_status}' for task {task_key}"}
                # Perform the transition
                jira.transition_issue(task_key, transition_id)
                return {"success": f"Task {task_key} transitioned to '{target_status}'"}
            except Exception as e:
                print(f"Error transitioning task {task_key} to {target_status}: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {"error": str(e)}

        @self.mcp.tool()
        async def get_subtasks(self, parent_task_key: str) -> Dict[str, Any]:
            """List all sub-tasks tied to a given Jira task, including assignee and status"""
            try:
                issue = jira.issue(parent_task_key)
                subtasks = issue['fields'].get('subtasks', [])
                subtask_list = [
                    {
                        "key": sub['key'],
                        "summary": sub['fields'].get('summary', ''),
                        "assignee": (sub['fields'].get('assignee') or {}).get('displayName') if sub['fields'].get('assignee') else None,
                        "status": (sub['fields'].get('status') or {}).get('name') if sub['fields'].get('status') else None
                    }
                    for sub in subtasks
                ]
                return {"subtasks": subtask_list}
            except Exception as e:
                print(f"Error fetching subtasks for task {parent_task_key}: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {"error": str(e)}

        @self.mcp.tool()
        async def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
            """Add a comment to a Jira issue (task, sub-task, or epic)"""
            try:
                jira.issue_add_comment(issue_key, comment)
                return {"success": f"Comment added to issue {issue_key}"}
            except Exception as e:
                print(f"Error adding comment to issue {issue_key}: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {"error": str(e)}


    def run(self):
        """Start the MCP server"""
        try:
            print("Running MCP poc server for Github PR Analysis...", file=sys.stderr)
            self.mcp.run(transport="stdio")
        except Exception as e:
            print(f"Fatal Error in MCP poc Server: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    analyzer = JiraOps()
    analyzer.run()