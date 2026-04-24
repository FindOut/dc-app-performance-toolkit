import requests
import json
from conftest import print_timing
# from fixtures import session
# from fixtures import base_url
from conftest import saveRemoveDiagramCmd
import os
from maxfreq import max_freq
from conftest import print_in_shell

class TestLinkConfig:
    @max_freq(500/3600)
    @print_timing
    def test_create_change_link(self, session, dm_headers):
        # Get user
        response = session.get('/rest/dependency-map/1.0/user', headers=dm_headers)
        assert response.status_code == 200
        userKey = response.json()["key"]
        print("DEB User key: " + userKey)
        print_in_shell("User key: " + userKey)

        # Create diagram
        payload = {
          'name':"E100",
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
        response = session.post('/rest/dependency-map/1.0/diagram',
            json=payload, headers=dm_headers)

        newDiagram = response.json()
        print('newDiagram=', newDiagram)
        diagramId = str(newDiagram["id"])
        saveRemoveDiagramCmd(diagramId)

        #JIRA Get list of available link types
        response = session.get('/rest/api/2/issueLinkType', headers=dm_headers)
        issueLinkTypeId = response.json()['issueLinkTypes'][0]['id']
        print_in_shell("issueLinkTypeId=" + issueLinkTypeId)
        print_in_shell( response.json() )

        # Get all link configs
        response = session.get('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId, headers=dm_headers)
        print_in_shell("all link configs")
        print_in_shell( response.json() )

        # Create linkConfig
        payload = { 'diagramId': diagramId, 'linkKey': 10000, 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}

        response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
            json=payload, headers=dm_headers)

        newLinkConfig = response.json()
        print('newLinkConfig=', newLinkConfig)
        assert(response.status_code == 200)

        # Update linkConfig
        payload = {'diagramId': diagramId, 'linkKey': 10000, 'visible': True, 'dashType': 1, 'width': 2, 'colorPaletteEntryId': 39}

        response = session.post('/rest/dependency-map/1.0/linkConfig',
            json=payload, headers=dm_headers)
        assert(response.status_code == 200)

        # Get all link configs
        response = session.get('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId, headers=dm_headers)
        assert response.status_code == 200
        print_in_shell( response.json() )
