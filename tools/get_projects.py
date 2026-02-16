import sys
import traceback
from typing import Dict, Any

def get_projects_tool(jira):
    async def get_projects() -> Dict[str, Any]:
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
    return get_projects

