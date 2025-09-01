import sys
import traceback
from typing import Dict, Any

def get_subtasks_tool(jira):
    async def get_subtasks(parent_task_key: str) -> Dict[str, Any]:
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
    return get_subtasks

