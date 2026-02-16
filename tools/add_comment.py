import sys
import traceback
from typing import Dict, Any

def add_comment_tool(jira):
    async def add_comment(issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to a Jira issue (task, sub-task, or epic)"""
        try:
            jira.issue_add_comment(issue_key, comment)
            return {"success": f"Comment added to issue {issue_key}"}
        except Exception as e:
            print(f"Error adding comment to issue {issue_key}: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return {"error": str(e)}
    return add_comment

