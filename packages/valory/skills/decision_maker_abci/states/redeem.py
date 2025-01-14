# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2023 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains the redeem state of the decision-making abci app."""

from typing import Type

from packages.valory.skills.abstract_round_abci.base import get_name
from packages.valory.skills.decision_maker_abci.payloads import (
    MultisigTxPayload,
    RedeemPayload,
)
from packages.valory.skills.decision_maker_abci.states.base import (
    Event,
    SynchronizedData,
    TxPreparationRound,
)


class RedeemRound(TxPreparationRound):
    """A round in which the agents prepare a tx to redeem the winnings."""

    payload_class: Type[MultisigTxPayload] = RedeemPayload
    selection_key = TxPreparationRound.selection_key + (
        get_name(SynchronizedData.policy),
        get_name(SynchronizedData.utilized_tools),
    )
    none_event = Event.NO_REDEEMING
