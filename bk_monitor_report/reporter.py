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
        chunk_size: int = 500,
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
        if chunk_size < 1:
            raise ValueError("chunk_size must greater than 1, receive: {}".format(chunk_size))
        self.chunk_size = chunk_size
        self._report_thread = None

    def _report(self, data: dict, session=None, **extras):
        sender = session or requests
        try:
            resp = sender.post(self.url, json=data)
        except Exception:
            logger.exception("[MonitorReporter]report fail, url: {}, extras: {}".format(self.url, extras))
            return

        if not resp.ok:
            logger.error(
                "[MonitorReporter]report fail, url: {}, extras: {}, resp: {}".format(self.url, extras, resp.text)
            )

        logger.info("[MonitorReporter]report finish: {}".format(resp.text))

    def _periodic_report_helper(self):
        report_start_time = time.perf_counter()
        try:
            self.report()
        except Exception:
            logger.exception("[MonitorReporter]periodic report fail")

        report_cost = time.perf_counter() - report_start_time
        logger.info("[MonitorReporter]periodic report cost {} seconds".format(report_cost))

        sleep_interval = self.report_interval - report_cost
        logger.info("[MonitorReporter]sleep {} seconds".format(sleep_interval))
        if sleep_interval > 0:
            time.sleep(sleep_interval)

    def _periodic_report(self):
        while True:
            self._periodic_report_helper()

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

    def generate_chunked_report_data(self):
        timestamp = round(time.time() * 1000)

        data = {"data_id": self.data_id, "access_token": self.access_token, "data": []}
        size = 0

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

            size += 1
            if size % self.chunk_size == 0:
                yield data
                data = {"data_id": self.data_id, "access_token": self.access_token, "data": []}

        if data["data"]:
            yield data

    def report_event(self, name: str, content: str, dimension: Optional[dict] = None):
        self._report(
            data={
                "data_id": self.data_id,
                "access_token": self.access_token,
                "data": [
                    {
                        "event_name": name,
                        "event": {"content": content},
                        "target": self.target,
                        "dimension": dimension or {},
                        "timestamp": round(time.time() * 1000),
                    }
                ],
            }
        )

    def report(self):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        for i, data in enumerate(self.generate_chunked_report_data(), 1):
            self._report(data=data, session=session, chunk=i)

    def start(self, *args, **kwargs):
        """
        args, kwargs: 可以用于启动reporter时传入自定义参数，如在celery worker中作为signal handler时会用到
        """
        if self._report_thread is not None:
            logger.warning("[MonitorReporter]reporter already started")
            return

        self.thread = threading.Thread(target=self._periodic_report, daemon=True)
        self.thread.start()
