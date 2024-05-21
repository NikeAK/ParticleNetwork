import asyncio
import hashlib
import json
import uuid
import twitter
import discord
import re
import random

from datetime import datetime, timezone

from core.utils import Web3Utils
from core.utils import Captcha
from core.database.models import Accounts

from core.client import BaseAsyncSession, RequestsAttempts

from core.utils import logger
from data.service import Network, AllNetwork
from data.config import DEPOSIT_PRATICLE, TRANSFER_AMOUNT, DELAY_ALL_BALANCES, MAX_GAS_USDG, DELAY_TRANSACTIONS, DEPOSIT_USDG, RANDOM_TX


class ParticleNetwork:
    pioneer_api = 'https://pioneer-api.particle.network'
    universal_api = 'https://universal-api.particle.network/'
    rpc_particle = 'https://rpc.particle.network'
    
    def __init__(
            self,
            thread  : int,
            account : Accounts,
            network : Network
        ):
        self.thread  = thread
        self.account = account
        self.network = network
        self.mackey = None

        self.session = BaseAsyncSession(
            thread  = self.thread,
            proxy   = self.account.proxy
        )
        self.w3u = Web3Utils(
            network         = self.network,
            private_key     = self.account.private_key,
            proxy           = self.account.proxy
        )

    @staticmethod
    def generate_mac(data: dict) -> str:
        data_str = json.dumps(data, separators=(',', ':'))
        hash_obj = hashlib.sha256()
        hash_obj.update(data_str.encode())
        return hash_obj.hexdigest()

    @staticmethod
    def get_unix_timestamp() -> int:
        return int(datetime.now(timezone.utc).timestamp())
    
    def create_op_signature(
            self,
            valid_until: int,
            valid_after: int,
            merkle_root: bytes,
            merkle_proof: bytes,
            r_signature: bytes,
        ):
        S_S = '0x1965cd0Bf68Db7D007613E79d8386d48B9061ea6'
        return self.w3u.encode(["bytes","address"],[self.w3u.encode(["uint48","uint48","bytes32","bytes32[]","bytes"],[valid_until,valid_after,merkle_root,merkle_proof,r_signature]),S_S]).hex()

    def create_common_data(self, update_data: dict | None = None) -> dict:
        mac_data = {
            "device_id": self.account.device_id,
            "mac_key": self.mackey,
            "project_app_uuid": "79df412e-7e9d-4a19-8484-a2c8f3d65a2e",
            "project_client_key": "cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76",
            "project_uuid": "91bf10e7-5806-460d-95af-bef2a3122e12",
            "random_str": str(uuid.uuid4()),
            "sdk_version": "web_1.0.0",
            "timestamp": ParticleNetwork.get_unix_timestamp()
        }
        if update_data:
            combined_data = update_data
            combined_data.update(mac_data)
            if combined_data['mac_key'] is None:
                combined_data['mac_key'] = "5706dd1db5aabc45c649ecc01fdac97100de8e8655715d810d0fb2080e6cea24"
        else:
            combined_data = mac_data
        return combined_data
    
    def create_common_params(self, mac_data: dict, update_params: dict | None = None) -> dict:
        mac_params = ParticleNetwork.generate_mac(mac_data)
        params = {
            'timestamp': mac_data['timestamp'],
            'random_str': mac_data['random_str'],
            'device_id': self.account.device_id,
            'sdk_version': 'web_1.0.0',
            'project_uuid': '91bf10e7-5806-460d-95af-bef2a3122e12',
            'project_client_key': 'cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76',
            'project_app_uuid': '79df412e-7e9d-4a19-8484-a2c8f3d65a2e',
            'mac': mac_params
        }
        if update_params:
            combined_params = update_params
            combined_params.update(params)
        else:
            combined_params = params
        return combined_params
    
    async def login(self) -> dict:
        sign_msg = f'Welcome to Particle Pioneer!\n\nWallet address:\n{self.account.address}\n\nNonce:\n{self.account.device_id}'
        signature = self.w3u.sign_message(message=sign_msg)

        mac_data = self.create_common_data({
            "device_id": self.account.device_id,
            "loginInfo": {
                "address": self.account.address,
                "signature": signature
            },
            "loginMethod": "evm_wallet",
            "loginSource": "metamask",
        })

        params = self.create_common_params(mac_data)

        payload = {
            "loginMethod": "evm_wallet",
            "loginSource": "metamask",
            "loginInfo": {
                "address": self.account.address,
                "signature": signature
            }
        }
        
        self.session.headers.update({
            'Auth-Type': 'Basic',
            'Authorization': 'Basic OUMzUnRxQmNCcUJuQk5vYjo3RGJubng3QlBxOENBOFBI'
        })

        response = await self.session.post(self.pioneer_api+'/users', params=params, json=payload)
        answer = response.json()

        self.mackey = answer['macKey']
        self.session.headers['Authorization'] = f'Bearer {answer['token']}'
        self.session.headers.pop('Auth-Type')

        logger.success(f'Поток {self.thread} | Выполнен вход <m>ParticleNetwork</m> | <i>PrivateKey: <g><u>{self.account.private_key[:5]}***{self.account.private_key[61:]}</u></g></i>')
        return answer
    
    async def get_user_info(self) -> dict:
        # Вернет неверный баланс поинтов, если сделать транзакцию и НЕ ВЫПОЛНИТЬ CHECK (Для проверки поинтов лучше использовать check_earned_points)
        mac_data = self.create_common_data()
        params = self.create_common_params(mac_data)

        response = await self.session.get(self.pioneer_api+'/users', params=params)
        answer = response.json()
        return answer

    async def enter_refcode(self) -> bool:
        for attempt in range(1, 4):
            mac_data = self.create_common_data({
                "code": self.account.refcode
            })
            
            params = self.create_common_params(mac_data)

            payload = {
                "code": self.account.refcode
            }

            response = await self.session.post(self.pioneer_api+'/users/invitation_code', params=params, json=payload)
            answer = response.json()

            if answer.get('referrerAddress'):
                logger.success(f'Поток {self.thread} | Установил <c>RefCode</c>: <m><u>{self.account.refcode}</u></m>')
                return True
            else:
                logger.error(f'Поток {self.thread} | Не удалось установить <r>RefCode</r>: <r>{answer.get('message')}</r> | Попытка <y>{attempt}</y>/<r>3</r>, сплю 5 сек.')
                await asyncio.sleep(5)
        else:
            return False

    async def bind_twitter(self, twitter_token: str) -> bool:
        for attempt in range(1, 4):
            bind_param = {
                'response_type': 'code',
                'client_id': 'c1h0S1pfb010TEVBUnh2N3U3MU86MTpjaQ',
                'redirect_uri': 'https://pioneer.particle.network/signup',
                'scope': 'tweet.read users.read',
                'state': 'twitter-' + str(uuid.uuid4()),
                'code_challenge': 'challenge',
                'code_challenge_method': 'plain',
            }

            account = twitter.Account(auth_token=twitter_token)
            async with twitter.Client(account=account, proxy=self.account.proxy) as twitter_client:
                twitter_code = await twitter_client.oauth2(**bind_param)

            captcha_code = await Captcha(self.thread, self.account.proxy).bind()

            mac_data = {
                "cfTurnstileResponse": captcha_code,
                "code": twitter_code,
                "device_id": self.account.device_id,
                "mac_key": self.mackey,
                "project_app_uuid": "79df412e-7e9d-4a19-8484-a2c8f3d65a2e",
                "project_client_key": "cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76",
                "project_uuid": "91bf10e7-5806-460d-95af-bef2a3122e12",
                "provider": "twitter",
                "random_str": str(uuid.uuid4()),
                "sdk_version": "web_1.0.0",
                "timestamp": ParticleNetwork.get_unix_timestamp()
            }

            params = self.create_common_params(mac_data)

            payload = {
                "code": twitter_code,
                "provider": "twitter",
                "cfTurnstileResponse": captcha_code
            }
            
            response = await self.session.post(self.pioneer_api+'/users/bind', params=params, json=payload)
            answer = response.json()
        
            if answer.get('twitterId'):
                logger.success(f'Поток {self.thread} | Привязал <c>Twitter</c> - <c>TwitterID</c>: <g>{answer['twitterId']}</g>')
                return True
            else:
                logger.error(f'Поток {self.thread} | Не удалось привязать <r>Twitter</r>: <r>{answer.get('message')}</r> | Попытка <y>{attempt}</y>/<r>3</r>, сплю 5 сек.')
                await asyncio.sleep(5)
        else:
            return False
    
    async def bind_discord(self, auth_token: str) -> dict:
        for attempt in range(1, 4):
            client = discord.Client()
            await client.login(auth_token)

            application_id = 1229361725870964818
            bind_params = {
                'scopes': ['identify email'],
                'response_type': 'code',
                'redirect_uri': 'https://pioneer.particle.network/signup',
                'state': 'discord-' + str(uuid.uuid4())
            }
            auth_url = await client.create_authorization(application_id, **bind_params)
            discord_code = re.search(r'code=([^&]+)', auth_url).group(1)

            captcha_code = await Captcha(self.thread, self.account.proxy).bind()

            mac_data = {
                "cfTurnstileResponse": captcha_code,
                "code": discord_code,
                "device_id": self.account.device_id,
                "mac_key": self.mackey,
                "project_app_uuid": "79df412e-7e9d-4a19-8484-a2c8f3d65a2e",
                "project_client_key": "cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76",
                "project_uuid": "91bf10e7-5806-460d-95af-bef2a3122e12",
                "provider": "discord",
                "random_str": str(uuid.uuid4()),
                "sdk_version": "web_1.0.0",
                "timestamp": ParticleNetwork.get_unix_timestamp()
            }

            params = self.create_common_params(mac_data)

            payload = {
                "code": discord_code,
                "provider": "discord",
                "cfTurnstileResponse": captcha_code
            }
            
            response = await self.session.post(self.pioneer_api+'/users/bind', params=params, json=payload)
            answer = response.json()

            if answer.get('discordId'):
                logger.success(f'Поток {self.thread} | Привязал <c>Discord</c> - <c>DiscordID</c>: <g>{answer['discordId']}</g>')
                return True
            else:
                logger.error(f'Поток {self.thread} | Не удалось привязать <r>Discord</r>: <r>{answer.get('message')}</r> | Попытка <y>{attempt}</y>/<r>3</r>, сплю 5 сек.')
                await asyncio.sleep(5)
        else:
            return False
    
    async def deposit_usdg(self, amount: int | float) -> str:
        logger.info(f'Поток {self.thread} | Инициализирую транзакцию <y>Particle Deposit USDG...</y>')
        balance_USDG = await self.get_balance(2011)

        mac_data = {
            "amount": str(int(amount*1e18)),
            "chainId": self.network.chain_id,
            "device_id": self.account.device_id,
            "mac_key": self.mackey,
            "project_app_uuid": "79df412e-7e9d-4a19-8484-a2c8f3d65a2e",
            "project_client_key": "cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76",
            "project_uuid": "91bf10e7-5806-460d-95af-bef2a3122e12",
            "random_str": str(uuid.uuid4()),
            "sdk_version": "web_1.0.0",
            "timestamp": ParticleNetwork.get_unix_timestamp(),
            "tokenAddress": "0x0000000000000000000000000000000000000000"
        }

        params = self.create_common_params(mac_data)

        payload = {
            "chainId": self.network.chain_id,
            "tokenAddress": "0x0000000000000000000000000000000000000000",
            "amount": mac_data['amount']
        }

        response = await self.session.post(self.pioneer_api+'/deposits/deposit_tx', params=params, json=payload)
        answer = response.json()

        txhash = await self.w3u.send_transaction(
            to = answer['tx']['to'],
            value = amount,
            data = answer['tx']['data']
        )

        logger.success(f'Поток {self.thread} | Транзакция <g>Particle Deposit USDG</g> | <i>Value: <g>{amount:.6f}</g> <e>${self.network.token}</e></i> | <i>TxHash: <k>{txhash}</k></i>')

        while True:
            new_balance_USDG = await self.get_balance(2011)
            if new_balance_USDG > balance_USDG:
                logger.success(f'Поток {self.thread} | <g>Particle Deposit USDG</g> подтвержден!')
                break
            else:
                logger.info(f'Поток {self.thread} | Жду подтверждение <y>Particle Deposit USDG...</y>')
                await asyncio.sleep(15)
        return txhash

    async def top_up_particle(self, amount: int | float) -> str:
        logger.info(f'Поток {self.thread} | Инициализирую транзакцию <y>Particle Top-Up...</y>')
        balance_particle = await self.get_balance(self.network.chain_id)

        txhash = await self.w3u.send_transaction(
            to = self.account.address_particle,
            value = amount,
        )

        logger.success(f'Поток {self.thread} | Транзакция <g>Particle Top-Up</g> | <i>Value: <g>{amount:.6f}</g> <e>${self.network.token}</e></i> | <i>TxHash: <k>{txhash}</k></i>')

        while True:
            new_balance_particle = await self.get_balance(self.network.chain_id)
            if new_balance_particle > balance_particle:
                logger.success(f'Поток {self.thread} | <g>Particle Top-Up</g> подтвержден!')
                break
            else:
                logger.info(f'Поток {self.thread} | Жду подтверждение <y>Particle Top-Up...</y>')
                await asyncio.sleep(10)
        return txhash

    async def get_deposits(self, page: int | str = 1, count: int | str = 100) -> list:
        mac_data = self.create_common_data({
            "count": str(count),
            "device_id": self.account.device_id,
            "mac_key": self.mackey,
            "page": str(page),
        })

        params = self.create_common_params(mac_data, {
            'page': str(page),
            'count': str(count),
        })

        response = await self.session.get(self.pioneer_api+'/deposits', params=params)
        answer = response.json()
        return answer['data']

    async def get_transactions(self, page: int | str = 1, count: int | str = 100) -> list:
        payload = {
            "jsonrpc": "2.0",
            "chainId": 11155420,
            "method": "universal_getCrossChainUserOperations",
            "params": [
                self.account.address_particle,
                {
                    "page": page,
                    "limit": count
                }
            ]
        }
        response = await self.session.post(self.universal_api, json=payload)
        answer = response.json()
        return answer['result']['data']
    
    async def check_checkin(self) -> bool:
        '''
        :return: Выполнил сегодня check-in?
        '''
        mac_data = self.create_common_data()
        params = self.create_common_params(mac_data)

        response = await self.session.post(self.pioneer_api+'/streaks/check_streak', params=params, json={})
        answer = response.json()
        return answer['success']
    
    async def get_balance(self, chainid: str | int, address: str | None = None) -> int | float:
        params = {
            'chainId': chainid,
            'projectUuid': '91bf10e7-5806-460d-95af-bef2a3122e12',
            'projectKey': 'cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76'
        }

        payload = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "eth_getBalance",
            "params": [
                address or self.account.address_particle,
                "latest"
            ]
        }

        response = await self.session.post(self.rpc_particle+'/evm-chain', params=params, json=payload, custom_headers=self.session.DEFAULT_HEADERS)
        answer = response.json()

        balance_wei = int(answer['result'], 16)
        balance_eth = balance_wei / 1e18
        return balance_eth
    
    async def check_deposit_point(self, logl: bool = False) -> bool:
        mac_data = self.create_common_data()
        params = self.create_common_params(mac_data)

        response = await self.session.post(self.pioneer_api+'/users/check_deposit_point', params=params, json={})
        answer = response.json()
        if logl:
            if answer['success']:
                logger.success(f'Поток {self.thread} | <i><u>Обновил статистику DEPOSIT_POINTS на сервере!</u></i>')
            else:
                logger.error(f'Поток {self.thread} | <i><u>Не удалось обновить статистику DEPOSIT_POINTS на сервере, данные будут устаревшие!</u></i>')
        return answer['success']
    
    async def check_tx_point(self, logl: bool = False) -> bool:
        mac_data = self.create_common_data()
        params = self.create_common_params(mac_data)

        response = await self.session.post(self.pioneer_api+'/users/check_tx_point', params=params, json={})
        answer = response.json()
        if logl:
            if answer['success']:
                logger.success(f'Поток {self.thread} | <i><u>Обновил статистику TX_POINTS на сервере!</u></i>')
            else:
                logger.error(f'Поток {self.thread} | <i><u>Не удалось обновить статистику TX_POINTS на сервере, данные будут устаревшие!</u></i>')
        return answer['success']
    
    async def check_earned_points(self, logl: bool = False) -> list:
        await self.check_deposit_point(logl)
        await self.check_tx_point(logl)

        mac_data = self.create_common_data()
        params = self.create_common_params(mac_data)

        response = await self.session.get(self.pioneer_api+'/users/earned_points', params=params)
        answer = response.json()
        return answer

    async def get_stats_daily_point(self) -> dict:
        mac_data = self.create_common_data()
        params = self.create_common_params(mac_data)

        response = await self.session.get(self.pioneer_api+'/streaks/daily_point', params=params)
        answer = response.json()
        return answer
    
    async def claim_checkin(self) -> str:
        logger.info(f'Поток {self.thread} | Инициализирую транзакцию <y>Check-IN...</y>')
        stats_daily = await self.get_stats_daily_point()

        mac_data = self.create_common_data()
        params = self.create_common_params(mac_data)

        response = await self.session.post(self.pioneer_api+'/streaks/streak_tx', params=params, json={})
        answer = response.json()

        payload = {
            "jsonrpc": "2.0",
            "chainId": 11155420,
            "method": "universal_createCrossChainUserOperation",
            "params": [
                {
                    "name": "UNIVERSAL",
                    "version": "1.0.0",
                    "ownerAddress": self.account.address
                },
                [
                    {
                        "to": answer['tx']['to'],
                        "data": answer['tx']['data'],
                        "chainId": 11155420
                    }
                ]
            ]
        }

        response = await self.session.post(self.universal_api, json=payload)
        answer = response.json()

        userOps = answer['result']['userOps']

        timestamp = ParticleNetwork.get_unix_timestamp()
        valid_until = timestamp+600
        valid_after = timestamp-600

        params = {
            'chainId': '11155420',
            'projectUuid': '91bf10e7-5806-460d-95af-bef2a3122e12',
            'projectKey': 'cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76'
        }

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "particle_aa_createMultiChainUnsignedData",
            "params": [
                {
                    "name": "UNIVERSAL",
                    "version": "1.0.0",
                    "ownerAddress": self.account.address
                },
                {
                    "multiChainConfigs": [
                        {
                            "chainId": 11155420,
                            "userOpHash": userOps[0]['userOpHash'],
                            "validUntil": valid_until,
                            "validAfter": valid_after
                        },
                        {
                            "chainId": 2011,
                            "userOpHash": userOps[1]['userOpHash'],
                            "validUntil": valid_until,
                            "validAfter": valid_after
                        }
                    ]
                }
            ]
        }

        response = await self.session.post(self.rpc_particle+'/evm-chain', params=params, json=payload, custom_headers=self.session.DEFAULT_HEADERS)
        answer = response.json()

        sign_tx_info = answer['result']

        signature = self.w3u.sign_message(hexstr=sign_tx_info['merkleRoot'])

        merkle_root = bytes.fromhex(sign_tx_info['merkleRoot'][2:])
        merkle_proof = [bytes.fromhex(sign_tx_info['data'][0]['merkleProof'][0][2:])]
        merkle_proof_2 = [bytes.fromhex(sign_tx_info['data'][1]['merkleProof'][0][2:])]
        r_signature = bytes.fromhex(signature[2:])

        first_signature = self.create_op_signature(
            valid_until = valid_until,
            valid_after = valid_after,
            merkle_root = merkle_root,
            merkle_proof = merkle_proof,
            r_signature = r_signature
        )

        second_signature = self.create_op_signature(
            valid_until = valid_until,
            valid_after = valid_after,
            merkle_root = merkle_root,
            merkle_proof = merkle_proof_2,
            r_signature = r_signature
        )

        captcha_code = await Captcha(self.thread, self.account.proxy).checkin()

        payload = {
            "jsonrpc": "2.0",
            "chainId": 11155420,
            "method": "universal_sendCrossChainUserOperation",
            "params": [[
                {"chainId": 11155420, "signature": "",},
                {"chainId": 2011, "signature": ""}
            ]],
            'cfTurnstileResponse': captcha_code
        }

        payload['params'][0][0].update(userOps[0]['userOp'])
        payload['params'][0][0]['signature'] = '0x' + first_signature

        payload['params'][0][1].update(userOps[1]['userOp'])
        payload['params'][0][1]['signature'] = '0x' + second_signature
        
        response = await self.session.post(self.universal_api, json=payload, custom_headers=self.session.DEFAULT_HEADERS)
        answer = response.json()

        _id = answer['result']['_id']

        while True:
            payload = {
                "jsonrpc": "2.0",
                "chainId": 11155420,
                "method": "universal_getCrossChainUserOperation",
                "params": [_id]
            }

            response = await self.session.post(self.universal_api, json=payload, custom_headers=self.session.DEFAULT_HEADERS)
            answer = response.json()

            if answer['result'].get('targetUserOpEvent') is None:
                logger.info(f'Поток {self.thread} | Ожидаю транзакцию <y>Check-IN...</y>, сплю 3 сек.')
                await asyncio.sleep(3)
            else:
                txhash = answer['result']['targetUserOpEvent']['txHash']
                logger.success(f'Поток {self.thread} | Транзакция <g>Check-IN</g> | <i>TxHash: <k>{txhash}</k></i>')
                break
        
        while True:
            already_checkin = await self.check_checkin()
            if not already_checkin:
                logger.info(f'Поток {self.thread} | Жду подтверждение <y>Check-IN</y>')
                await asyncio.sleep(5)
            else:
                streak_days = stats_daily['streakDays'] + (stats_daily['streakDays'] != 1)
                logger.success(f'Поток {self.thread} | Задание <c>Check-IN</c> выполнено! | <i>Streak: <g>{streak_days}</g> days, <g>+{stats_daily['dailyPoint']}</g> <m>$PARTI</m>!</i>')
                break
        return txhash

    async def claim_retweet(self) -> bool:
        mac_data = self.create_common_data()
        params = self.create_common_params(mac_data)

        response = await self.session.post(self.pioneer_api+'/users/check_retweet_point', params=params, json={})
        answer = response.json()
        return answer['success']

    async def calculate_gas(self) -> tuple:
        params = {
            'chainId': self.network.chain_id,
            'projectUuid': '91bf10e7-5806-460d-95af-bef2a3122e12',
            'projectKey': 'cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76',
            'method': 'particle_suggestedGasFees'
        }

        payload = {
            "method": "particle_suggestedGasFees",
            "params": [],
            "id": str(uuid.uuid4()),
            "jsonrpc": "2.0"
        }

        response = await self.session.post(self.rpc_particle+'/evm-chain', params=params, json=payload, custom_headers=self.session.DEFAULT_HEADERS)
        answer = response.json()['result']

        maxFeePerGas = hex(int(float(answer['high']['maxFeePerGas'])*1e9))
        maxPriorityFeePerGas = hex(int(float(answer['high']['maxPriorityFeePerGas'])*1e9))
        return maxFeePerGas, maxPriorityFeePerGas
    
    async def estimate_gas(self, amount: int | float) -> str:
        params = {
            'chainId': self.network.chain_id,
            'projectUuid': '91bf10e7-5806-460d-95af-bef2a3122e12',
            'projectKey': 'cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76',
            'method': 'eth_estimateGas'
        }

        payload = {
            "method": "eth_estimateGas",
            "params": [{
                "value": hex(int(amount*1e18)),
                "to": self.account.address,
                "data": "0x",
                "from": self.account.address_particle
            }],
            "id": str(uuid.uuid4()),
            "jsonrpc": "2.0"
        }

        response = await self.session.post(self.rpc_particle+'/evm-chain', params=params, json=payload, custom_headers=self.session.DEFAULT_HEADERS)
        answer = response.json()
        return answer['result']

    async def send_transaction(self, amount: int | float) -> str:
        while True:
            gas = await self.estimate_gas(amount)

            payload = {
                "jsonrpc": "2.0",
                "chainId": self.network.chain_id,
                "method": "universal_createCrossChainUserOperation",
                "params": [
                    {
                        "name": "UNIVERSAL",
                        "version": "1.0.0",
                        "ownerAddress": self.account.address
                    },
                    [
                        {
                            "from": self.account.address_particle,
                            "to": self.account.address,
                            "value": hex(int(amount*1e18)),
                            "gasLimit": gas,
                            "action": "normal",
                            "data": "0x",
                            "gasLevel": "high",
                        }
                    ]
                ]
            }

            if self.network.chain_id == 97:
                payload['params'][0].update({'biconomyApiKey': 'u7F_1lHe5.f9c588e6-96d6-4965-bc33-03f96fa05387'})
            elif self.network.chain_id == 43113:
                payload['params'][0].update({'biconomyApiKey': 'mc7THlBmj.827b72e3-a50f-4d9b-b619-ca7d5680655b'})
            # TODO - Не все biconomyApiKey проверил
            
            maxFeePerGas, maxPriorityFeePerGas = await self.calculate_gas()

            if self.network.chain_id == 97:
                payload['params'][1][0].update({
                    'type': '0x0',
                    'gas': gas,
                    'gasPrice': maxFeePerGas
                })
            else:
                payload['params'][1][0].update({
                    'type': '0x2',
                    'maxFeePerGas': maxFeePerGas,
                    'maxPriorityFeePerGas': maxPriorityFeePerGas
                })

            response = await self.session.post(self.universal_api, json=payload, custom_headers=self.session.DEFAULT_HEADERS)
            answer = response.json()

            gas_USDG = int(answer['result']['particleCost'], 16)/1e18
 
            if gas_USDG > MAX_GAS_USDG:
                logger.info(f'Поток {self.thread} | Газ выше указанного, жду снижения | <i>Текущий газ: <r>{gas_USDG:.6f}</r> <e>$USDG</e>, Указанный: <g>{MAX_GAS_USDG}</g> <e>$USDG</e></i>')
                await asyncio.sleep(10)
            else:
                logger.info(f'Поток {self.thread} | Инициализирую транзакцию <y>Particle Withdraw...</y>')
                break
        
        balance_main = await self.get_balance(self.network.chain_id, self.account.address)

        userOps = answer['result']['userOps']

        timestamp = ParticleNetwork.get_unix_timestamp()
        valid_until = timestamp+600
        valid_after = timestamp-600

        params = {
            'chainId': str(self.network.chain_id),
            'projectUuid': '91bf10e7-5806-460d-95af-bef2a3122e12',
            'projectKey': 'cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76'
        }

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "particle_aa_createMultiChainUnsignedData",
            "params": [
                {
                    "name": "UNIVERSAL",
                    "version": "1.0.0",
                    "ownerAddress": self.account.address
                },
                {
                    "multiChainConfigs": [
                        {
                            "chainId": self.network.chain_id,
                            "userOpHash": userOps[0]['userOpHash'],
                            "validUntil": valid_until,
                            "validAfter": valid_after
                        },
                        {
                            "chainId": 2011,
                            "userOpHash": userOps[1]['userOpHash'],
                            "validUntil": valid_until,
                            "validAfter": valid_after
                        }
                    ]
                }
            ]
        }

        if self.network.chain_id == 97:
            payload['params'][0].update({'biconomyApiKey': 'u7F_1lHe5.f9c588e6-96d6-4965-bc33-03f96fa05387'})
        elif self.network.chain_id == 43113:
            payload['params'][0].update({'biconomyApiKey': 'mc7THlBmj.827b72e3-a50f-4d9b-b619-ca7d5680655b'})
        # TODO - Не все biconomyApiKey проверил

        response = await self.session.post(self.rpc_particle+'/evm-chain', params=params, json=payload, custom_headers=self.session.DEFAULT_HEADERS)
        answer = response.json()

        sign_tx_info = answer['result']

        signature = self.w3u.sign_message(hexstr=sign_tx_info['merkleRoot'])

        merkle_root = bytes.fromhex(sign_tx_info['merkleRoot'][2:])
        merkle_proof = [bytes.fromhex(sign_tx_info['data'][0]['merkleProof'][0][2:])]
        merkle_proof_2 = [bytes.fromhex(sign_tx_info['data'][1]['merkleProof'][0][2:])]
        r_signature = bytes.fromhex(signature[2:])

        first_signature = self.create_op_signature(
            valid_until = valid_until,
            valid_after = valid_after,
            merkle_root = merkle_root,
            merkle_proof = merkle_proof,
            r_signature = r_signature
        )

        second_signature = self.create_op_signature(
            valid_until = valid_until,
            valid_after = valid_after,
            merkle_root = merkle_root,
            merkle_proof = merkle_proof_2,
            r_signature = r_signature
        )
        
        captcha_code = await Captcha(self.thread, self.account.proxy).checkin()

        payload = {
            "jsonrpc": "2.0",
            "chainId": self.network.chain_id,
            "method": "universal_sendCrossChainUserOperation",
            "params": [[
                {"chainId": self.network.chain_id, "signature": ""},
                {"chainId": 2011, "signature": ""}
            ]],
            "cfTurnstileResponse": captcha_code
        }

        payload['params'][0][0].update(userOps[0]['userOp'])
        payload['params'][0][0]['signature'] = '0x' + first_signature

        payload['params'][0][1].update(userOps[1]['userOp'])
        payload['params'][0][1]['signature'] = '0x' + second_signature

        response = await self.session.post(self.universal_api, json=payload, custom_headers=self.session.DEFAULT_HEADERS)
        answer = response.json()

        _id = answer['result']['_id']

        while True:
            payload = {
                "jsonrpc": "2.0",
                "chainId": self.network.chain_id,
                "method": "universal_getCrossChainUserOperation",
                "params": [_id]
            }

            response = await self.session.post(self.universal_api, json=payload, custom_headers=self.session.DEFAULT_HEADERS)
            answer = response.json()

            if answer['result'].get('targetUserOpEvent') is None:
                await asyncio.sleep(3)
            else:
                txhash = answer['result']['targetUserOpEvent']['txHash']
                logger.success(f'Поток {self.thread} | Транзакция <g>Particle Withdraw</g> | <i>GasUsed: <g>{gas_USDG:.6f}</g> <e>$USDG</e></i> | <i>Value: <g>{amount:.6f}</g> <e>${self.network.token}</e></i> | <i>TxHash: <k>{txhash}</k></i>')
                break

        while True:
            new_balance_main = await self.get_balance(self.network.chain_id, self.account.address)
            if new_balance_main > balance_main:
                logger.success(f'Поток {self.thread} | <g>Particle Withdraw</g> подтвержден!')
                break
            else:
                logger.info(f'Поток {self.thread} | Жду подтверждение <y>Particle Withdraw...</y>')
                await asyncio.sleep(10)

        return txhash

    async def auto_transactions(self, count_tx: int):
        logger.info(f'Поток {self.thread} | Начинаю крутить транзакции')
        while count_tx != 0:
            shuffle = random.randint(1, 12)
            balance_main = await self.get_balance(self.network.chain_id, self.account.address)
            balance_particle = await self.get_balance(self.network.chain_id)
            balance_USDG = await self.get_balance(2011)

            transfer_amount = round(random.uniform(TRANSFER_AMOUNT[0], TRANSFER_AMOUNT[1]), 6)
            
            if balance_particle < transfer_amount or (shuffle == 1 and RANDOM_TX):
                topup_amount = round(random.uniform(DEPOSIT_PRATICLE[0], DEPOSIT_PRATICLE[1]), 6)
                if balance_main < transfer_amount:
                    logger.critical(f'Поток {self.thread} | <r>Баланс на основном EVM кошельке закончился, транзакции будут пропущены!</r> | <r>Баланс: {balance_main} ${self.network.token}</r>')
                await self.top_up_particle(topup_amount)
                random_sleep = random.randint(DELAY_TRANSACTIONS[0], DELAY_TRANSACTIONS[1])
                logger.info(f'Поток {self.thread} | Отдых между транзакциями, сплю {random_sleep} сек.')
                await asyncio.sleep(random_sleep)
                continue
                
            if balance_USDG < MAX_GAS_USDG or (shuffle == 12 and RANDOM_TX):
                deposit_amount = round(random.uniform(DEPOSIT_USDG[0], DEPOSIT_USDG[1]), 6)
                if balance_main < deposit_amount:
                    logger.critical(f'Поток {self.thread} | <r>Баланс на основном EVM кошельке закончился, транзакции будут пропущены!</r> | <r>Баланс: {balance_main} ${self.network.token}</r>')
                await self.deposit_usdg(deposit_amount)
                random_sleep = random.randint(DELAY_TRANSACTIONS[0], DELAY_TRANSACTIONS[1])
                logger.info(f'Поток {self.thread} | Отдых между транзакциями, сплю {random_sleep} сек.')
                await asyncio.sleep(random_sleep)
                continue

            await self.send_transaction(transfer_amount)
            count_tx -= 1
            random_sleep = random.randint(DELAY_TRANSACTIONS[0], DELAY_TRANSACTIONS[1])
            logger.info(f'Поток {self.thread} | Отдых между транзакциями, сплю {random_sleep} сек.')
            await asyncio.sleep(random_sleep)

            if count_tx != 0:
                logger.info(f'Поток {self.thread} | <i>Осталось транзакций: <u><k>{count_tx}</k>/<g>100</g></u></i>')
            else:
                logger.success(f'Поток {self.thread} | Успешно накрутил <g>100</g> транзакций!')
            logger.success(f'Поток {self.thread} | Задание выполнено <c>USE UNIVERSAL GAS TO TRANSACT</c> | <i>Points: <g>+50</g> <m>$PARTI</m></i>')

    async def get_all_balances(self) -> dict:
        logger.warning(f'Поток {self.thread} | Включен <y>GET_ALL_BALANCES</y> - <u>Может занимать длительное время</u>')
        chains = {
            'ethereum': AllNetwork.EthereumRPC,
            'arbitrum': AllNetwork.ArbitrumRPC,
            'optimism': AllNetwork.OptimismRPC,
            'base': AllNetwork.BaseRPC,
            'linea': AllNetwork.LineaRPC,
            'blast': AllNetwork.BlastRPC,
            'polygon': AllNetwork.PolygonRPC,
            'bnb': AllNetwork.BSC_RPC,
            'avalanche': AllNetwork.AvalancheRPC,
            'b2network': AllNetwork.B2networkRPC
        }

        balances = {}
        for name, network in chains.items():
            balances[f'{name}_main'] = await self.get_balance(network.chain_id, self.account.address)
            await asyncio.sleep(DELAY_ALL_BALANCES)
            balances[f'{name}_particle'] = await self.get_balance(network.chain_id, self.account.address_particle)
            await asyncio.sleep(DELAY_ALL_BALANCES)

        return balances

