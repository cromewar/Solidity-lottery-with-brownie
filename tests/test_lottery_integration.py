from scripts.helpful_scripts import (
    FORKED_LOCAL_ENVIRONMENTS,
    get_account,
    fund_with_link,
)
from scripts.deploy_lottery import deploy_lottery
from brownie import network
import pytest
import time


def test_can_pick_winner():
    if network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enterToLottery({"from": account, "value": lottery.getEntranceFee()})
    lottery.enterToLottery({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
