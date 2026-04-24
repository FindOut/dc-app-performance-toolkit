import os
from os import path
import math
import random
import pathlib
from itertools import islice

from fixtures import session, setup_with_session, dm_headers, nr_projects
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

basepath = path.dirname(__file__)
#CURRENT_PATH = pathlib.Path().absolute()
out_file_path = path.abspath(path.join(basepath, "deleteCreatedObjects"))

#CURRENT_PATH = pathlib.Path().absolute()
projects_path = path.abspath(path.join(basepath, "projects"))

def saveRemoveFilterCmd(filterId):
    filter_request ='/rest/api/2/filter/' + str(filterId) + '\n'
    with open(out_file_path, "a") as f:
        f.write(filter_request)
        f.close()

def saveProjectCmd(projectName, key, id, filterId):
    try:
        with open(projects_path, "a") as f:
            project = {'projectName': projectName, 'key': key, 'id': id, 'filterId': filterId}
            f.write(str (project))
            f.write("\n")
            f.close()
    except IOError:
        print("File not accessible write: " + projects_path)


# returns the number of ways k elements can be chosen from n elements
def binom(n, k):
    return math.factorial(n) // math.factorial(k) // math.factorial(n - k)

# returns the number in an issue key
def issue_key_number(s):
    return int(s.partition("-")[2])

def get_link_type(session, dm_headers):
    #JIRA Get list of available link types
    issueLinkTypeId = 0
    response = session.get('/rest/api/2/issueLinkType', headers=dm_headers)
    issueLinkTypes = response.json()['issueLinkTypes']
    for linkType in issueLinkTypes:
        print(linkType)
        if linkType["name"]=="Blocks":
            issueLinkTypeId=linkType["id"]
            break
    print(issueLinkTypeId)
    return issueLinkTypeId



def get_projects(nr_projects, session, dm_headers):
    resp = session.get('/rest/api/latest/project', headers=dm_headers)
    assert resp.status_code == 200
    result = resp.json()
    return result

def get_projects_with_permisions(nr_projects, session, dm_headers):
    #Before running, there has to performance users in the DB.
    projects = get_projects(nr_projects, session, dm_headers)
 #   print("AllProjects: " + str(projects))
    projects_with_perm = []
    for project in projects:
        projectKey = project['key']
        response = session.get(
            "/rest/api/2/user/permission/search?permissions=ASSIGN_ISSUE&projectKey=" + projectKey + "&username=per", 
            headers=dm_headers)
#        print(str(response.json()))
        if (len(response.json())) > 0:
            projectId = project['id']
            projects_with_perm.append(project)
        if (len(projects_with_perm)>= nr_projects):
            break
    print ("PROJECTS WITH PERM:" + str(len(projects_with_perm )))
    return projects_with_perm

def get_filter(projectId, session, dm_headers):
    page = 0
    exit = 0
    filterKey =""
    print("PROJECT" + str( projectId ))
    while True:
        result_response = session.get('/rest/dependency-map/1.0/filter?searchTerm=&page=' + str(page) + '&resultsPerPage=50', headers=dm_headers)
        assert result_response.status_code == 200
        filter_response = result_response.json()["filters"]
#        print ("all filters json: " + str(filter_response))
        page = page + 1

        if len(filter_response) ==0:
            break

        for filter in filter_response:
            filter_id = str (filter['filterId'])
 #           print("filter['filterId']" +filter_id)
            permission_response = session.get('/rest/api/2/filter/' + filter_id + '/permission', headers=dm_headers)
  #          print ("for filter: " + str(permission_response.json()))
            for sharePer in permission_response.json():
   #             print("Permission: " + str(sharePer))
   #             print(sharePer['type']=='project')
   #             print (sharePer['project']['id'] == projectId )
   #             print("F2 SharePer['project']['id']" + sharePer['project']['id'])
   #             print("F2 projectId" + projectId)
                if sharePer['type']=='project' and  sharePer['project']['id'] == projectId   :
                    filterKey=filter_id
                    exit = 1
                    break
            if exit ==1:
                break

        if exit == 1:
            break
    return filterKey

def create_filter_if_missing(projects, session, dm_headers):
    #Before running, there has to performance users in the DB.
    print("PROJECTS#" + str(projects))
    for project in projects:
        filterKey = get_filter(project["id"], session, dm_headers)
        print("FilterKey" + filterKey)

        if filterKey == "" :
            # Create filter
            jqlQuery = "project = " + project["key"]
            print(jqlQuery)
            payload = {"jql": jqlQuery,
                "name": project["key"] + " NEW All issues",
                "description": "List all issues"}
            response = session.post(
                '/rest/api/2/filter', json=payload, headers=dm_headers)
            assert response.status_code == 200
            result = response.json()
            new_filter_id = result['id']
            print("Filter created: " + new_filter_id)
            filterKey=new_filter_id
            saveRemoveFilterCmd(new_filter_id)
            #Set filter permission
            payloadPer = {"type": "group",
                          "groupname": "jira-software-users"}
            responsePer = session.post(
                '/rest/api/2/filter/' + filterKey + "/permission", json=payloadPer, headers=dm_headers)
            assert response.status_code == 200
        saveProjectCmd(project['name'], project['key'], project['id'], filterKey)


class TestCreateIssueLinks:
    def test_create_issue_links(self, nr_projects, session, dm_headers):
        # get all projects
        projStartAt = 0

        respProj = session.get('/rest/api/latest/project', headers=dm_headers)
        projects = get_projects_with_permisions(nr_projects, session, dm_headers)
        create_filter_if_missing(projects, session, dm_headers)

        issueLinkTypeId = get_link_type(session, dm_headers)
        assert respProj.status_code == 200
        projects = respProj.json()
        print("NR of projects: " + str(nr_projects))
        fieldsKey = "status" # FIXME Hack to get going - see session.get on line 179 
        if len(projects) > nr_projects:
            projects = x = islice(projects, 0, nr_projects)
        for project in projects:
            project_key = project['key']
            # collect keys of all issues in this project into issue_ids
            link_percentage = 30
            issue_ids = []
            startAt = 0
            while True:
                logger.info(f"DEBUG searching project {project_key} starting at {startAt} -> /rest/api/latest/search?maxResults=100&startAt={startAt}&jql=project={project_key}&fields={fieldsKey}")
                resp = session.get(f'/rest/api/latest/search?maxResults=100&startAt={startAt}&jql=project="{project_key}"&fields={fieldsKey}', headers=dm_headers)
                assert resp.status_code == 200
                result = resp.json()
                #         print(f"if {startAt} >= {result['total']}")
                if startAt >= result['total'] or not ('issues' in result):
                    break
                issue_ids.extend(list(map(lambda issue: issue['id'], result['issues'])))
                startAt = len(issue_ids)
            if len(issue_ids) == 0:
                break
            # generate link_percentage random issue pairs out of issue_ids
            # all pairs are in increasing order, to avoid link cycles
            pair_count = min(len(issue_ids) * link_percentage / 100,
                             binom(len(issue_ids), 2))  # limit wanted number of links by theoretical maximum
            pairs = set()  # set of tuples, as tuples can be added to a set, but not lists
            while len(pairs) < pair_count:
                pair = tuple(sorted(random.sample(issue_ids, 2)))
                if pair not in pairs:
                    pairs.add(pair)
            for pair in pairs:
                print(pair)
                self.create_link(session, dm_headers, issueLinkTypeId, pair[0], pair[1])
        print("end")

    def create_link(self, session, dm_headers, issueLinkTypeId, from_issue_id, to_issue_id):
        #before
        response = session.get('/rest/api/2/issue/' + from_issue_id, headers=dm_headers)
        before_issue_links = response.json()['fields']['issuelinks']
        before_size = len(before_issue_links)

        payload = { 'type': { 'id': issueLinkTypeId},  #blocks?
                    'inwardIssue': { 'id': to_issue_id },
                    'outwardIssue': { 'id': from_issue_id}}
        response = session.post('/rest/api/2/issueLink',
                                     json= payload, headers=dm_headers)

        logger.info(f"DEBUG created link from issue {from_issue_id} to {to_issue_id}. Status code: {response.status_code}")

        #JIRA Get new issue links id
        response = session.get('/rest/api/2/issue/' + from_issue_id, headers=dm_headers)
        issueLinks = response.json()['fields']['issuelinks']
        #print(issueLinks)
        if (len(issueLinks) > before_size):
            issueLinksId = 0
            for issueLink in issueLinks:
                if 'inwardIssue' in issueLink and  issueLink['inwardIssue']:
                   if  issueLink['inwardIssue']['id']==to_issue_id:
                       issueLinksId = issueLink['id']

            #issueLinksId = issueLinks[-1]['id']
            print("New issue Links Id=" + issueLinksId);
            if issueLinksId!=0:
                try:
                    with open(out_file_path, "a") as f:
                        issueLink_delete_request ='/rest/api/latest/issueLink/' + issueLinksId
                        f.write(issueLink_delete_request)
                        f.write("\n")
                        f.close()
                except IOError:
                    print("File not accessible delete...")
