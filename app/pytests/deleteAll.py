import requests
import json
from fixtures import base_url
import os
from os import path
import pathlib
from fixtures import base_url, dm_headers


basepath = path.dirname(__file__)
delete_diagram_file_path = path.abspath(path.join(basepath, "deleteCreatedObjects"))

class TestDeleteAllDiagrams:
    def test_delete(self,  base_url, dm_headers):
        adminSession = requests.session()
        auth_response = adminSession.post(base_url + '/rest/auth/1/session', headers=dm_headers)
        resp = adminSession.get(base_url + '/rest/api/2/project', headers=dm_headers)
        assert resp.status_code == 200
        diagram_ids = []
        startAt=0
        while True:
            resp =adminSession.get(base_url + f'/rest/dependency-map/1.0/diagram?searchTerm=&startAt={startAt}&maxResults=50', headers=dm_headers)
            assert resp.status_code == 200
            result = resp.json()
            if startAt >= result['total']  or not('values' in result):
                break
            diagram_ids.extend(list(map(lambda issue : issue['id'], result['values'])))
            startAt = len(diagram_ids)

        for diagram_id in  diagram_ids:
            deleteLine = "/rest/dependency-map/1.0/diagram/" + str(diagram_id)
            print(base_url + deleteLine)
            diagrams_response = adminSession.delete(base_url + deleteLine, headers=dm_headers)
            print(diagrams_response)
