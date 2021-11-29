from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    interface,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-fev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

DECIMALS = 8
INITIAL_VALUE = 200000000000


def get_account(index=None, id=None):
    # for specific account into the ganache-cli testnet accounts
    if index:
        return accounts[index]
    # For specific account configured on brownie accounts
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        # for any of the local or forked environemnts return the account with index zero
        return accounts[0]

    # Default option, load from config file

    return accounts.add(config["wallets"]["from_key"])


# mapping the MockV3Aggregator and the VRFCoordinator and LinkToken

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and return
    that mock contract.

        Args:
            contract_name (strings):

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # Verifiy if the contract is already deployed
        # It's the same as check MockV3Aggregator.length
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]  # Same as MockV3Aggregator[-1]
    else:
        # set the address for the contract based on it's name
        contract_address = config["networks"][network.show_active()][contract_name]
        # we need the address and the abi
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})

    print("Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract successful")
    return tx
