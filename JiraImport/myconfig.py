# <!----- PARAMETERS ------

JIRA_BASE_URL = 'https://jira.org.co.nz'

SprintExtract = "Sprints"
JiraExtract = "JiraIssues"
WorkLogExtract = "WorkLogs"
ReleasesExtract = "Releases"
TeamMemberExtract = 'TeamMembers'

#date = time.strftime('%Y%m%d%H%M%S')
xlext = '.xlsx'
csvext = '.csv'

# Jira Issue field list
FieldList = ['issuetype', 'project', 'status', 'resolution', 'created', 'timeestimate',
                 'aggregatetimeoriginalestimate', 'aggregatetimeestimate',
                 'timespent', 'aggregatetimespent', 'resolutiondate', 'customfield_10000', 'customfield_10001',
                 'customfield_11412', 'customfield_10103', 'customfield_10600','fixVersions', 'customfield_10008', 'summary', 'priority', 'customfield_10400']

# Sprint field list
SPFieldList = ['rapidViewId', 'state', 'name', 'startDate', 'endDate', 'completeDate', 'sequence']

# Sprints: Fields to removed
spfieldremove= ['rapidViewId=', 'state=', 'name=', 'startDate=', 'endDate=', 'completeDate=', 'sequence=']

# Work Log field list
WLFieldList = ['issuekey','id', 'issueId', 'created','author.name', 'timeSpentSeconds']
#,'runningremainingestimate','totalremaining', 'cummtimespent'

# Members fields list
MembersFieldList =['id', 'name', 'key', 'displayname', 'availability', 'team', 'teamname']

# Releases Fields List
ReleasesFieldList = 'self, id, description, name, archived, released, projectId'

# ----- PARAMETERS ------>
