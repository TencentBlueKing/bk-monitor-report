[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](https://github.com/TencentBlueKing/bk-monitor-report/blob/master/LICENSE.txt)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/TencentBlueKing/bk-monitor-report/pulls)
[![BK Pipelines Status](https://api.bkdevops.qq.com/process/api/external/pipelines/projects/bkapppipeline/p-8892cf59f0ea4a928234706a232ae3b8/badge?X-DEVOPS-PROJECT-ID=bkapppipeline)](https://api.bkdevops.qq.com/process/api/external/pipelines/projects/bkapppipeline/p-8892cf59f0ea4a928234706a232ae3b8/badge?X-DEVOPS-PROJECT-ID=bkapppipeline)

[(English Documents Available)](readme_en.md)

## Overview

蓝鲸监控自定义上报 Python SDK，支持获取当前系统配置的 prometheus metrics 上报到蓝鲸监控中

## Features

- [Basic] 蓝鲸监控自定义上报 API
- [Basic] 将 prometheus metrics 转换为蓝鲸监控自定义上报指标
- [Basic] 周期性上报守护进程
- [Contrib] Celery worker metrics 自定义上报蓝图

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

```python
from bk_monitor_report import MonitorReporter 

reporter = MonitorReporter(
    data_id=123,  # 监控 Data ID
    access_token="xx",  # 自定义上报 Token
    target="test",   # 上报唯一标志符
    url="http://xxx:10205/v2/push/",  # 上报地址
) 
MonitorReportStep.setup_reporter(reporter)

# 初始化 celery app
app = Celery("proj")

# 如果worker非多进程模式，可以设置启动蓝图
from bk_monitor_report.contrib.celery import MonitorReportStep
app.steps["worker"].add(MonitorReportStep)

# 如果worker为多进程模式，可以通过监听进程初始化信号进行处理
from celery.signals import worker_process_init
worker_process_init.connect(reporter.start, weak=False)
```

### Installation

```
pip install bk-monitor-report
```

### Usage

- [使用文档](docs/zh/usage.md)

## Roadmap

- [版本日志](release.md)

## Support

- [蓝鲸论坛](https://bk.tencent.com/s-mart/community)
- [蓝鲸 DevOps 在线视频教程](https://cloud.tencent.com/developer/edu/major-100008)
- 联系我们，技术交流QQ群：

<img src="https://github.com/Tencent/bk-PaaS/raw/master/docs/resource/img/bk_qq_group.png" width="250" hegiht="250" align=center />


## BlueKing Community

- [BK-CI](https://github.com/Tencent/bk-ci)：蓝鲸持续集成平台是一个开源的持续集成和持续交付系统，可以轻松将你的研发流程呈现到你面前。
- [BK-BCS](https://github.com/Tencent/bk-bcs)：蓝鲸容器管理平台是以容器技术为基础，为微服务业务提供编排管理的基础服务平台。
- [BK-BCS-SaaS](https://github.com/Tencent/bk-bcs-saas)：蓝鲸容器管理平台SaaS基于原生Kubernetes和Mesos自研的两种模式，提供给用户高度可扩展、灵活易用的容器产品服务。
- [BK-PaaS](https://github.com/Tencent/bk-PaaS)：蓝鲸PaaS平台是一个开放式的开发平台，让开发者可以方便快捷地创建、开发、部署和管理SaaS应用。
- [BK-SOPS](https://github.com/Tencent/bk-sops)：标准运维（SOPS）是通过可视化的图形界面进行任务流程编排和执行的系统，是蓝鲸体系中一款轻量级的调度编排类SaaS产品。
- [BK-CMDB](https://github.com/Tencent/bk-cmdb)：蓝鲸配置平台是一个面向资产及应用的企业级配置管理平台。

## Contributing

如果你有好的意见或建议，欢迎给我们提 Issues 或 Pull Requests，为蓝鲸开源社区贡献力量。

## License

基于 MIT 协议， 详细请参考[LICENSE](LICENSE.txt)
