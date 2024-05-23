import random
import uuid
import asyncio
import pandas

from datetime import datetime, timezone
from web3 import Account as ethAccount
from tqdm import tqdm

from core.data_loader import DataLoader
from core.particle import ParticleNetwork
from core.utils import FileManager, logger

from core.database.database import MainDB
from core.database.models import Accounts

from data.config import MAIN_NETWORK, TIMEOUT_PROXY, DEPOSIT_USDG, MAKE_TRANSACTIONS, GET_ALL_BALANCES, EXPORT_DATA, EXPORT_SEPARATOR
from data.service import NETWORK_BYKEY


class TaskManager:
    def __init__(self, filter_: list | None) -> None:
        self.lock = asyncio.Lock()
        self.__db = MainDB()
        self.__dl = DataLoader(lock=self.lock)
        self.__network = NETWORK_BYKEY[MAIN_NETWORK]
        self._apply_filter(filter_)
            
    def _apply_filter(self, filter_: list | None) -> None:
        if filter_:
            self.__dl.accounts = self.__db.get_accounts_filtered(
                checkin=('Check-in failed' in filter_),
                todaytx=('No 100 transactions' in filter_)
            )

    async def launch(self, thread: int, storage: str) -> None:
        while True:
            if storage == 'Launch DataBase':
                account = await self.__dl.get_account()
                if account == 'noaccount':return account

                logger.info(f'Поток {thread} | Начал работу - <i>PrivateKey: <u><g>{account.private_key[:5]}***{account.private_key[61:]}</g></u></i>')
                self.__db.update_account(account.id, {'check_in': False})

                particle = ParticleNetwork(thread, account, self.__network)
                login_data = await particle.login()
            
                points_stats = await particle.check_earned_points()


                if not any(item['type'] == 3 for item in points_stats):
                    balance_main = await particle.get_balance(self.__network.chain_id, account.address)
                    deposit_amount = round(random.uniform(DEPOSIT_USDG[0], DEPOSIT_USDG[1]), 6)
                    if balance_main > deposit_amount:
                        await particle.deposit_usdg(deposit_amount)
                        logger.success(f'Поток {thread} | Задание <c>DEPOSIT UNIVERSAL GAS</c> выполнено! | <i>Points: <g>+200</g> <m>$PARTI</m></i>')
                    else:
                        logger.critical(f'Поток {thread} | <r>Баланс на основном EVM кошельке закончился, транзакции будут пропущены!</r> | <r>Баланс: {balance_main} ${self.__network.token}</r>')

                if not any(item['type'] == 5 for item in points_stats):
                    result = await particle.claim_retweet()
                    if result:
                        logger.success(f'Поток {thread} | Задание <c>RETWEET PARTICLE NETWORKS TWEET</c> выполнено! | <i>Points: <g>+1000</g> <m>$PARTI</m></i>')
                    else:
                        logger.error(f'Поток {thread} | Ошибка при выполнении задания <r>RETWEET PARTICLE NETWORKS TWEET</r>')
                    
                if not await particle.check_checkin():
                    await particle.claim_checkin()
                
                if MAKE_TRANSACTIONS:
                    transactions = await particle.get_transactions()
                    transaction_count_today = 0

                    timestamp = ParticleNetwork.get_unix_timestamp()

                    for trade in transactions:
                        trade_parsed_time = datetime.strptime(trade['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                        trade_time_utc = trade_parsed_time.replace(tzinfo=timezone.utc).timestamp()

                        if timestamp - trade_time_utc <= 86400:
                            transaction_count_today += 1
                    
                    transaction_count_make = 100 - transaction_count_today
                    if transaction_count_make > 0:
                        await particle.auto_transactions(transaction_count_make)
                
                logger.info(f'Поток {thread} | Собираю информацию/статистику аккаунта...')
                
                points_stats = await particle.check_earned_points(logl=True)
                user_info = await particle.get_user_info()

                referral_points, checkin_points, deposit_points, transactions_points, retweet_points = 0, 0, 0, 0, 0

                for item in points_stats:
                    if item['type'] == 1:
                        referral_points = int(item['point'])
                    elif item['type'] == 2:
                        checkin_points = int(item['point'])
                    elif item['type'] == 3:
                        deposit_points = int(item['point'])
                    elif item['type'] == 4:
                        transactions_points = int(item['point'])
                    elif item['type'] == 5:
                        retweet_points = int(item['point'])
                
                all_transactions = []
                transaction_count_today = 0

                page = 1
                while True:
                    transactions = await particle.get_transactions(page)
                    page += 1
                    if transactions:
                        all_transactions.extend(transactions)
                    else:
                        break

                timestamp = ParticleNetwork.get_unix_timestamp()

                for trade in all_transactions:
                    trade_parsed_time = datetime.strptime(trade['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    trade_time_utc = trade_parsed_time.replace(tzinfo=timezone.utc).timestamp()

                    if timestamp - trade_time_utc <= 86400:
                        transaction_count_today += 1

                balances = await particle.get_all_balances() if GET_ALL_BALANCES else {}

                data_update = {
                    'invite_code': user_info['invitationCode'],
                    'referrer_address': user_info['referrerAddress'],
                    
                    'check_in': True,
                    'today_tx': transaction_count_today,
                    'total_tx': len(all_transactions),
                    
                    'referral_points': referral_points,
                    'checkin_points': checkin_points,
                    'deposit_points': deposit_points,
                    'transactions_points': transactions_points,
                    'retweet_points': retweet_points,
                    'total_points': user_info['totalPoint'],
                    **balances
                }
                self.__db.update_account(account.id, data_update)
                logger.success(f'Поток {thread} | Информация и статистика аккаунта в базе данных обновлена!')
                logger.success(f'Поток {thread} | Завершил работу - <u><i>PrivateKey: <g>{account.private_key[:5]}***{account.private_key[61:]}</g></i></u>')
            else:
                wallet = await self.__dl.get_wallet(thread)
                if wallet == 'nowallet':return wallet

                logger.info(f'Поток {thread} | Начал работу - <u><i>PrivateKey: <g>{wallet[:5]}***{wallet[61:]}</g></i></u>')

                proxy = await self.__dl.get_proxy(thread, TIMEOUT_PROXY)
                if proxy == 'noproxy':return proxy
                
                account = Accounts(
                    address=ethAccount.from_key(wallet).address,
                    private_key=wallet,
                    twitter_token='This account has already been registered',
                    proxy=proxy,
                    device_id=str(uuid.uuid4()),
                    refcode='This account has already been registered'
                )

                particle = ParticleNetwork(thread, account, self.__network)
                login_data = await particle.login()

                account.address_particle = login_data['aaAddress']

                if login_data['referrerAddress'] is None:
                    account.refcode = await self.__dl.get_refcode()
                    await particle.enter_refcode()
                else:
                     logger.info(f'Поток {thread} | К аккаунту уже привязан <c>RefCode</c>!')
                
                if login_data['twitterId'] is None:
                    twitter = await self.__dl.get_twitter(thread, proxy)
                    if twitter == 'notwitter':return twitter
                    account.twitter_token = twitter
                    await particle.bind_twitter(twitter)
                else:
                    logger.info(f'Поток {thread} | К аккаунту уже привязан <c>Twitter</c>!')

                self.__db.add_account(account)
                logger.info(f'Поток {thread} | Добавил аккаунт в БД - <u><i>PrivateKey: <g>{wallet[:5]}***{wallet[61:]}</g></i></u>')
    
    async def generate_wallets(self, thread: int, number: int) -> None:
        all_wallets = ''
        with tqdm(
            total=number,
            colour='green',
            unit=' wallets',
        ) as pbar:
            for _ in range(number):
                acct = ethAccount.create()
                all_wallets += acct.key.hex() +'\n'
                pbar.update(1)
                
        FileManager.save_data('data/generate/wallets.txt', all_wallets)
        print("")
        logger.success(f"Успешно сгенерировано <g>{number}</g> кошельков, сохранил по пути -> <c>data/generate/wallets.txt</c>")
        return ''
    
    async def export_info(self, thread: int, keys: list, format_: str):
        accounts = self.__dl.accounts
        export_list = EXPORT_DATA.replace(" ","").split(",") if keys[0] == 'From config.py' else keys

        if format_ == 'TXT':
            data = ''
            for account in accounts:
                for export in export_list:
                    if export == 'check_in':
                        data += ('✅' if getattr(account, export) else '❌') + EXPORT_SEPARATOR
                    else:
                        data += str(getattr(account, export)) + EXPORT_SEPARATOR
                data = data[:-len(EXPORT_SEPARATOR)] + '\n'
                logger.info(f"Аккаунт <g>{account.private_key}</g> экспортирован!")
            FileManager.save_data('data/export/wallets.txt', data)
            logger.success(f"Успешно экспортировано <g>{len(accounts)}</g> кошельков, сохранил по пути -> <c>data/export/wallets.txt</c>")
        else:
            df = pandas.DataFrame(columns=[export.capitalize() for export in export_list])
            for account in accounts:
                row_data = []
                for export in export_list:
                    if export == 'check_in':
                        row_data.append('✅' if getattr(account, export) else '❌')
                    else:
                        row_data.append(str(getattr(account, export)))
                df.loc[len(df)] = row_data
                logger.info(f"Аккаунт <g>{account.private_key}</g> экспортирован!")
            excel_file_path = 'data/export/wallets.xlsx'
            df.to_excel(excel_file_path, index=False) 
            logger.success(f"Успешно экспортировано <g>{len(accounts)}</g> кошельков, сохранил по пути -> <c>data/export/wallets.xlsx</c>")
        return ''

