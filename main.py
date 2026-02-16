import sys
import traceback
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from auth import JiraAuth
from tools.get_projects import get_projects_tool
from tools.get_epics import get_epics_tool
from tools.get_tasks import get_tasks_tool
from tools.get_backlog import get_backlog_tool
from tools.get_active_sprints import get_active_sprints_tool
from tools.transition_task import transition_task_tool
from tools.get_subtasks import get_subtasks_tool
from tools.add_comment import add_comment_tool

class JiraOps:
    def __init__(self) -> None:
        # Initialize MCP server
        self.mcp = FastMCP("JIRA OPS...")
        print("MCP Server initialized", file=sys.stderr)
        
        # Initialize Jira Client using the modularized auth
        self.jira = JiraAuth().get_jira_client()

        # Register MCP tools
        self._register_tools()



    def _register_tools(self):
        """Register MCP tools for various GitHub operations"""
        mcp = self.mcp
        jira = self.jira
        mcp.tool()(get_projects_tool(jira))
        mcp.tool()(get_epics_tool(jira))
        mcp.tool()(get_tasks_tool(jira))
        mcp.tool()(get_backlog_tool(jira))
        mcp.tool()(get_active_sprints_tool(jira))
        mcp.tool()(transition_task_tool(jira))
        mcp.tool()(get_subtasks_tool(jira))
        mcp.tool()(add_comment_tool(jira))

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