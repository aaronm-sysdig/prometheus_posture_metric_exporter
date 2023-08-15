# Disclaimer

Notwithstanding anything that may be contained to the contrary in your agreement(s) with Sysdig, Sysdig provides no support, no updates, and no warranty or guarantee of any kind with respect to these script(s), including as to their functionality or their ability to work in your environment(s).  Sysdig disclaims all liability and responsibility with respect to any use of these scripts. 

# prometheus_posture_metric_exporter
A simple prometheus exporter that exports the Posture metrics that are displayed on the Posture landing page in Sysdig Secure.

## Configuration
Configuration YAML file

| Setting | Description | Example |
| config.apiToken | Sysdig API Token | `96feb702-3b2b-11ee-be56-0242ac120002` | 
| config.regionURL | Base region URL | `https://app.au1.sysdig.com` | 
| config.postureAPIEndpoint | Endpoint for posture metrics | `/api/cspm/v1/compliance/views` | 
| config.noDataThresholdHours | Number of hours that data cannot be older than, else we stop reporting metrics | `24` |
| settings.httpPort | Port to run HTTP server on | `8000` |
| settings.logLevel | Python logging level to use | `INFO` |

### Example configuration File
```
config:
  apiToken: <API token> 
  regionURL: <Rgion Base URL>
  postureAPIEndpoint: /api/cspm/v1/compliance/views
  noDataThresholdHours: 24 # maximum number of hours data can be before it is not exported (i.e ignored)

settings:
  httpPort: 8000 # HTTP port to listen on
  logLevel: INFO
```
### Execution
`prom_posture.py --config <Configuration file>`

Example: `prom_posture.py --config prom_posture_config.yaml`

### Example Console Output
```
2023-08-15 15:22:59 - INFO - Loading Yaml Config File: prom_posture_config.yaml
2023-08-15 15:22:59 - INFO - Starting Collection Run...
2023-08-15 15:22:59 - INFO - Starting Prometheus HTTP Server
2023-08-15 15:23:03 - INFO - Starting Collection Run...
```

### Example ficticuous GET of metrics
```
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 266.0
python_gc_objects_collected_total{generation="1"} 118.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable objects found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 57.0
python_gc_collections_total{generation="1"} 5.0
python_gc_collections_total{generation="2"} 0.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="9",patchlevel="6",version="3.9.6"} 1.0
# HELP sysdig_posture_passing_requirements Number of passing requirements
# TYPE sysdig_posture_passing_requirements gauge
sysdig_posture_passing_requirements{policy="Sysdig Kubernetes",zone="Entire Infrastructure"} 7.0
sysdig_posture_passing_requirements{policy="CIS Kubernetes V1.24 Benchmark",zone="Entire Infrastructure"} 15.0
sysdig_posture_passing_requirements{policy="All Posture Findings",zone="Entire Infrastructure"} 16.0
sysdig_posture_passing_requirements{policy="CIS Distribution Independent Linux Benchmark (Level 2 - Server)",zone="Entire Infrastructure"} 20.0
sysdig_posture_passing_requirements{policy="CIS Amazon Web Services Foundations Benchmark",zone="Entire Infrastructure"} 79.0
sysdig_posture_passing_requirements{policy="CIS Microsoft Azure Foundations Benchmark",zone="Entire Infrastructure"} 93.0
sysdig_posture_passing_requirements{policy="CIS Kubernetes V1.24 Benchmark",zone="Aarons Kubernetes Zone"} 15.0
sysdig_posture_passing_requirements{policy="CIS Microsoft Azure Foundations Benchmark",zone="Azure Zone"} 93.0
sysdig_posture_passing_requirements{policy="CIS Distribution Independent Linux Benchmark (Level 1 - Server)",zone="Linux Hosts"} 29.0
sysdig_posture_passing_requirements{policy="CIS Kubernetes V1.24 Benchmark",zone="Text4Shell-Deployment"} 26.0
# HELP sysdig_posture_failed_requirements Number of failed requirements
# TYPE sysdig_posture_failed_requirements gauge
sysdig_posture_failed_requirements{policy="Sysdig Kubernetes",zone="Entire Infrastructure"} 24.0
sysdig_posture_failed_requirements{policy="CIS Kubernetes V1.24 Benchmark",zone="Entire Infrastructure"} 101.0
sysdig_posture_failed_requirements{policy="All Posture Findings",zone="Entire Infrastructure"} 5.0
sysdig_posture_failed_requirements{policy="CIS Distribution Independent Linux Benchmark (Level 2 - Server)",zone="Entire Infrastructure"} 188.0
sysdig_posture_failed_requirements{policy="CIS Amazon Web Services Foundations Benchmark",zone="Entire Infrastructure"} 13.0
sysdig_posture_failed_requirements{policy="CIS Microsoft Azure Foundations Benchmark",zone="Entire Infrastructure"} 6.0
sysdig_posture_failed_requirements{policy="CIS Kubernetes V1.24 Benchmark",zone="Aarons Kubernetes Zone"} 101.0
sysdig_posture_failed_requirements{policy="CIS Microsoft Azure Foundations Benchmark",zone="Azure Zone"} 6.0
sysdig_posture_failed_requirements{policy="CIS Distribution Independent Linux Benchmark (Level 1 - Server)",zone="Linux Hosts"} 136.0
sysdig_posture_failed_requirements{policy="CIS Kubernetes V1.24 Benchmark",zone="Text4Shell-Deployment"} 88.0
# HELP sysdig_posture_evaluated_resources Number of evaluated resources
# TYPE sysdig_posture_evaluated_resources gauge
sysdig_posture_evaluated_resources{policy="Sysdig Kubernetes",zone="Entire Infrastructure"} 0.0
sysdig_posture_evaluated_resources{policy="CIS Kubernetes V1.24 Benchmark",zone="Entire Infrastructure"} 0.0
sysdig_posture_evaluated_resources{policy="All Posture Findings",zone="Entire Infrastructure"} 0.0
sysdig_posture_evaluated_resources{policy="CIS Distribution Independent Linux Benchmark (Level 2 - Server)",zone="Entire Infrastructure"} 0.0
sysdig_posture_evaluated_resources{policy="CIS Amazon Web Services Foundations Benchmark",zone="Entire Infrastructure"} 0.0
sysdig_posture_evaluated_resources{policy="CIS Microsoft Azure Foundations Benchmark",zone="Entire Infrastructure"} 0.0
sysdig_posture_evaluated_resources{policy="CIS Kubernetes V1.24 Benchmark",zone="Aarons Kubernetes Zone"} 0.0
sysdig_posture_evaluated_resources{policy="CIS Microsoft Azure Foundations Benchmark",zone="Azure Zone"} 0.0
sysdig_posture_evaluated_resources{policy="CIS Distribution Independent Linux Benchmark (Level 1 - Server)",zone="Linux Hosts"} 0.0
sysdig_posture_evaluated_resources{policy="CIS Kubernetes V1.24 Benchmark",zone="Text4Shell-Deployment"} 0.0
# HELP sysdig_posture_failed_controls Number of failed controls
# TYPE sysdig_posture_failed_controls gauge
sysdig_posture_failed_controls{policy="Sysdig Kubernetes",zone="Entire Infrastructure"} 41.0
sysdig_posture_failed_controls{policy="CIS Kubernetes V1.24 Benchmark",zone="Entire Infrastructure"} 106.0
sysdig_posture_failed_controls{policy="All Posture Findings",zone="Entire Infrastructure"} 513.0
sysdig_posture_failed_controls{policy="CIS Distribution Independent Linux Benchmark (Level 2 - Server)",zone="Entire Infrastructure"} 271.0
sysdig_posture_failed_controls{policy="CIS Amazon Web Services Foundations Benchmark",zone="Entire Infrastructure"} 14.0
sysdig_posture_failed_controls{policy="CIS Microsoft Azure Foundations Benchmark",zone="Entire Infrastructure"} 6.0
sysdig_posture_failed_controls{policy="CIS Kubernetes V1.24 Benchmark",zone="Aarons Kubernetes Zone"} 106.0
sysdig_posture_failed_controls{policy="CIS Microsoft Azure Foundations Benchmark",zone="Azure Zone"} 6.0
sysdig_posture_failed_controls{policy="CIS Distribution Independent Linux Benchmark (Level 1 - Server)",zone="Linux Hosts"} 199.0
sysdig_posture_failed_controls{policy="CIS Kubernetes V1.24 Benchmark",zone="Text4Shell-Deployment"} 90.0
# HELP sysdig_posture_high_severity_violations_resource Number of high severity resource violations
# TYPE sysdig_posture_high_severity_violations_resource gauge
sysdig_posture_high_severity_violations_resource{policy="Sysdig Kubernetes",zone="Entire Infrastructure"} 165.0
sysdig_posture_high_severity_violations_resource{policy="CIS Kubernetes V1.24 Benchmark",zone="Entire Infrastructure"} 331.0
sysdig_posture_high_severity_violations_resource{policy="All Posture Findings",zone="Entire Infrastructure"} 1015.0
sysdig_posture_high_severity_violations_resource{policy="CIS Distribution Independent Linux Benchmark (Level 2 - Server)",zone="Entire Infrastructure"} 395.0
sysdig_posture_high_severity_violations_resource{policy="CIS Amazon Web Services Foundations Benchmark",zone="Entire Infrastructure"} 25.0
sysdig_posture_high_severity_violations_resource{policy="CIS Microsoft Azure Foundations Benchmark",zone="Entire Infrastructure"} 52.0
sysdig_posture_high_severity_violations_resource{policy="CIS Kubernetes V1.24 Benchmark",zone="Aarons Kubernetes Zone"} 331.0
sysdig_posture_high_severity_violations_resource{policy="CIS Microsoft Azure Foundations Benchmark",zone="Azure Zone"} 52.0
sysdig_posture_high_severity_violations_resource{policy="CIS Distribution Independent Linux Benchmark (Level 1 - Server)",zone="Linux Hosts"} 186.0
sysdig_posture_high_severity_violations_resource{policy="CIS Kubernetes V1.24 Benchmark",zone="Text4Shell-Deployment"} 167.0
# HELP sysdig_posture_medium_severity_violations_resource Number of medium severity resource violations
# TYPE sysdig_posture_medium_severity_violations_resource gauge
sysdig_posture_medium_severity_violations_resource{policy="Sysdig Kubernetes",zone="Entire Infrastructure"} 279.0
sysdig_posture_medium_severity_violations_resource{policy="CIS Kubernetes V1.24 Benchmark",zone="Entire Infrastructure"} 197.0
sysdig_posture_medium_severity_violations_resource{policy="All Posture Findings",zone="Entire Infrastructure"} 578.0
sysdig_posture_medium_severity_violations_resource{policy="CIS Distribution Independent Linux Benchmark (Level 2 - Server)",zone="Entire Infrastructure"} 81.0
sysdig_posture_medium_severity_violations_resource{policy="CIS Amazon Web Services Foundations Benchmark",zone="Entire Infrastructure"} 23.0
sysdig_posture_medium_severity_violations_resource{policy="CIS Microsoft Azure Foundations Benchmark",zone="Entire Infrastructure"} 1.0
sysdig_posture_medium_severity_violations_resource{policy="CIS Kubernetes V1.24 Benchmark",zone="Aarons Kubernetes Zone"} 197.0
sysdig_posture_medium_severity_violations_resource{policy="CIS Microsoft Azure Foundations Benchmark",zone="Azure Zone"} 1.0
sysdig_posture_medium_severity_violations_resource{policy="CIS Distribution Independent Linux Benchmark (Level 1 - Server)",zone="Linux Hosts"} 13.0
sysdig_posture_medium_severity_violations_resource{policy="CIS Kubernetes V1.24 Benchmark",zone="Text4Shell-Deployment"} 37.0
# HELP sysdig_posture_low_severity_violations_resource Number of low severity resource violations
# TYPE sysdig_posture_low_severity_violations_resource gauge
sysdig_posture_low_severity_violations_resource{policy="Sysdig Kubernetes",zone="Entire Infrastructure"} 367.0
sysdig_posture_low_severity_violations_resource{policy="CIS Kubernetes V1.24 Benchmark",zone="Entire Infrastructure"} 174.0
sysdig_posture_low_severity_violations_resource{policy="All Posture Findings",zone="Entire Infrastructure"} 530.0
sysdig_posture_low_severity_violations_resource{policy="CIS Distribution Independent Linux Benchmark (Level 2 - Server)",zone="Entire Infrastructure"} 8.0
sysdig_posture_low_severity_violations_resource{policy="CIS Amazon Web Services Foundations Benchmark",zone="Entire Infrastructure"} 0.0
sysdig_posture_low_severity_violations_resource{policy="CIS Microsoft Azure Foundations Benchmark",zone="Entire Infrastructure"} 0.0
sysdig_posture_low_severity_violations_resource{policy="CIS Kubernetes V1.24 Benchmark",zone="Aarons Kubernetes Zone"} 174.0
sysdig_posture_low_severity_violations_resource{policy="CIS Microsoft Azure Foundations Benchmark",zone="Azure Zone"} 0.0
sysdig_posture_low_severity_violations_resource{policy="CIS Distribution Independent Linux Benchmark (Level 1 - Server)",zone="Linux Hosts"} 0.0
sysdig_posture_low_severity_violations_resource{policy="CIS Kubernetes V1.24 Benchmark",zone="Text4Shell-Deployment"} 19.0
```
