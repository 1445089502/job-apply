"""全自动投递：扩展状态机 + 幂等 + 补偿。"""
from app.apply.state_machine import Status, can_transition, terminal_states

__all__ = ["Status", "can_transition", "terminal_states"]
