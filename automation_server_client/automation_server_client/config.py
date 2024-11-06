import os
import logging

class AutomationServerConfig:
    token = ""
    url = ""
    session = ""
    resource = ""
    process = ""

    workitem_id = None

    def from_enviroment(fallback_url: str = "", fallback_token: str = ""):
        logger = logging.getLogger(__name__)

        if "ATS_URL" not in os.environ or "ATS_TOKEN" not in os.environ:
            AutomationServerConfig.url = fallback_url
            AutomationServerConfig.token = fallback_token
            logger.info(f"Using fallback URL {fallback_url} and token {fallback_token}")
            return

        AutomationServerConfig.url = os.environ["ATS_URL"]
        AutomationServerConfig.token = os.environ["ATS_TOKEN"]
        AutomationServerConfig.session = os.environ["ATS_SESSION"]
        AutomationServerConfig.resource = os.environ["ATS_RESOURCE"]    
        AutomationServerConfig.process = os.environ["ATS_PROCESS"]
        

        logger.info(f"Using URL {AutomationServerConfig.url} and token {AutomationServerConfig.token}")

    


