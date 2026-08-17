"""投递状态机：扩展状态以表达外部平台未知结果、取消、重复、人工超时。

doc/10 A-05 要求补充 UNKNOWN / CANCELLED / DUPLICATE / HUMAN_TIMEOUT / SUBMITTED_UNCONFIRMED。
"""
from enum import StrEnum


class Status(StrEnum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    APPLYING = "APPLYING"
    SUBMITTED_UNCONFIRMED = "SUBMITTED_UNCONFIRMED"  # 已提交但平台结果未知
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"  # 外部结果未知，需人工确认
    CANCELLED = "CANCELLED"
    DUPLICATE = "DUPLICATE"  # 重复投递被拦截
    NEEDS_HUMAN = "NEEDS_HUMAN"  # 验证码/异常，需人工介入
    HUMAN_TIMEOUT = "HUMAN_TIMEOUT"  # 人工介入超时


# 允许的状态流转
_TRANSITIONS: dict[Status, set[Status]] = {
    Status.CREATED: {Status.QUEUED},
    Status.QUEUED: {Status.APPLYING, Status.CANCELLED, Status.DUPLICATE},
    Status.APPLYING: {
        Status.SUBMITTED_UNCONFIRMED,
        Status.SUCCESS,
        Status.FAILED,
        Status.UNKNOWN,
        Status.NEEDS_HUMAN,
    },
    Status.SUBMITTED_UNCONFIRMED: {Status.SUCCESS, Status.FAILED, Status.UNKNOWN},
    Status.NEEDS_HUMAN: {Status.APPLYING, Status.CANCELLED, Status.HUMAN_TIMEOUT},
    Status.HUMAN_TIMEOUT: {Status.FAILED},
    Status.FAILED: {Status.QUEUED},  # 允许重试
    # 终态：SUCCESS / CANCELLED / DUPLICATE / UNKNOWN
    Status.SUCCESS: set(),
    Status.CANCELLED: set(),
    Status.DUPLICATE: set(),
    Status.UNKNOWN: set(),
}


def terminal_states() -> set[Status]:
    return {s for s, nxt in _TRANSITIONS.items() if not nxt}


def can_transition(src: Status, dst: Status) -> bool:
    return dst in _TRANSITIONS.get(src, set())


def transition(src: Status, dst: Status) -> Status:
    """执行状态流转，非法流转抛 ValueError。"""
    if not can_transition(src, dst):
        raise ValueError(f"非法状态流转: {src.value} -> {dst.value}")
    return dst
