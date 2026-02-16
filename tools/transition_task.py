import sys
import traceback
from typing import Dict, Any

def transition_task_tool(jira):
    async def transition_task(task_key: str, target_status: str) -> Dict[str, Any]:
        """Transition a Jira task to a specified status (e.g., Ready for Dev, In Progress, Blocked, In Review, Done)"""
        try:
            transitions = jira.get_issue_transitions(task_key)
            transition_id = None
            for t in transitions:
                if t.get('to', {}).get('name', '').lower() == target_status.lower():
                    transition_id = t.get('id')
                    break
            if not transition_id:
                return {"error": f"No transition found to status '{target_status}' for task {task_key}"}
            jira.transition_issue(task_key, transition_id)
            return {"success": f"Task {task_key} transitioned to '{target_status}'"}
        except Exception as e:
            print(f"Error transitioning task {task_key} to {target_status}: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"error": str(e)}
    return transition_task

