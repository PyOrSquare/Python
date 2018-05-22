import datetime
import errno
import os
import fileinput
from jira import JIRA
from jira.resources import GreenHopperResource, TimeTracking, Resource, Issue, Worklog, CustomFieldOption
import json
#from lib.jirahelper import *

# <!----- PARAMETERS ------

jql = 'project = "SWAG2"'
SprintExtract = "Sprints.csv"
JiraExtract = "JiraIssues.csv"
WorkLogExtract = "WorkLogs.csv"


# ----- PARAMETERS ------>

def get_jira_admin_auth():
    # **** Credentials **** #
    # jira = JIRA(basic_auth=(userName, passwd), server='https://jira.vectorams.co.nz')
    serverName = 'https://jira.vectorams.co.nz'
    userName = 'kannanr'
    passwd = 'Password01'
    return JIRA(basic_auth=(userName, passwd),
                server='https://jira.vectorams.co.nz')


def setUp():
    jira = get_jira_admin_auth()
    return jira


def writecsv(data, filename, fieldNames):
    csv = open(filename, "a")
    # csv.write(fieldNames+ '\n')
    csv.write(data)
    # print (data)

    csv.close()
    return;


def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def writeHeader(filename, line):
    with open(filename, 'w+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)


def replacestrinfile(filename, text_to_search, replacement_text):
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')


def importFromJira():
    print('Started..' + str(datetime.datetime.time(datetime.datetime.now())))

    # Delete Extract files if already exist
    silentremove(JiraExtract)
    silentremove(SprintExtract)
    silentremove(WorkLogExtract)

    FieldList = ['issuetype', 'project', 'status', 'resolution', 'created', 'timeestimate',
                 'aggregatetimeoriginalestimate', 'aggregatetimeestimate',
                 'timespent', 'aggregatetimespent', 'resolutiondate', 'customfield_10000', 'customfield_10001',
                 'customfield_11412', 'customfield_10103', 'customfield_10600','fixVersions']

    flist = ','.join(FieldList)
    #flist = flist.replace('customfield_10000,', '')

    WLFieldList = ['id', 'created', 'issueId', 'author.name', 'timeSpentSeconds']
    wlflist = ','.join(WLFieldList)

    SPFieldList = ['rapidViewId', 'state', 'name', 'startDate', 'endDate', 'completeDate', 'sequence']
    spfieldremove= ['rapidViewId=', 'state=', 'name=', 'startDate=', 'endDate=', 'completeDate=', 'sequence=']
    spflist = ','.join(SPFieldList)

    # Add Header to Extracts
    writeHeader(JiraExtract, 'issuekey,' + flist)
    writeHeader(SprintExtract, spflist)
    writeHeader(WorkLogExtract, wlflist)

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
                print(issue.key)
                worklogs = jira.worklogs(issue.key)
                wl = getWorkLog(worklogs)
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

                concatStr = concatStr + '\n'
            # print(concatStr)

            # Write Jira Issues to File
            writecsv(concatStr, JiraExtract, flist)

            # Write Work Logs to csv
            writecsv(wlConcat, WorkLogExtract, wlflist)

            # Write Sprint details to File
            writecsv(spConcat, SprintExtract, spflist)

            # Cleanse Sprint file
            for rf in spfieldremove:
                replacestrinfile(SprintExtract, rf, '')
            # **** GET JIRA ISSUES  **** ---->
    print('Completed..' + str(datetime.datetime.time(datetime.datetime.now())))

def getWorkLog(worklogs):
    for w in worklogs:
        # print (w.issueId)
        retStr = str(w.id) + ',' + str(w.issueId) + ',' + str(w.created) + ',' + w.author.name + ',' + str(
            w.timeSpentSeconds) + '\n'

        return retStr


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
    issue = jira.issue('TECHOVER-129')
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
    issue = jira.issue('SWAG2-6606')
    # Fetch all fields
    allfields = jira.fields()
    print(issue.raw['fields']['customfield_10600']['id'])
    if (issue.raw['fields']['customfield_10600']['id'] != '0'):
        print(issue.raw['fields']['customfield_10600']['name'])
    else:
        print('Skip')
    # Make a map from field name -> field id
    nameMap = {field['name']: field['id'] for field in allfields}
    # Fetch an issue

    # You can now look up custom fields by name using the map
    print(nameMap)
    print (getattr(issue.fields, nameMap['name']['id']))

    #for f in p.raw['fields']:
    #    print(p.raw['fields'][f])

def main():
    importFromJira()
    #listallboards()
    #List_all_Fields()
    #worklog_trial()
    #listallTeams()

if __name__ == '__main__':
    main()
