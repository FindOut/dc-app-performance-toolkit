from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from selenium_ui.conftest import print_timing
from selenium_ui.jira.modules import _wait_until
from util.conf import JIRA_SETTINGS

APPLICATION_URL = JIRA_SETTINGS.server_url
timeout = 20


def custom_action(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            webdriver.get(f'{APPLICATION_URL}/secure/objectives/ObjectivesAction!MyObjectives.jspa')
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, 'wobo-addon-okrs-container')), interaction)
        measure(webdriver, 'selenium_app_custom_action:work-board-okrs')

        @print_timing
        def measure(webdriver, interaction):
            webdriver.get(f'{APPLICATION_URL}/secure/krs/KeyResultsAction!UpdateKeyResults.jspa')
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, 'wobo-addon-update-kr-container')), interaction)
        measure(webdriver, 'selenium_app_custom_action:work-board-key-results')
    measure(webdriver, 'selenium_app_custom_action')
