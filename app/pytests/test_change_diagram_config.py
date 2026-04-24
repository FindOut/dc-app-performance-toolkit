import requests
import json
from conftest import print_timing
# from fixtures import session
# from fixtures import base_url
from conftest import saveRemoveDiagramCmd
from conftest import print_in_shell

import os
from maxfreq import max_freq
import pathlib
import pytest

#POST /rest/dependency-map/1.0/diagram
#POST /rest/dependency-map/1.0/linkConfig
#GET /plugins/servlet/dependency-map/diagram
#POST /rest/webResources/1.0/resources
#GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50
#POST /rest/webResources/1.0/resources

class TestChangeDiagram:
    @max_freq(50/3600)
    @print_timing
    def test_change_diagram_config(self, session, dm_headers):
        # Get user
        response = session.get('/rest/dependency-map/1.0/user', headers=dm_headers)
        print_in_shell("User response: " + str(response.text))
        assert response.status_code == 200
        userKey = response.json()["key"]
        print_in_shell("User key: " + userKey)

        # Create diagram
        payload ={
          'name':"D100",
          'layoutId':0,
          'filterKey': 10000,
          'boxColorFieldKey': "priority",
          'groupedLayoutFieldKey': "priority",
          'matrixLayoutHorizontalFieldKey': 'fixVersions',
          'matrixLayoutVerticalFieldKey': 'fixVersions',
          'showTypeIcons': True,
          'parallelIssueBatches': 4,
          'issuesPerRow': 5,
          'secondaryIssues': 1,
          'boxType': 0
        }
        print_in_shell('payload=', payload)
        response = session.post('/rest/dependency-map/1.0/diagram',
            json=payload, headers=dm_headers)
        print('diag resp=',str(response.text))
        assert response.status_code == 200
        newDiagram = response.json()
        diagramId = str(newDiagram["id"])
        print_in_shell('diagramid=' +diagramId)

        saveRemoveDiagramCmd(diagramId)

        # Get all priorities
        response = session.get('/rest/dependency-map/1.0/fieldOption/priority', headers=dm_headers)
        assert response.status_code == 200
        priorityItem = response.json()[4]
        priorityItemId = str(priorityItem['id'])
        print_in_shell('priorityItemId=' + priorityItemId)

        #Get colore palete entry for diagram for field=priority option=5
        response = session.get('/rest/dependency-map/1.0/boxColor/' + diagramId, headers=dm_headers)
        assert response.status_code == 200
        value = response.text
        if not value:
           print_in_shell( "No response value")
        else:
           print_in_shell( response.json() )

        #create box coloure resource entry
        payload = {"diagramId":diagramId,"fieldKey":"priority","fieldOptionId":priorityItemId,"colorPaletteEntryId":4}
        response = session.post('/rest/dependency-map/1.0/boxColor',
            json=payload, headers=dm_headers)
        assert response.status_code == 200
        print_in_shell( response.json() )
