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
from unittest.mock import MagicMock, patch, call

from bk_monitor_report.reporter import MonitorReporter


def test_init():
    reporter = MonitorReporter(data_id=1, access_token="token", target="t", url="u")
    assert reporter.data_id == 1
    assert reporter.access_token == "token"
    assert reporter.target == "t"
    assert reporter.url == "u"
    assert reporter.report_interval == 60
    assert reporter.registry is not None

    reporter = MonitorReporter(
        data_id=1, access_token="token", target="t", url="u", report_interval=120, registry="reg"
    )
    assert reporter.data_id == 1
    assert reporter.access_token == "token"
    assert reporter.target == "t"
    assert reporter.url == "u"
    assert reporter.report_interval == 120
    assert reporter.registry == "reg"


def test_generate_report_data():
    timestamp = round(time.time() * 1000) - 1
    reporter = MonitorReporter(data_id=1, access_token="token", target="t", url="u")
    data = reporter.generate_report_data()

    assert data["data_id"] == reporter.data_id
    assert data["access_token"] == reporter.access_token
    assert len(data["data"]) > 0
    for item in data["data"]:
        assert item["timestamp"] > timestamp


def test_generate_chunked_report_data():
    timestamp = round(time.time() * 1000) - 1

    def validate_chunkd(chunks):
        for data in chunks:
            assert data["data_id"] == reporter.data_id
            assert data["access_token"] == reporter.access_token
            assert len(data["data"]) > 0
            for item in data["data"]:
                assert item["timestamp"] > timestamp

    # smallest chunk size
    reporter = MonitorReporter(data_id=1, access_token="token", target="t", url="u", chunk_size=1)
    chunks = list(reporter.generate_chunked_report_data())
    assert len(chunks) > 1
    validate_chunkd(chunks)

    # large chunk size
    reporter = MonitorReporter(data_id=1, access_token="token", target="t", url="u", chunk_size=100000)
    chunks = list(reporter.generate_chunked_report_data())
    assert len(chunks) > 0
    validate_chunkd(chunks)


def test_report_success():
    reporter = MonitorReporter(data_id=1, access_token="token", target="t", url="u")
    reporter.generate_chunked_report_data = MagicMock(return_value=["report_data_1", "report_data_2", "report_data_3"])
    post = MagicMock(return_value=MagicMock(ok=True))

    with patch("bk_monitor_report.reporter.requests.Session.post", post):
        reporter.report()

    post.assert_has_calls(
        [
            call(reporter.url, json="report_data_1"),
            call(reporter.url, json="report_data_2"),
            call(reporter.url, json="report_data_3"),
        ]
    )


def test_report__post_raise():
    reporter = MonitorReporter(data_id=1, access_token="token", target="t", url="u")
    reporter.generate_chunked_report_data = MagicMock(return_value=["report_data_1", "report_data_2", "report_data_3"])
    post = MagicMock(side_effect=Exception)

    with patch("bk_monitor_report.reporter.requests.Session.post", post):
        reporter.report()

    post.assert_has_calls(
        [
            call(reporter.url, json="report_data_1"),
            call(reporter.url, json="report_data_2"),
            call(reporter.url, json="report_data_3"),
        ]
    )


def test_report__post_resp_is_not_ok():
    reporter = MonitorReporter(data_id=1, access_token="token", target="t", url="u")
    reporter.generate_chunked_report_data = MagicMock(return_value=["report_data_1", "report_data_2", "report_data_3"])
    post = MagicMock(return_value=MagicMock(ok=False))

    with patch("bk_monitor_report.reporter.requests.Session.post", post):
        reporter.report()

    post.assert_has_calls(
        [
            call(reporter.url, json="report_data_1"),
            call(reporter.url, json="report_data_2"),
            call(reporter.url, json="report_data_3"),
        ]
    )


def test___periodic_report_helper():
    reporter = MonitorReporter(data_id=1, access_token="token", target="t", url="u")
    reporter.report = MagicMock()
    sleep = MagicMock()

    with patch("bk_monitor_report.reporter.time.sleep", sleep):
        reporter._periodic_report_helper()

    reporter.report.assert_called_once()
    sleep.assert_called_once()


def test_start():
    reporter = MonitorReporter(data_id=1, access_token="token", target="t", url="u")
    threading = MagicMock()

    with patch("bk_monitor_report.reporter.threading", threading):
        reporter.start()

    assert reporter.thread is not None
    threading.Thread.assert_called_once_with(target=reporter._periodic_report, daemon=True)
    reporter.thread.start.assert_called_once()


def test_report_event():
    reporter = MonitorReporter(data_id=1, access_token="token", target="t", url="u")
    reporter._report = MagicMock()

    reporter.report_event(name="my_event", content="event content", dimension={"a": "b"})
    reporter._report.assert_called_once()
    data_args = reporter._report.call_args[1]["data"]
    assert data_args["data_id"] == reporter.data_id
    assert data_args["access_token"] == reporter.access_token
    assert "timestamp" in data_args["data"][0]
    assert data_args["data"][0]["event_name"] == "my_event"
    assert data_args["data"][0]["event"]["content"] == "event content"
    assert data_args["data"][0]["target"] == reporter.target
    assert data_args["data"][0]["dimension"] == {"a": "b"}
