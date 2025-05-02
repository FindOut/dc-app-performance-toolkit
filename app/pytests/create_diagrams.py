import json
from conftest import readProjectCmd
import os
from os import path
import random
import pathlib

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

basepath = path.dirname(__file__)
#CURRENT_PATH = pathlib.Path().absolute()
out_file_path = path.abspath(path.join(basepath, "deleteCreatedObjects"))

def getProjectIds(projectDict):
    result = []
    for project in projectDict:
        result.append(project['id'])
    return result

class TestCreateDiagram:

    def test_create_diagram(self, session, dm_headers):
        #Get filter key
        page = 0
        projectDict = readProjectCmd()
        projectIdList = getProjectIds(projectDict)
        filterKeyList =[]
        for  project in projectDict:
            filterKeyList.append(project["filterId"])
        print(str(filterKeyList))

        with open(out_file_path, "a") as f:
            # print( diagrams_response.json() );
            for filterKey in filterKeyList:
                logger.info("DEBUG 2 FILTER KEY: %s", filterKey)
                for c in range(0, 10):
                    diagramId = create_diagram(filterKey, session, dm_headers)
                    diagrams_delete_request = '/rest/dependency-map/1.0/diagram/' + diagramId
                    f.write(diagrams_delete_request)
                    f.write("\n")
        f.close()

def create_diagram(filterKey, session, dm_headers):
    # Get field
    field = 'priority'
    print(field)

    # Get field
    field2 = 'status'
    print(field)

    # Get user
    user_response = session.get('/rest/dependency-map/1.0/user', headers=dm_headers)
    logger.info("DEBUG 1 USER RESPONSE: %s", user_response.status_code)
    assert user_response.status_code == 200
    userKey = user_response.json()["key"]
    logger.info("User key: " + userKey)

    # Create diagram
    payload = {
      'name': "A100",
      'author': userKey,
      'layoutId': 2,
      'filterKey': filterKey,
      'boxColorFieldKey': field,
      'groupedLayoutFieldKey': field,
      'matrixLayoutHorizontalFieldKey': field,
      'matrixLayoutVerticalFieldKey': field2,
      'showTypeIcons': True,
      'parallelIssueBatches': 4,
      'issuesPerRow': 5,
      'secondaryIssues': 1,
      'boxType': 0
    }
    logger.info("DEBUG 2 PAYLOAD: %s", payload)
    logger.info("DEBUG 2 HEADERS: %s", dm_headers)
    diagram_response = session.post('/rest/dependency-map/1.0/diagram', json=payload, headers=dm_headers)
    logger.info("DEBUG 2 DIAGRAM RESPONSE: %s", diagram_response.status_code)
    assert diagram_response.status_code == 200
    diagramId = str(diagram_response.json()["id"])
    logger.info("New diagram id: " + diagramId)

    # Create linkConfig
    payload = {
      'diagramId': diagramId,
      'linkKey': 10000,
      'visible': True,
      'dashType': 0,
      'width': 0,
      'colorPaletteEntryId': 20
    }

    link_config_response = session.post('/rest/dependency-map/1.0/linkConfig?diagramId=' + diagramId,
                                     json=payload, headers=dm_headers)
    logger.info("DEBUG 2 LINK CONFIG RESPONSE: %s", link_config_response.status_code)
    assert link_config_response.status_code == 200

    newLinkConfig = link_config_response.json()
    logger.info("DEBUG 2 NEW LINK CONFIG: %s", newLinkConfig)
    # linkConfigId = str(newLinkConfig["id"])
    # logger.info("New link config id: " + linkConfigId)
    assert(link_config_response.status_code == 200)

    change_color_mapping(session, diagramId, dm_headers)

    return diagramId

def change_color_mapping(session, diagramId, dm_headers):

    # Get all priorities
    field_option_response = session.get('/rest/dependency-map/1.0/fieldOption/status', headers=dm_headers)
    logger.info("DEBUG 2 FIELD OPTION RESPONSE: %s", field_option_response.status_code)
    assert field_option_response.status_code == 200
    nrOfFieldOptions=len(field_option_response.json())
    fieldIemList = field_option_response.json()
    #Nr of field options
    print(nrOfFieldOptions)

    for field in fieldIemList:
        fieldOptionId = field["id"]
        colorPaletteEntryId = random.randint(0,19)
        #create box coloure resource entry
        payload = {
          "diagramId":diagramId,
          "fieldKey":"status",
          "fieldOptionId":fieldOptionId,
          "colorPaletteEntryId": colorPaletteEntryId
        }
        box_color_response = session.post('/rest/dependency-map/1.0/boxColor', json=payload, headers=dm_headers)
        logger.info("DEBUG 2 BOX COLOR RESPONSE: %s", box_color_response.status_code)
        assert box_color_response.status_code == 200
        print( box_color_response.json() )
        #boxColorResource = diagrams_response.json()['id']
