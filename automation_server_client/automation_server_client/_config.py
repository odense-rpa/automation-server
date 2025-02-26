import os
from dotenv import load_dotenv


class AutomationServerConfig:
    token = ""
    url = ""
    session = None
    resource = None
    process = None

    workitem_id = None

    workqueue_override = None

    @staticmethod
    def init_from_environment():
        load_dotenv()
        
        AutomationServerConfig.url = os.environ["ATS_URL"] if "ATS_URL" in os.environ else ""
        AutomationServerConfig.token = os.environ["ATS_TOKEN"] if "ATS_TOKEN" in os.environ else ""
        AutomationServerConfig.session = os.environ["ATS_SESSION"] if "ATS_SESSION" in os.environ else None
        AutomationServerConfig.resource = os.environ["ATS_RESOURCE"] if "ATS_RESOURCE" in os.environ else None
        AutomationServerConfig.process = os.environ["ATS_PROCESS"] if "ATS_PROCESS" in os.environ else None
        AutomationServerConfig.workqueue_override = os.environ["ATS_WORKQUEUE_OVERRIDE"] if "ATS_WORKQUEUE_OVERRIDE" in os.environ else None
        
        
        if AutomationServerConfig.url == "":
            raise ValueError("ATS_URL is not set in the environment")        
