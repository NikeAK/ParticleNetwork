from asyncio import Lock
from better_proxy import Proxy

from core.utils import Checker, FileManager, logger

from core.database.database import MainDB
from core.database.models import Accounts


class DataLoader:
    proxies_path    = 'data/proxy.txt'
    refcodes_path   = 'data/refcodes.txt'
    twitters_path   = 'data/twitter_tokens.txt'
    wallets_path    = 'data/wallets.txt'

    def __init__(self, lock: Lock) -> None:
        self.lock = lock
        self.__db = MainDB()

        self.proxies        = FileManager.read_file(self.proxies_path)
        self.refcodes       = FileManager.read_file(self.refcodes_path)
        self.twitter_tokens = FileManager.read_file(self.twitters_path)
        self.wallets        = FileManager.read_file(self.wallets_path)
        self.accounts       = self.__db.get_accounts()
        
        self.count_refcode  = 0

    async def get_proxy(self, thread: int, timeout: int | float = 5) -> str:
        while True:
            async with self.lock:
                if self.proxies:
                    proxy: str = self.proxies.pop(0)
                else:
                    return 'noproxy'
                
            format_proxy = Proxy.from_str(proxy if proxy.startswith('http://') else 'http://' + proxy).as_url

            if self.__db.get_account_by_key('proxy', format_proxy):
                logger.info(f'Поток {thread} | Уже присутсвует в БД! Пропущен - <u><i>Proxy: <r>{proxy}</r></i></u>')
                async with self.lock:
                    FileManager.delete_str_file(self.proxies_path, proxy)
                continue

            status, message = await Checker.proxy(
                proxy=format_proxy,
                ping_urls=[
                    'https://twitter.com/i/api/graphql',
                    'https://pioneer-api.particle.network/',
                    # 'https://universal-api.particle.network/',
                    # 'https://rpc.particle.network/evm-chain',
                ],
                timeout=timeout
            )

            if status:
                logger.info(f"Поток {thread} | Валидный <g>Proxy</g>: {message}")
                async with self.lock:
                    FileManager.delete_str_file(self.proxies_path, proxy)
                return format_proxy
            else:
                logger.error(f"Поток {thread} | Невалидный <r>Proxy</r>: {message}")
                async with self.lock:
                    FileManager.delete_str_file(self.proxies_path, proxy)
                continue

    async def get_refcode(self) -> str:
        async with self.lock:
            refcode = self.refcodes[self.count_refcode % len(self.refcodes)]
            self.count_refcode += 1
        return refcode

    async def get_twitter(self, thread: int, proxy: str | None = None) -> str:
       while True:
            async with self.lock:
                if self.twitter_tokens:
                    token: str = self.twitter_tokens.pop(0)
                else:
                    return 'notwitter'
                
            if self.__db.get_account_by_key('twitter_token', token):
                logger.info(f'Поток {thread} | Уже присутсвует в БД! Пропущен - <u><i>TwitterToken: <r>{token}</r></i></u>')
                async with self.lock:
                    FileManager.delete_str_file(self.twitters_path, token)
                continue

            status, message = await Checker.twitter_auth(
                auth_token=token,
                proxy=proxy
            )

            if status == False:
                logger.error(f'Поток {thread} | Невалидный <r>TwitterToken</r>: {message}')
                async with self.lock:
                    FileManager.delete_str_file(self.twitters_path, token)
                continue
            elif status is None:
                logger.warning(f'Поток {thread} | Ошибка <y>TwitterToken</y>: {message}')
                continue #TODO Возможен бесконечный цикл при плохих прокси
            else:
                logger.info(f'Поток {thread} | Валидный <g>TwitterToken</g>')
                async with self.lock:
                    FileManager.delete_str_file(self.twitters_path, token)
                return token

    async def get_wallet(self, thread: int) -> str:
        while True:
            async with self.lock:
                if self.wallets:
                    wallet: str = self.wallets.pop(0)
                else:
                    return 'nowallet'
                
            if self.__db.get_account_by_key('private_key', wallet):
                logger.info(f'Поток {thread} | Уже присутсвует в БД! Пропущен - <u><i>PrivateKey: <r>{wallet[:5]}***{wallet[61:]}</r></i></u>')
                async with self.lock:
                    FileManager.delete_str_file(self.wallets_path, wallet)
                continue
            else:
                async with self.lock:
                    FileManager.delete_str_file(self.wallets_path, wallet)
                return wallet
            
    async def get_account(self) -> Accounts:
        async with self.lock:
            if self.accounts:
                account: str = self.accounts.pop(0)
            else:
                return 'noaccount'
        return account

