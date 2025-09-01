import os
import sys
import traceback
from atlassian import Jira
from dotenv import load_dotenv

class JiraAuth:
    def __init__(self):
        self.jira_url = None
        self.jira_username = None
        self.jira_api_token = None
        self.jira = None

    def load_credentials(self):
        """Load Jira credentials from environment variables"""
        try:
            load_dotenv()
            self.jira_url = os.getenv("JIRA_URL")
            self.jira_username = os.getenv("JIRA_USERNAME")
            self.jira_api_token = os.getenv("JIRA_API_TOKEN")
            if not all([self.jira_url, self.jira_username, self.jira_api_token]):
                raise ValueError("Missing Jira credentials in environment variables")
        except Exception as e:
            print(f"Error loading Jira credentials: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

    def get_jira_client(self):
        """Initialize and return the Jira client"""
        try:
            if not all([self.jira_url, self.jira_username, self.jira_api_token]):
                self.load_credentials()
            self.jira = Jira(
                url=self.jira_url,
                username=self.jira_username,
                password=self.jira_api_token
            )
            print(f"Jira client initialized successfully", file=sys.stderr)
            print(f"Using Jira URL: {self.jira_url}", file=sys.stderr)
            return self.jira
        except Exception as e:
            print(f"Error initializing Jira client: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

