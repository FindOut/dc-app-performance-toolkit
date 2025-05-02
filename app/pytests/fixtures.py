import pytest
import os
from pathlib import Path
import yaml
from requests import Session
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def env_settings():
    """
    Load environment settings from jira.yml
    """
    basepath = Path(__file__).parent
    filepath = basepath.parent / "jira.yml"

    if not filepath.exists():
        raise FileNotFoundError(f"jira.yml not found at {filepath}")

    with open(filepath) as file:
        config = yaml.safe_load(file)
    
    if not config.get('settings', {}).get('env'):
        raise ValueError("'settings.env' not found in jira.yml")    

    return config['settings']['env']

def get_hostname_port() -> str:
    """
    Get base URL:
    """
    envSetting = env_settings()

    host = envSetting['application_hostname']
    port = envSetting['application_port']
    postfix = envSetting.get('application_postfix', '')
    
    if not all([host, port]):
        raise ValueError("'application_hostname' and 'application_port' must be set in jira.yml")
    
    postfix = str(postfix) if postfix is not None else ''
    
    logger.info("DEBUG HOST: %s", host)
    logger.info("DEBUG PORT: %s", port)
    logger.info("DEBUG POSTFIX: %s", postfix)
    
    return f"http://{host}:{port}{postfix}"

BASE_URL = get_hostname_port()

class LiveServerSession(Session):
    """
    Custom session that prepends base URL to requests:
    """
    def __init__(self, prefix_url=None, *args, **kwargs):
        super(LiveServerSession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
    def request(self, method, url, *args, **kwargs):
        url = self.prefix_url + url
        return super(LiveServerSession, self).request(method, url, *args, **kwargs)

@pytest.fixture
def base_url() -> str:
    """
    Fixture to return base URL:
    """
    return BASE_URL

@pytest.fixture
def nr_projects() -> int:
    """
    Fixture to return number of projects to use:
    """
    envSettings = env_settings()
    return envSettings['max_nr_projects_to_use']

@pytest.fixture(scope="class")
def dm_headers():
    """
    Fixture to return DM headers:
    """
    envSettings = env_settings()
    token = envSettings['admin_access_token']

    if not token:
        raise ValueError("'admin_access_token' not found - check jira.yml")
    bearer_token = "Bearer " + token
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": bearer_token,
    }
    logger.info("DEBUG Headers: %s", headers)
    return headers


# returns a logged in session for use in a test method
@pytest.fixture(scope="class")
def session(dm_headers):
    """
    Fixture providing an authenticated session:
    """
    
    logger.info("DEBUG fixtures BASE_URL: %s", BASE_URL)
    
    s = LiveServerSession(BASE_URL)
    
    # Set default headers for all requests
    headers = dm_headers
    logger.info("DEBUG fixtures Headers: %s", headers)
    # Test authentication
    auth_url = "/rest/auth/1/session"
    response = s.get(auth_url, headers=headers)
    logger.info("DEBUG fixtures RESPONSE: %s", response.text)
    logger.info("DEBUG fixtures STATUS: %s", response.status_code)
    if response.status_code != 200:
        raise ValueError(f"Failed to authenticate: {response.status_code} {response.text}")
    logger.info("DEBUG fixtures SESSION OK")
    yield s  # provide the fixture value
    # after test teardown
    s.close()

@pytest.fixture(scope="class")
def setup_with_session(session, dm_headers):
    """
    Setup fixture that has access to the authenticated session.
    This will run after session is created and before tests start.
    """
    # You can perform any setup operations here using the authenticated session
    # For example:
    response = session.get('/rest/dependency-map/1.0/user', headers=dm_headers)
    logger.info("DEBUG 3 STATUS: %s", response.status_code)
    if response.status_code != 200:
        raise ValueError(f"Failed to get user info: {response.status_code} {response.text}")
    
    # You can return any data needed by tests
    setup_data = {
        'user_info': response.json(),
        'timestamp': time.time()
    }
    logger.info("DEBUG 3 SETUP DATA: %s", setup_data)
    yield setup_data
    
    # Cleanup code (optional)
    # This will run after all tests in the class are done
    logger.info("Setup cleanup completed")
