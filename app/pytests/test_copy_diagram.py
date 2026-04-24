import requests
from conftest import print_timing
# from fixtures import session
# from fixtures import base_url
from conftest import saveRemoveDiagramCmd
from conftest import print_in_shell
import os
import random
import pathlib
from maxfreq import max_freq

class TestCopyDiagram:
    @max_freq(50/3600)
#    @print_timing
    def test_copy_diagram(self, session, dm_headers):

        #create a copy of the diagram
        response = session.get('/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50', headers=dm_headers)
        assert response.status_code == 200
        result = response.json()['values']
        if len(result)>0:
            diagramId=result[0]['id']
            print_in_shell('diagramId to copy', diagramId)
            #create a copy of the diagram
            response = session.post('/rest/dependency-map/1.0/diagram/duplicate/' + str(diagramId), headers=dm_headers)
            assert response.status_code == 200
            diagramId = response.json()
            saveRemoveDiagramCmd(diagramId)
