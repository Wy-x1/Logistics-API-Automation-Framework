# -*- coding: utf-8 -*-
import time

import pytest

from common.readyaml import ReadYamlData
from base.removefile import remove_file
from common.dingRobot import send_dd_msg
from conf.setting import dd_msg

import warnings

yfd = ReadYamlData()


@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    # 禁用HTTPS告警，ResourceWarning
    warnings.simplefilter('ignore', ResourceWarning)

    yfd.clear_yaml_data()
    remove_file("./report/temp", ['json', 'txt', 'attach', 'properties'])


#def generate_test_summary(terminalreporter):
#    """生成测试结果摘要字符串"""
#    total = terminalreporter._numcollected
#    passed = len(terminalreporter.stats.get('passed', []))
#    failed = len(terminalreporter.stats.get('failed', []))
#    error = len(terminalreporter.stats.get('error', []))
#    skipped = len(terminalreporter.stats.get('skipped', []))
#    duration = time.time() - terminalreporter._sessionstarttime

#    summary = f"""
#    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
#    测试用例总数：{total}
#    测试通过数：{passed}
#    测试失败数：{failed}
#    错误数量：{error}
#    跳过执行数量：{skipped}
#    执行总时长：{duration}
#    """
#    print(summary)
#    return summary

def generate_test_summary(terminalreporter):
    """生成测试结果摘要字符串"""
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))

    # --- 修改开始：增加强力容错，防止时间计算崩坏 ---
    try:
        # 1. 尝试获取开始时间属性
        start_time = getattr(terminalreporter, '_session_start', getattr(terminalreporter, '_sessionstarttime', 0))

        # 2. 根据类型进行计算
        if isinstance(start_time, (float, int)) and start_time > 0:
            # 如果是数字且大于0，直接计算
            duration = time.time() - start_time
        elif hasattr(start_time, 'timestamp'):
            # 如果是时间对象（带timestamp方法），转换后计算
            duration = time.time() - start_time.timestamp()
        else:
            # 如果是未知对象（如 Instant），且无法转换，直接给默认值 0，避免报错退出
            duration = 0.0
    except Exception:
        # 万一发生其他未知错误，兜底为 0
        duration = 0.0
    # --- 修改结束 ---

    summary = f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration:.2f}秒
    """
    print(summary)
    return summary

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """自动收集pytest框架执行的测试结果并打印摘要信息"""
    summary = generate_test_summary(terminalreporter)
    if dd_msg:
        send_dd_msg(summary)


