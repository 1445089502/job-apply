"""投递状态机测试（扩展状态）。"""
import pytest

from app.apply.state_machine import Status, can_transition, terminal_states, transition


def test_valid_transition():
    assert can_transition(Status.CREATED, Status.QUEUED)
    assert transition(Status.APPLYING, Status.SUBMITTED_UNCONFIRMED) == Status.SUBMITTED_UNCONFIRMED


def test_invalid_transition_raises():
    with pytest.raises(ValueError):
        transition(Status.CREATED, Status.SUCCESS)


def test_terminal_states():
    states = terminal_states()
    assert Status.SUCCESS in states
    assert Status.CANCELLED in states
    assert Status.DUPLICATE in states
    assert Status.UNKNOWN in states
    assert Status.QUEUED not in states


def test_extended_states():
    # doc/10 A-05：UNKNOWN / CANCELLED / DUPLICATE / HUMAN_TIMEOUT / SUBMITTED_UNCONFIRMED
    assert can_transition(Status.QUEUED, Status.DUPLICATE)
    assert can_transition(Status.APPLYING, Status.UNKNOWN)
    assert can_transition(Status.NEEDS_HUMAN, Status.HUMAN_TIMEOUT)
    assert can_transition(Status.HUMAN_TIMEOUT, Status.FAILED)
    assert can_transition(Status.FAILED, Status.QUEUED)  # 允许重试
