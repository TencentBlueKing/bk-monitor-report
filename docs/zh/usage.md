## Getting started

```python
from bk_monitor_report import MonitorReporter 

reporter = MonitorReporter(
    data_id=123,  # 监控 Data ID
    access_token="xx",  # 自定义上报 Token
    target="test",   # 上报唯一标志符
    url="http://xxx:10205/v2/push/",  # 上报地址
) 

# 生成上报数据
reporter.generate_report_data()

# 手动进行上报
reporter.report()

# 启动守护进程周期性自动上报
reporter.start()
```

### 如何上报 celery worker 进程的数据

如果要上报 celery worker 进程的数据，请确保 worker 是以非 prefork 模式启动的

```python
from bk_monitor_report import MonitorReporter 
from bk_monitor_report.contrib.celery import MonitorReportStep

reporter = MonitorReporter(
    data_id=123,  # 监控 Data ID
    access_token="xx",  # 自定义上报 Token
    target="test",   # 上报唯一标志符
    url="http://xxx:10205/v2/push/",  # 上报地址
) 
MonitorReportStep.setup_reporter(reporter)

# 初始化 celery app
app = Celery("proj")
# 设置启动蓝图
app.steps["worker"].add(MonitorReportStep)
```