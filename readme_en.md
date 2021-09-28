[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](https://github.com/TencentBlueKing/bk-monitor-report/blob/master/LICENSE.txt)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/TencentBlueKing/bk-monitor-report/pulls)
[![BK Pipelines Status](https://api.bkdevops.qq.com/process/api/external/pipelines/projects/bkapppipeline/p-8892cf59f0ea4a928234706a232ae3b8/badge?X-DEVOPS-PROJECT-ID=bkapppipeline)](https://api.bkdevops.qq.com/process/api/external/pipelines/projects/bkapppipeline/p-8892cf59f0ea4a928234706a232ae3b8/badge?X-DEVOPS-PROJECT-ID=bkapppipeline)

[(English Documents Available)](readme_en.md)

## Overview

BK-Monitor custom report Python SDK.

## Features

- [Basic] BK-Monitor custom report API
- [Basic] convert prometheus metrics to BK-Monitor custom metrics
- [Basic] periodic reporting daemon
- [Contrib] Celery worker metrics custom report Blueprint

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

### Installation

```
pip install bk-monitor-report
```

### Usage

- [usage doc](docs/en/usage.md)

## Roadmap

- [release log](release.md)

## Support

- [bk forum](https://bk.tencent.com/s-mart/community)
- [bk DevOps online video tutorial(In Chinese)](https://cloud.tencent.com/developer/edu/major-100008)
- Contact us, technical exchange QQ group:

<img src="https://github.com/Tencent/bk-PaaS/raw/master/docs/resource/img/bk_qq_group.png" width="250" hegiht="250" align=center />


## BlueKing Community

- [BK-CI](https://github.com/Tencent/bk-ci)：a continuous integration and continuous delivery system that can easily present your R & D process to you.
- [BK-BCS](https://github.com/Tencent/bk-bcs)：a basic container service platform which provides orchestration and management for micro-service business.
- [BK-BCS-SaaS](https://github.com/Tencent/bk-bcs-saas)：a SaaS provides users with highly scalable, flexible and easy-to-use container products and services.
- [BK-PaaS](https://github.com/Tencent/bk-PaaS)：an development platform that allows developers to create, develop, deploy and manage SaaS applications easily and quickly.
- [BK-SOPS](https://github.com/Tencent/bk-sops)：an lightweight scheduling SaaS  for task flow scheduling and execution through a visual graphical interface. 
- [BK-CMDB](https://github.com/Tencent/bk-cmdb)：an enterprise-level configuration management platform for assets and applications.

## Contributing

If you have good ideas or suggestions, please let us know by Issues or Pull Requests and contribute to the Blue Whale Open Source Community.

## License

Based on the MIT protocol. Please refer to [LICENSE](LICENSE.txt)
