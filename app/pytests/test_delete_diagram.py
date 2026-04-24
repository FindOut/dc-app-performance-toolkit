from fixtures import session, setup_with_session, dm_headers
from conftest import print_timing
import os
from maxfreq import max_freq
from conftest import print_in_shell
from conftest import getRandomFilter

class TestDelete:
    @max_freq(50/3600)
#    @print_timing
    def test_delete_diagram(self, session, dm_headers):
        # Prepare
        # request list of diagrams using the session id
        response = session.get('/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50', headers=dm_headers)
        assert response.status_code == 200

        # To make it thread save need to create the diagram before removing

        # Get user
        response = session.get('/rest/dependency-map/1.0/user', headers=dm_headers)
        assert response.status_code == 200
        userKey = response.json()["key"]

        # Get filter key
        response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=0&resultsPerPage=25', headers=dm_headers)
        assert response.status_code == 200

        #Get filterKey randomly among the project in the project file
        filterKey= getRandomFilter(session)

        # Create diagram
        payload ={
          'name':"F100",
          'author':userKey,
          'layoutId':2,
          'filterKey': filterKey,
          'boxColorFieldKey': 'status',
          'groupedLayoutFieldKey': 'status',
          'matrixLayoutHorizontalFieldKey': 'status',
          'matrixLayoutVerticalFieldKey': 'priority',
          'showTypeIcons': True,
          'parallelIssueBatches': 4,
          'issuesPerRow': 5,
          'secondaryIssues': 1,
          'boxType': 0
        }

        response = session.post('/rest/dependency-map/1.0/diagram',
                                         json=payload, headers=dm_headers)
        assert response.status_code == 200
        diagramId = response.json()['id']

        #remove
        response = session.delete('/rest/dependency-map/1.0/diagram/' + str(diagramId), headers=dm_headers)
        assert response.status_code == 200
        print_in_shell("Diagram removed" +  str(diagramId))
        #print_in_shell( diagrams_response.json() );

        #get all diagrams after delete
        response = session.get('/rest/dependency-map/1.0/diagram?searchTerm=&startAt=0&maxResults=50', headers=dm_headers)
        assert response.status_code == 200
