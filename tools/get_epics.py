import sys
import traceback
from typing import Dict, Any

def get_epics_tool(jira):
    async def get_epics(project_key: str) -> Dict[str, Any]:
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
    return get_epics

