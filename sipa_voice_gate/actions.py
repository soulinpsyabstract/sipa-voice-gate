"""Track 2 - action executors.

Dry-run stubs for the hackathon demo: they record what *would* happen and
succeed. Real integrations register a callable under the same action type and
replace the stub - the gate and the loop above do not change.

    from sipa_voice_gate.actions import register
    register("send_money", my_real_transfer_fn)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class ActionOutcome:
    ok: bool
    detail: str


Executor = Callable[[dict], ActionOutcome]


def _dry(label: str) -> Executor:
    def run(args: dict) -> ActionOutcome:
        return ActionOutcome(True, f"[dry-run] {label}: {args}")
    return run


REGISTRY: dict[str, Executor] = {
    "send_money": _dry("transfer"),
    "delete_file": _dry("delete"),
    "send_email": _dry("email"),
    "purchase": _dry("purchase"),
    "change_setting": _dry("setting change"),
    "read_data": lambda args: ActionOutcome(True, f"here is what I found for {args.get('query', args)}"),
}


def register(action_type: str, executor: Executor) -> None:
    REGISTRY[action_type] = executor


def execute(action_type: str, args: dict) -> ActionOutcome:
    fn = REGISTRY.get(action_type)
    if fn is None:
        return ActionOutcome(False, f"no executor registered for '{action_type}'")
    return fn(args)
