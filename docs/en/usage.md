## Getting started


```python
from bk_monitor_report import MonitorReporter 

reporter = MonitorReporter(
    data_id=123,  # BK-Monitor Data ID
    access_token="xx",  # custom report Token
    target="test",   # report identifier
    url="http://xxx:10205/v2/push/",  # report gateway
) 

# generate report data
reporter.generate_report_data()

# report manually
reporter.report()

# start periodic reporting daemon
reporter.start()
```

### How to report celery worker's metrics


```python
from bk_monitor_report import MonitorReporter 
from bk_monitor_report.contrib.celery import MonitorReportStep

reporter = MonitorReporter(
    data_id=123,  # BK-Monitor Data ID
    access_token="xx",  # custom report Token
    target="test",   # report identifier
    url="http://xxx:10205/v2/push/",  # report gateway
) 

MonitorReportStep.setup_reporter(reporter)

# init celery app
app = Celery("proj")
# set Blueprint
app.steps["worker"].add(MonitorReportStep)
```