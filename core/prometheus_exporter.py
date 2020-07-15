from prometheus_client.core import GaugeMetricFamily
import prometheus_client as prom
import time
from sonarqube_exporter import get_all_projects_with_metrics

class CustomSonarExporter:

    def __init__(self):
        pass

    def collect(self):
        projects = get_all_projects_with_metrics()

        for project in projects:
            for branch in project.branches:
                for metric in branch.metrics:
                    label_list = ['key', 'name','branch']
                    label_values = []
                    value_to_set = None

                    label_values.append(project.key)
                    label_values.append(project.name)
                    label_values.append(branch.name)
                    
                    
                    value_to_set = metric['value']

                    gauge = GaugeMetricFamily(
                        name="sonar_{}".format(metric['metric']),
                        documentation=metric['description'],
                        labels=label_list
                    )

                    gauge.add_metric(
                        labels=label_values,
                        value=value_to_set
                    )
                    yield gauge

if __name__ == "__main__":
    custom_exporter = CustomSonarExporter()
    prom.REGISTRY.register(custom_exporter)
    prom.start_http_server(9120)

    while True:
        time.sleep(30)