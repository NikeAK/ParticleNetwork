import random

from web3 import AsyncWeb3, Account
from web3.middleware import geth_poa
from eth_account.messages import encode_defunct

from data.service import Network
from data.config import MULTIPLIER_GAS


class Web3Utils:
    def __init__(
            self,
            network: Network,
            private_key: str,
            proxy: str = None
        ):
        self.network = network
        self.private_key = private_key
        self.address = Account.from_key(self.private_key).address

        self.w3 = AsyncWeb3(
            AsyncWeb3.AsyncHTTPProvider(endpoint_uri=random.choice(self.network.rpc)),
            request_kwargs = {'proxy': proxy}
        )

    def sign_message(self, hexstr: str|None = None, message: str|None = None) -> str:
        return Account.sign_message(encode_defunct(hexstr=hexstr, text=message), self.private_key).signature.hex()
    
    def encode(self, types: list, args: list) -> bytes:
        return self.w3.codec.encode(types, args)
    
    def update_provider(self, new_provider: str) -> None:
        self.w3.provider = AsyncWeb3.AsyncHTTPProvider(new_provider)

    async def get_chain_id(self) -> int:
        return await self.w3.eth.chain_id
    
    async def get_balance(self) -> float:
        balance_wei = await self.w3.eth.get_balance(self.address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        return float(balance_eth)
    
    # TODO Переделать, если газ высокий
    async def calculate_gas(self) -> tuple[int, int]:
        fee_history = await self.w3.eth.fee_history(4, 'latest', [20, 50])

        last_block = await self.get_last_block()

        base_fee = last_block['baseFeePerGas']

        priority_fee_1 = fee_history['reward'][0][0]
        priority_fee_2 = fee_history['reward'][0][1]
        max_priority_fee = int((priority_fee_1 + priority_fee_2) / 2)
        max_fee_per_gas = int((base_fee + max_priority_fee) * MULTIPLIER_GAS)

        return max_fee_per_gas, max_priority_fee
    
    async def send_transaction(self, to: str, value: int | float | None = None, data: str | None = None) -> str:

        tx_params = {
            'from': self.address,
            'to': self.w3.to_checksum_address(to),
            'nonce': await self.w3.eth.get_transaction_count(self.address),
            'chainId': self.network.chain_id,
        }

        if data:
            tx_params['data'] = data
        
        if self.network.eip1559_support:
            max_fee_per_gas, max_priority_fee = await self.calculate_gas()

            tx_params['maxFeePerGas'] = max_fee_per_gas
            tx_params['maxPriorityFeePerGas'] = max_priority_fee
        else:
            tx_params['gasPrice'] = await self.w3.eth.gas_price
        
        if value:
            tx_params['value'] = self.w3.to_wei(value, 'ether')

        estimated_gas = await self.w3.eth.estimate_gas(tx_params)
        tx_params['gas'] = int(estimated_gas * MULTIPLIER_GAS)
        return await self.send_txn(tx_params)
            
    async def get_last_block(self) -> dict:
        self.w3.middleware_onion.inject(geth_poa.async_geth_poa_middleware, layer=0)
        last_block = await self.w3.eth.get_block('latest')
        self.w3.middleware_onion.remove(geth_poa.async_geth_poa_middleware)
        return last_block
    
    async def send_txn(self, data: dict, timeout: int = 180, wait_tx: bool = True) -> str:
        sign_txn = self.w3.eth.account.sign_transaction(data, self.private_key)
        tx_hash = await self.w3.eth.send_raw_transaction(sign_txn.rawTransaction)
        if wait_tx:
            await self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        return tx_hash.hex()
    
