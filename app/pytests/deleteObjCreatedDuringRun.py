import requests
import json
import os
from os import path
import pathlib

basepath = path.dirname(__file__)
delete_diagram_file_path = path.abspath(path.join(basepath, "deleteDuringRun"))

class TestDelete:
    def test_delete(self, base_url, dm_headers):
        adminSession = requests.session()
        auth_response = adminSession.post(base_url + '/rest/auth/1/session', headers=dm_headers)
        resp = adminSession.get(base_url + '/rest/api/2/project', headers=dm_headers)
        assert resp.status_code == 200
        try:
            with open(delete_diagram_file_path) as f:
                for line in f:
                    deleteLine = line.strip();
                    print(base_url + deleteLine)
                    diagrams_response = adminSession.delete(base_url + deleteLine, headers=dm_headers)
                    print(diagrams_response)
            f.close()
        except FileNotFoundError:
            print("File can not be found: " + str(delete_diagram_file_path))
        except:
            print("Something else went wrong")
