"""
Entry point for Streamlit Community Cloud.
Deploys the Supply Chain Intelligence Dashboard in demo mode.
"""
import sys, os
root = os.path.dirname(__file__)
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(root, "dashboard"))

from dashboard import *
