import requests
from config import Config

# Web API Documentation: http://your-sonarqube-url/web_api

CONF = Config()

class SonarExporter:

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.base_url = CONF.sonar_url

    def _request(self, endpoint):
        req = requests.get("{}/{}".format(self.base_url, endpoint), auth=(self.user, self.password))
        if req.status_code != 200:
            return req.status_code
        else:
            return req.json()

    def get_all_projects(self):
        return self._request(endpoint='api/components/search?qualifiers=TRK')

    def get_all_metrics(self):
        return self._request(endpoint='api/metrics/search')

    def get_project_branches(self, project):
        return self._request(endpoint="api/project_branches/list?project={}".format( project))

    def get_measures_component_by_branch(self, component_key, metric_key,branch):
        return self._request(endpoint="api/measures/component_tree?component={}&metricKeys={}&branch={}".format(component_key, metric_key,branch))


class Project:

    def __init__(self, project, key):
        self.project = project
        self.key = key
        self._branches = []
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def branches(self):
        return self._branches

    @branches.setter
    def branches(self, value):
        self._branches.extend(value)

class Branch:

    def __init__(self, name):
        self._metrics = []
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def metrics(self):
        return self._metrics

    @metrics.setter
    def metrics(self, value):
        self._metrics.extend(value)

class Metric:

    def __init__(self):
        self._name = None
        self._value = None
        self._description = None
        self._domain = None

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value):
        self._domain = value

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_all_projects_with_metrics():
    projects = []
    metrics = []

    client = SonarExporter(CONF.sonar_user, CONF.sonar_password)
    
    branch_mandatory_list = tuple(CONF.sonar_branch_list.split(','))
    all_projects = client.get_all_projects()
    all_metrics = client.get_all_metrics()

    white_list_domains = ['Reliability','Security','Maintainability','Duplications','Coverage','Size','Issues']
    black_list_metrics = ['duplications_data','ncloc_language_distribution']

    for metric in all_metrics['metrics']:
        m = Metric()
        if 'description' in metric.keys() and metric['domain'] in white_list_domains and metric['key'] not in black_list_metrics:
            m.id = metric['id']
            m.description = metric['description']
            m.key = metric['key']
            m.domain = metric['domain']
            metrics.append(m)

    
    for project in all_projects['components']:
        p = Project(project=project['project'], key=project['key'])
        p.name = project['name']
        branches = client.get_project_branches(project=p.project)
        branch_list = [b['name'] for b in branches['branches'] if b['name'].startswith(branch_mandatory_list)]

        for branch in branch_list:
            
            b = Branch(name=branch)
            metrics_names = [metric.key for metric in metrics]
            metrics_chunks = chunks(metrics_names,15)
            
            for chunk in metrics_chunks:
                metric_keys = ','.join(map(str, chunk))
                measures = client.get_measures_component_by_branch(component_key=p.key,metric_key=metric_keys,branch=branch)
                
                for measure in measures['baseComponent']['measures']:
                    if 'value' in measure.keys():
                        description = next((x.description for x in metrics if x.description is not None), None)
                        b.metrics.append({
                            "metric":measure['metric'],
                            "value":measure['value'],
                            "description":description
                    })

            p.branches.append(b)



        
        
        projects.append(p)
        return projects


get_all_projects_with_metrics()