import asyncio
import warnings
import twitter

from curl_cffi.requests import AsyncSession #переделать
from twitter.errors import BadToken, BadRequest
from pydantic import ValidationError

warnings.filterwarnings("ignore", message="Curlm alread closed!", category=UserWarning)


class Checker:
    @staticmethod
    async def proxy(proxy: str, ping_urls: list['str'], timeout: int | float = 5) -> tuple[bool, str]:
        try:
            async with AsyncSession(proxy=proxy, timeout=timeout) as session:
                for url in ping_urls:
                    await session.get(url)
                    await asyncio.sleep(3)
                response = await session.get('https://api.ipify.org/?format=json')
                answer = response.json()
        except Exception as error:
            return False, str(error)
        else:
            return True, answer['ip']

    @staticmethod
    async def twitter_auth(auth_token: str, proxy: str | None = None) -> tuple[bool | None, str]:
        account = twitter.Account(auth_token=auth_token)
        try:
            async with twitter.Client(account=account, proxy=proxy) as client:
                # await client.login()  # Uncomment if login method exists in twitter.Client
                pass  # Placeholder for further implementation
        except (BadToken, ValidationError) as error:
            return False, str(error)
        except Exception as error:
            return None, str(error)
        else:
            return True, auth_token