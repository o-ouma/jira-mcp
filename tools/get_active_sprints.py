import sys
import traceback
from typing import Dict, Any

def get_active_sprints_tool(jira):
    async def get_active_sprints(project_key: str) -> Dict[str, Any]:
        """List all active sprints in a given Jira project"""
        try:
            boards = jira.boards(project_key=project_key)
            active_sprints = []
            for board in boards['values']:
                board_id = board.get('id')
                sprints = jira.sprints(board_id)
                for sprint in sprints['values']:
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
    return get_active_sprints

