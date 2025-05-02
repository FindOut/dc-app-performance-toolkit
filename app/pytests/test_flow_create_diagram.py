from conftest import print_timing
from conftest import saveRemoveDiagramCmd
import pytest
import time
import os
import random
from maxfreq import max_freq
from conftest import print_in_shell
from conftest import getRandomFilter


import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFlowCreateDiagram:

    @max_freq(50/3600)
    @print_timing
    def test_show_dependency_maps_flow_cd(self, session, dm_headers):

        #Select Dependency Map
        #GET /rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50 HTTP/1.1" 200 1630 3
        #GET /rest/api/2/filter/10000 HTTP/1.1" 200 631 2
        #GET /rest/api/2/filter/10001 HTTP/1.1" 200 632 2
        #GET /rest/api/2/user?key=admin HTTP/1.1" 200 344 1

        user_response = session.get('/rest/dependency-map/1.0/user', headers=dm_headers)
        diagrams_response = session.get('/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50', headers=dm_headers)
        assert diagrams_response.status_code == 200

        start = time.time()

        diagram_ids = []
        startAt = 0

        #Get all diagrams
        while True:
            resp =session.get(f'/rest/dependency-map/1.0/diagram?searchTerm=&startAt={startAt}&maxResults=50', headers=dm_headers)
            assert resp.status_code == 200
            result = resp.json()
            if startAt >= result['total'] or startAt > 500 or not('values' in result):
                break
            diagram_ids.extend(list(map(lambda issue : issue['id'], result['values'])))
            startAt = len(diagram_ids)
            print_in_shell("START-AT", startAt)

        # Get filter key
        diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25', headers=dm_headers)
        assert diagrams_response.status_code == 200

        filterKey1=  getRandomFilter(session)
        filterKey2=  getRandomFilter(session)
        while filterKey1==filterKey2:
            filterKey2= getRandomFilter(session)

        # Get filter 10000  ?Scrum?
        diagrams_response = session.get('/rest/api/2/filter/' + filterKey1, headers=dm_headers)
        assert diagrams_response.status_code == 200

        # Get filter 10001 ?Kanban?
        diagrams_response = session.get('/rest/api/2/filter/'+ filterKey2, headers=dm_headers)
        assert diagrams_response.status_code == 200

        # Get user
        diagrams_response = session.get('/rest/dependency-map/1.0/user', headers=dm_headers)
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print_in_shell("USERKEY", userKey)

    @max_freq(50/3600)
    @print_timing
    def test_create_diagram_flow_cd(self, session, dm_headers):
        # Create Diagram

        #JIRA Get list of available link types
        response = session.get('/rest/api/2/issueLinkType', headers=dm_headers)
        assert response.status_code == 200

        # Get filter key
        filter_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25', headers=dm_headers)
        assert filter_response.status_code == 200

        # TODO Remove these lines after testing:
        # # Get filter key
        # filter_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25', headers=dm_headers)
        # assert filter_response.status_code == 200

        # # Get filter key
        # diagrams_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25', headers=dm_headers)
        # assert diagrams_response.status_code == 200

        #Get filterKey randomly among the project in the project file
        filterKey= getRandomFilter(session)

        #Get color palet entry
        color_palette_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?paletteId=' + '1', headers=dm_headers)
        assert color_palette_response.status_code == 200

        # Get field options - status
        status_response = session.get('/rest/dependency-map/1.0/fieldOption/status', headers=dm_headers)
        assert status_response.status_code == 200

        #Get color palet entries
        color_palette_response = session.get('/rest/dependency-map/1.0/colorPaletteEntry?paletteId=' + '0', headers=dm_headers)
        assert color_palette_response.status_code == 200

        # Get user
        user_response = session.get('/rest/dependency-map/1.0/user', headers=dm_headers)
        assert user_response.status_code == 200
        userKey = user_response.json()["key"]

        # Create diagram
        payload ={
          'name': "A100",
          'layoutId': 2,
          'filterKey': filterKey,
          'boxColorFieldKey': 'priority',
          'groupedLayoutFieldKey': 'priority',
          'matrixLayoutHorizontalFieldKey': 'priority',
          'matrixLayoutVerticalFieldKey': 'priority',
          'showTypeIcons': True,
          'parallelIssueBatches': 4,
          'issuesPerRow': 5,
          'secondaryIssues': 1,
          'boxType': 0
        }

        diagrams_response = session.post('/rest/dependency-map/1.0/diagram',
            json=payload, headers=dm_headers)
        assert diagrams_response.status_code == 200
        diagramId = diagrams_response.json()['id']
        diagramKey = str(diagramId)

        saveRemoveDiagramCmd(diagramId)

        #create box colore resource entries.
        payload = {"diagramId":diagramId,"fieldKey":"priority","fieldOptionId":1,"colorPaletteEntryId":5}
        box_color_response = session.post('/rest/dependency-map/1.0/boxColor',
            json=payload, headers=dm_headers)
        assert box_color_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldKey":"priority","fieldOptionId":2,"colorPaletteEntryId":6}
        box_color_response = session.post('/rest/dependency-map/1.0/boxColor',
            json=payload, headers=dm_headers)
        assert box_color_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldKey":"priority","fieldOptionId":3,"colorPaletteEntryId":7}
        box_color_response = session.post('/rest/dependency-map/1.0/boxColor',
            json=payload, headers=dm_headers)
        assert box_color_response.status_code == 200

        payload = {"diagramId":diagramId,"fieldKey":"priority","fieldOptionId":4,"colorPaletteEntryId":8}
        box_color_response = session.post('/rest/dependency-map/1.0/boxColor',
            json=payload, headers=dm_headers)
        assert box_color_response.status_code == 200

        #Create link config entries
        # Create linkConfig
        response = session.get('/rest/api/2/issueLinkType', headers=dm_headers)

        issueLinkTypeId = response.json()['issueLinkTypes'][0]['id']

        issueLinkTypeId2 = response.json()['issueLinkTypes'][1]['id']

        issueLinkTypeId3 = response.json()['issueLinkTypes'][2]['id']

        payload = { 
            'diagramId': int(diagramKey), 
            'linkKey': int(issueLinkTypeId), 
            'visible': True, 
            'dashType': 0, 
            'width': 0, 
            'colorPaletteEntryId': 20
        }
        link_config_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
            json=payload, headers=dm_headers)
        assert(link_config_response.status_code == 200)

        payload = { 'diagramId': int(diagramKey), 'linkKey': int(issueLinkTypeId2), 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}
        link_config_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
            json=payload, headers=dm_headers)
        assert(link_config_response.status_code == 200)

        payload = { 'diagramId': int(diagramKey), 'linkKey': int(issueLinkTypeId3) , 'visible': True, 'dashType': 0, 'width': 0, 'colorPaletteEntryId': 20}
        link_config_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramKey,
            json=payload, headers=dm_headers)
        assert(link_config_response.status_code == 200)
