# Usage example:
# python3 util/edit_yml.py --application jira --application_hostname=test-instance.com --concurrency=10 --test_duration=5m

import argparse

from util.project_paths import JIRA_YML, CONFLUENCE_YML
from util.conf import read_yml_file, write_yml_file


parser = argparse.ArgumentParser(description='Edit yml config')
parser.add_argument('--application', type=str, help='e.g. jira or confluence')
parser.add_argument('--application_hostname', type=str, help='e.g. --application_hostname=test.com')
parser.add_argument('--concurrency', type=int, help='e.g. --concurrency=200')
parser.add_argument('--test_duration', type=str, help='e.g. --test_duration=5m')
args = parser.parse_args()

if args.application == 'jira':
    YML_PATH = JIRA_YML
elif args.application_hostname == 'confluence':
    YML_PATH = CONFLUENCE_YML
else:
    raise Exception('Application argument is not specified.')

yml_obj = read_yml_file(YML_PATH)

yml_obj['settings']['env']['application_hostname'] = args.application_hostname
yml_obj['settings']['env']['concurrency'] = args.concurrency
yml_obj['settings']['env']['test_duration'] = args.test_duration

write_yml_file(yml_obj, YML_PATH)