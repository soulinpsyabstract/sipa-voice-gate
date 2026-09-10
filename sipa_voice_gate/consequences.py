"""Track 2 — consequence model.

Two pieces:

  ConsequenceProfile   what an action does along axes that matter for the gate
  predict_consequences  the downstream chain of an action, in plain language,
                        worked out *before* the action runs

The second piece is the SIPA bet in miniature: don't wait for a bad action and
notice it afterwards - expand the action into what it sets in motion and what
becomes irreversible, and decide on that.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConsequenceProfile:
    reversible: bool = True          # can this be undone by us alone?
    external_effect: bool = False    # does it leave the system / reach a third party?
    moves_value: bool = False        # money, assets, funds
    destroys_data: bool = False      # delete / overwrite
    changes_config: bool = False     # standing rules, settings, permissions
    magnitude: float = 0.0           # value moved (money, etc.), when it means something
    unit: str = ""
    target_count: int = 1            # how many external targets this hits at once

    def is_consequential(self) -> bool:
        return (
            self.moves_value
            or self.destroys_data
            or self.changes_config
            or self.external_effect
            or not self.reversible
        )


# Downstream-effect graph: action type -> ordered plain-language consequences.
_CHAINS: dict[str, list[str]] = {
    "send_money": [
        "moves funds out of your account",
        "the recipient can move or withdraw them right away",
        "there is no unilateral way to pull the transfer back",
    ],
    "delete_file": [
        "removes the file from disk",
        "anything that pointed at it will start failing",
        "it is not recoverable unless a backup already exists",
    ],
    "send_email": [
        "delivers a message to the recipient in your name",
        "you cannot unsend it once it has left",
        "the recipient may forward or archive it",
    ],
    "purchase": [
        "charges your saved payment method",
        "commits you to the vendor's cancellation and return terms",
    ],
    "change_setting": [
        "changes how the agent behaves for every later request",
        "future actions will quietly follow the new rule",
    ],
    "read_data": [
        "returns information to you and changes nothing",
    ],
}


def predict_consequences(action_type: str, profile: ConsequenceProfile) -> list[str]:
    """The chain of effects to expect if this action runs."""
    chain = list(_CHAINS.get(action_type, []))
    if chain:
        return chain

    # Unknown action: build a conservative chain from the profile alone.
    if profile.moves_value:
        chain.append("moves value you may not get back")
    if profile.destroys_data:
        chain.append("destroys data that may not be recoverable")
    if profile.changes_config:
        chain.append("changes standing configuration")
    if profile.external_effect:
        chain.append("has an effect outside this system")
    if not profile.reversible and not chain:
        chain.append("cannot be undone")
    if not chain:
        chain.append("effect is unknown - treating it as unsafe")
    return chain
