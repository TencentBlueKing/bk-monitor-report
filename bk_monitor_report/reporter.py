# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import time
import logging
import threading
from typing import Optional

import requests
from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    generate_latest,
)
from prometheus_client.parser import text_string_to_metric_families


logger = logging.getLogger("bk-monitor-report")


class MonitorReporter:
    def __init__(
        self,
        data_id: int,
        access_token: str,
        target: str,
        url: str,
        report_interval: int = 60,
        registry: Optional[CollectorRegistry] = REGISTRY,
    ):
        """

        :param data_id: 监控 Data ID
        :param access_token: 自定义上报 Token
        :param target: 上报唯一标志符
        :param url: 上报地址
        :param report_interval: 周期性上报间隔，单位为秒, defaults to 60
        :param registry: promethues 指标获取来源, defaults to REGISTRY
        """
        self.data_id = data_id
        self.access_token = access_token
        self.target = target
        self.url = url
        self.registry = registry
        self.report_interval = report_interval
        self._report_thread = None

    def generate_report_data(self):
        data = {"data_id": self.data_id, "access_token": self.access_token, "data": []}
        timestamp = round(time.time() * 1000)

        metrics_text = generate_latest(self.registry).decode("utf-8")
        for family in text_string_to_metric_families(metrics_text):
            for sample in family.samples:
                data["data"].append(
                    {
                        "metrics": {sample.name: sample.value},
                        "target": self.target,
                        "dimension": sample.labels,
                        "timestamp": timestamp,
                    }
                )

        return data

    def report(self):
        data = self.generate_report_data()

        try:
            resp = requests.post(self.url, json=data)
        except Exception:
            logger.exception("data({}) report to {} failed".format(data, self.url))
            return

        if not resp.ok:
            logger.error(
                "data({}) report to {} failed, resp: {}".format(
                    data, self.url, resp.text
                )
            )

        logger.info("report finish: {}".format(resp.text))

    def _periodic_report(self):
        while True:
            try:
                self.report()
            except Exception:
                logger.exception("periodic report to {} failed".format(self.url))

            time.sleep(self.report_interval)

    def start(self):
        if self._report_thread is not None:
            logger.warning("reporter already started")
            return

        self.thread = threading.Thread(target=self._periodic_report, daemon=True)
        self.thread.start()
