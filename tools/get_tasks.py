import sys
import traceback
from typing import Dict, Any

def get_tasks_tool(jira):
    async def get_tasks(project_key: str) -> Dict[str, Any]:
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
    return get_tasks

