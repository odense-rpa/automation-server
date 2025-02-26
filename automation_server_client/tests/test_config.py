import os


from automation_server_client import AutomationServerConfig


def test_AutomationServerConfig_no_env():

    try:
        AutomationServerConfig.init_from_environment()
    except ValueError as e:
        assert str(e) == "ATS_URL is not set in the environment"

    
def test_AutomationServerConfig_env():

    os.environ["ATS_URL"] = "http://localhost:8000"
    
    AutomationServerConfig.init_from_environment()

    assert AutomationServerConfig.url == "http://localhost:8000"
