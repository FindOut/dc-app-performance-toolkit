import requests
import json
from fixtures import session
import os

class TestChangeColorMapping:
    def test_change_color_mapping(self, session):
        HOSTNAME = os.environ.get('application_hostname')
        # Get user
        diagrams_response = session.get('http://'  + HOSTNAME + ':8080/rest/dependency-map/1.0/user')
        assert diagrams_response.status_code == 200
        userKey = diagrams_response.json()["key"]
        print("User key: " + userKey)

        # Create diagram
        payload ={ 'name':"D100", 'author':userKey,
           'lastEditedBy':userKey, 'layoutId':0, 'filterKey': 10000,
            'boxColorFieldKey': "priority", 'groupedLayoutFieldKey': "priority", 
            'matrixLayoutHorizontalFieldKey': 'fixVersions', 'matrixLayoutVerticalFieldKey': 'fixVersions'}

        diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/diagram',
            json=payload)
        assert diagrams_response.status_code == 200    
        newDiagram = diagrams_response.json()
        diagramId = str(newDiagram["id"])
        print('diagramid=' +diagramId)
         
        # Get all priorities
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/fieldOption/priority')
        assert diagrams_response.status_code == 200            
        priorityItem = diagrams_response.json()[4]
        priorityItemId = str(priorityItem['id'])
        print('priorityItemId=' + priorityItemId)
        
        #Get colore palete entry for diagram for field=priority option=5 
        diagrams_response = session.get('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor?diagramId=' + diagramId + '&fieldId=priority&fieldOptionId=' + priorityItemId)
        assert diagrams_response.status_code == 200            
        value = diagrams_response.text
        if not value:
           print( "No response value")
        else:
           print( diagrams_response.json() ) 

        #create box coloure resource entry
        payload = {"diagramId":diagramId,"fieldId":"priority","fieldOptionId":priorityItemId,"colorPaletteEntryId":4}
        diagrams_response = session.post('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
            json=payload)
        assert diagrams_response.status_code == 200
        print( diagrams_response.json() )
        boxColorResource = diagrams_response.json()['id']
        
        #update box coloure resource entry, created if not exists.
        payload = {"id":boxColorResource,"diagramId":diagramId,"fieldId":"priority","fieldOptionId":priorityItemId,"colorPaletteEntryId":5}
        diagrams_response = session.put('http://' + HOSTNAME + ':8080/rest/dependency-map/1.0/boxColor',
            json=payload)
        assert diagrams_response.status_code == 200
        print( diagrams_response.json() )
        
        
    
           
        
        
              
        
 
