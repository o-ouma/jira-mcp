import sys
import traceback
from typing import Dict, Any

def get_backlog_tool(jira):
    async def get_backlog(project_key: str) -> Dict[str, Any]:
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
    return get_backlog

