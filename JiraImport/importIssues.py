from jira import JIRA
#from xlsxwriter.workbook import Workbook
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
try:
    from openpyxl.cell import get_column_letter
except ImportError:
    from openpyxl.utils import get_column_letter
import warnings
import datetime
import time
import errno
import os
import fileinput
import glob
import csv
import requests
import urllib3
import json
from jira.resources import GreenHopperResource, TimeTracking, Resource, Issue, Worklog, CustomFieldOption

# <!----- PARAMETERS ------

JIRA_BASE_URL = 'https://jira.vectorams.co.nz'
SprintExtract = project + "_Sprints"
JiraExtract = project + "_JiraIssues"
WorkLogExtract = project + "_WorkLogs"
TeamMemberExtract = 'TeamMembers'
date = time.strftime('%Y%m%d%H%M%S')
xlext = '.xlsx'
csvext = '.csv'

# Jira Issue field list
FieldList = ['issuetype', 'project', 'status', 'resolution', 'created', 'timeestimate',
                 'aggregatetimeoriginalestimate', 'aggregatetimeestimate',
                 'timespent', 'aggregatetimespent', 'resolutiondate', 'customfield_10000', 'customfield_10001',
                 'customfield_11412', 'customfield_10103', 'customfield_10600','fixVersions', 'customfield_10008', 'summary', 'priority']

# Sprint field list
SPFieldList = ['rapidViewId', 'state', 'name', 'startDate', 'endDate', 'completeDate', 'sequence']

# Sprints: Fields to removed
spfieldremove= ['rapidViewId=', 'state=', 'name=', 'startDate=', 'endDate=', 'completeDate=', 'sequence=']

# Work Log field list
WLFieldList = ['issuekey','id', 'issueId', 'created','author.name', 'timeSpentSeconds']
#,'runningremainingestimate','totalremaining', 'cummtimespent'

#Members fields list
MembersFieldList =['id', 'name', 'key', 'displayname', 'availability', 'team', 'teamname']

# ----- PARAMETERS ------>

def get_jira_admin_auth():
    # **** Credentials **** #
    # jira = JIRA(basic_auth=(userName, passwd), server='https://jira.vectorams.co.nz')
    #serverName = 'https://jira.vectorams.co.nz'

    serverName = JIRA_BASE_URL
    userName = 'kannanr'
    passwd = 'Password01'
    option = {'server': serverName,'verify':False}
    return JIRA(options = option, basic_auth=(userName, passwd))


def setUp():
    jira = get_jira_admin_auth()
    return jira

def Jsetup():
    JIRAsession = requests.session()
    JIRAsession.auth = ("kannanr", "Password01")
    return JIRAsession


# Writes to csv and converts into Excel
def writecsv(data, filename, fieldNames):
    filename = filename + csvext
    csv = open(filename, "a")
    csv.write(data)
    csv.close()

    #if filename.__contains__('Sprint'):
    # Cleanse Sprint file
    #    for rf in spfieldremove:
    #        replacestrinfile(filename, rf, '')
    return;

# Rename file if exist
def silentrename(filename):
    try:
        os.rename(filename, filename + '_' + date)
        os.remove(filename)
    except OSError as e:                    # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:         # errno.ENOENT = no such file or directory
            raise                           # re-raise exception if a different error occurred

# Delete a file is exist
def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:                    # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:         # errno.ENOENT = no such file or directory
            raise                           # re-raise exception if a different error occurred

# Insert header line in the given file
def writeHeader(filename, line):
    with open(filename, 'w+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

# Find and replace string in the given file
def replacestrinfile(filename, text_to_search, replacement_text):
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')

# Convert csv to Excel file
def coneverttoxls():
    filecount=0
    filedata=[0,0]
    for csvfile in glob.glob(os.path.join('.', '*.csv')):
        f = open(csvfile)
        csv.register_dialect('comma', delimiter=',')
        reader = csv.reader(f)
        rowcount = 0
        wb=Workbook()
        dest_filename = csvfile[:-4] + xlext
        ws = wb.worksheets[0]
        ws.title = "Table1"

        for row_index, row in enumerate(reader):
            colcount=0
            for column_index, cell in enumerate(row):
                column_letter = get_column_letter((column_index + 1))
                ws.cell(row_index + 1, column_index+1, cell)
                #ws.cell('%s%s' % (column_letter, (row_index + 1))).value = cell
                colcount = colcount + 1
            rowcount = rowcount + 1
        range='A1:' + column_letter + str(rowcount)

        wb.save(filename=dest_filename)
        wb.close()
        f.close()

        # Delete csv file
        silentremove(csvfile)
        filedata[0] = rowcount
        filedata[1] = colcount - 1

        # Create Table in Excel
        createtable(dest_filename, range)
    return filedata

# Convert data in Excel as Table to avoid structure issue in Power BI when more fields are added or removed
def createtable(filename, range):
    open_file = load_workbook(filename)
    ws = open_file.worksheets[0]
    tab=Table(displayName="Table1",ref=range)
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    tab.tableStyleInfo = style
    ws.add_table(tab)

    open_file.save(filename)
    open_file.close()

# Cleanse Sprint csv file
def cleansesprintfile():
    # Cleanse Sprint file
    try:
        for rf in spfieldremove:
            replacestrinfile(SprintExtract + csvext, rf, '')
    except FileNotFoundError:
        print('Sprint file cleansing failed')

# Import all issues from Jira
def importFromJira(project):
    #project = "SWAG2"
    jql = 'project = "' + project + '" OR project = SPRINTOVER'
    print('Started..' + project + "--" + str(datetime.datetime.time(datetime.datetime.now())))

    # Delete Extract files if already exist
    silentrename(JiraExtract + xlext)
    silentrename(SprintExtract + xlext)
    silentrename(WorkLogExtract + xlext)
    silentrename(TeamMemberExtract + xlext)
    # Get Jira fields in Array
    flist = ','.join(FieldList)

    # Work Log fields in Array
    wlflist = ','.join(WLFieldList)

    #Sprint fields in Array
    spflist = ','.join(SPFieldList)


    #TeamMembers fields in Array
    tmflist = ','.join(MembersFieldList)

    # Add Header to Extracts
    writeHeader(JiraExtract + csvext, 'issuekey,' + flist)
    writeHeader(SprintExtract + csvext, spflist)
    writeHeader(WorkLogExtract + csvext, wlflist)
    writeHeader(TeamMemberExtract + csvext, tmflist)

    jira = setUp()
    
    # <!---- **** GET JIRA ISSUES  ****
    block_size = 500
    block_num = 0
    running = True

    while running:
        start_idx = block_num * block_size
        issues = jira.search_issues(jql, start_idx, block_size)
        if len(issues) == 0:
            # Retrieve issues until there are no more to come
            running = False

        if running:
            block_num += 1
            print('Building Jira Issues..' + str(datetime.datetime.time(datetime.datetime.now())))
            concatStr = ''
            wlConcat = ''
            spConcat=''

            for issue in issues:
                #print(issue.key)
                worklogs = jira.worklogs(issue.key)

                origestimate = 0
                remestimate = 0

                #Total Original Estimate
                if issue.raw['fields']['aggregatetimeoriginalestimate'] is not None:
                    origestimate = int(issue.raw['fields']['aggregatetimeoriginalestimate'])

                #Total Remaining Estimate
                if issue.raw['fields']['aggregatetimeestimate'] is not None:
                    remestimate = int(issue.raw['fields']['aggregatetimeestimate'])

                wl = getWorkLog(issue.key, worklogs)
                #print('{0}:{1}:{2}'.format(issue.key, origestimate, remestimate))

                if wl is not None:
                    wlConcat = wlConcat + wl

                concatStr = concatStr + issue.key + ','

                for field in FieldList:
                    f = 'issue.fields.' + field


                    # Sprint Details {list}
                    if field == 'customfield_10000':
                        sp=''
                        for s in eval(f) or []:
                            sp = s.split(",")
                            spConcat =  spConcat + ','.join(sp[1:] + ['\n'])
                        #print(sp[1:])
                        if sp[1:] !='':
                            sprintname= sp[3]
                            concatStr = concatStr + sprintname.replace('name=','') + ','
                        else:
                            concatStr = concatStr + '' + ','
                    # Account WBS Code {dict}
                    elif field == 'customfield_10600':
                        try:
                            if (issue.raw['fields']['customfield_10600']['id'] != '0'):
                                concatStr = concatStr + issue.raw['fields'][field]['name'] + ','
                                #print(issue.raw['fields'][field]['key'])
                            else:
                                concatStr = concatStr + ','
                        except TypeError:
                            concatStr = concatStr + ','

                    # fixVersions {list}
                    elif field == 'fixVersions':
                        fixver=''
                        fv=''
                        for fv in eval(f) or []:
                            fixver = str(fv)

                        if fv is not None:
                            concatStr = concatStr + fixver + ','
                    else:
                        try:
                            concatStr = concatStr + str(eval(f)) + ','
                        except TypeError:
                            concatStr = concatStr + ','
                        except AttributeError:
                            concatStr = concatStr + ','

                concatStr = concatStr + '\n'
            # print(concatStr)

            # Write Jira Issues to File
            writecsv(concatStr, JiraExtract, flist)

            # Write Work Logs to csv
            writecsv(wlConcat, WorkLogExtract, wlflist)

            # Write Sprint details to File
            writecsv(spConcat, SprintExtract, spflist)

     # Cleanse the Sprint file
    cleansesprintfile()

    # Create member file
    createTeamMembercsv()

    # Convert all csv files into Excel
    coneverttoxls()

            # **** GET JIRA ISSUES  **** ---->
    print('Completed..' + str(datetime.datetime.time(datetime.datetime.now())))

# Get work log for the given issue
def getWorkLog(issuekey, worklogs):
    #os = origestimate
    #cumremestimate = os
    #cummtimespent = 0
    retStr =''
    for w in worklogs:
        # print (w.issueId)
        #if origestimate > 0 :
        #    cumremestimate = (os - int(w.timeSpentSeconds))
        #cummtimespent = cummtimespent + int(w.timeSpentSeconds)

        #print('{0}:{1}:{2}:{3}'.format(w.timeSpentSeconds, os, cumremestimate, remestimate ))

        retStr = retStr + issuekey + ',' + str(w.id) + ',' + str(w.issueId) + ',' + str(w.started) + ',' + w.author.name + ',' + str(
            w.timeSpentSeconds) + ',' + '\n'
        #+ str(cumremestimate) + ',' + str(remestimate) + ',' + str(cummtimespent)
        #if origestimate > 0 :
        #    os  = cumremestimate
    return retStr


# Get Teams from Jira
def TeamListGet():
    JIRA_BASE_URL = 'https://jira.vectorams.co.nz'
    JiraBaseUrl = JIRA_BASE_URL
    team_list = []
    JIRAsession = requests.session()
    JIRAsession.auth = ("kannanr","Password01")

    # Get all Teams names
    team_url = JiraBaseUrl + '/rest/tempo-teams/1/team'
    url = team_url
    #print('team url:', url)

    r = JIRAsession.get(url)
    if r.status_code == 200:
        json_return = json.loads(r.text)

        # create clean Team list
        for entry in json_return:
            #print(entry)
            team_list.append({'id': entry['id'],
                               'name': entry['name'],
                               'summary': entry['summary']})
        return team_list

# Get team members by Team Id
def TeamMembersGet(teamId, teamName):
    JIRA_BASE_URL = 'https://jira.vectorams.co.nz'
    JiraBaseUrl = 'https://jira.vectorams.co.nz'
    jira_sub_dict = {}
    jira_parent_dict = {}
    #member_list = []
    JIRAsession = requests.session()
    JIRAsession.auth = ("kannanr","Password01")

    # Get all members details with Team Id
    team_url = JiraBaseUrl + '/rest/tempo-teams/2/team/{0}/member?type=user'
    url = team_url.format(teamId)
    #print('team url:', url)
    member_list=''
    r = JIRAsession.get(url)
    if r.status_code == 200:
        json_return = json.loads(r.text)

        # create clean Team list
        for entry in json_return:
            #print(entry)
            member_list = member_list + '\n' + str(entry['id']) + ',' + \
                          entry['member']['name'] + ',' + \
                          str(entry['member']['key']) + ',' + \
                          entry['member']['displayname'] + ',' + \
                          str(entry['membershipBean']['availability']) + ',' + str(teamId) + ',' + teamName

        #print (member_list)
        return member_list

# Get all Sprints in a Project
def GetSprintsList(projectKey):
    JiraBaseUrl = JIRA_BASE_URL

    JIRAsession = Jsetup()

    team_url = JiraBaseUrl + '/rest/greenhopper/latest/rapidviews/list?projectKey={0}'
    url = team_url.format(projectKey)

    sprint_list = ''
    r = JIRAsession.get(url)
    if r.status_code == 200:
        json_return = json.loads(r.text)
        print(json_return)
        # create clean Team list
        for entry in json_return:
            sprint_list = entry['views']

        print (sprint_list)
        #return member_list

# Create Team Member csv
def createTeamMembercsv():
    team_list = TeamListGet()
    for team in team_list:
        # print(team['id'])
        # list.append(TeamMembersGet(team['id'], team['name']))
        #print(team['name'])
        data = TeamMembersGet(team['id'], team['name'])
        writecsv(data, TeamMemberExtract, MembersFieldList)

def worklog_trial():
    jira = setUp()
    issue = jira.issue('TECHOVER-129')

    worklogs = jira.worklogs(issue)
    wlConcat = ''
    for w in worklogs:
        # print(w.raw)
        wlConcat = wlConcat + str(w.id) + ',' + str(w.created) + ',' + str(
            w.issueId) + ',' + w.author.name + ',' + w.comment + ',' + str(
            w.timeSpentSeconds) + ',' + w.timeSpent + '\n'
    print(wlConcat)
    # print (worklogs)

def List_all_Fields():
    jira = setUp()
    issue = jira.issue('SWAG2-10177')
    for field_name in issue.raw['fields']:
        # print("Field:", field_name, "Value:", issue.raw['fields'][field_name])
        print("Field:{0}, Value:{1}".format(field_name, issue.raw['fields'][field_name]))

def listallboards():
    jira=setUp()
    issue = jira.issue('SWAG2-2522')
    jt=jira.transitions(issue)
    p=jira.project(issue.fields.project)

    boards = jira.boards()
    for board in boards:
        print('{0} : {1}'.format(str(board.id).ljust(5), board.name))


    #for f in p.raw['fields']:
    #    print(p.raw['fields'][f])

def listallTeams():
    jira=setUp()
    issue = jira.issue('DDNZ-1077')
    # Fetch all fields
    allfields = jira.fields()

    # Make a map from field name -> field id
    nameMap = {field['name']: field['id'] for field in allfields}
    # Fetch an issue

    # Look up custom fields by name using the map
    print(nameMap)
    print (getattr(issue.fields, nameMap['name']['id']))

    #for f in p.raw['fields']:
    #    print(p.raw['fields'][f])

def main():

    #Project list
    projectList = ["DDNZ","SWAG2","SWAG3"]
    for project in projectList:
        importFromJira(project)

    #listallTeams()
    #a= coneverttoxls('JiraIssues.csv')

    #GetSprintsList('DDNZ')
    #listallboards()
    #List_all_Fields()
    #worklog_trial()
    #createtable('DDNZ.xlsx','A1:B5')
    #cleansesprintfile()


if __name__ == '__main__':
    urllib3.disable_warnings()
    main()
