import asyncio
import warnings

from curl_cffi.requests import AsyncSession, BrowserType, Response, RequestsError
from .errors import RequestsAttempts 

from core.utils import logger
from data.config import REQUEST_ATTEMPTS

warnings.filterwarnings("ignore", message="Curlm alread closed!", category=UserWarning)


class BaseAsyncSession:
    DEFAULT_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "Origin": "https://pioneer.particle.network",
        "Referer": "https://pioneer.particle.network/",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    DEFAULT_IMPERSONATE = BrowserType.chrome124

    def __init__(
            self,
            thread: int,
            headers: dict | None = None,
            proxy: str  | None = None,
            **session_kwargs
        ):

        self.thread = thread

        self._session = AsyncSession(
            impersonate = self.DEFAULT_IMPERSONATE,
            headers = headers or self.DEFAULT_HEADERS,
            proxy = proxy,
            verify = False,
            **session_kwargs
        )

    @property
    def headers(self):
        return self._session.headers
    
    async def _request(
            self,
            method: str,
            url: str,
            params: dict | list | tuple | None = None,
            json: dict = None,
            custom_headers: dict | None = None,
            **request_kwargs
        ) -> Response:
        original_headers = self._session.headers

        if custom_headers is not None:
            self._session.headers = custom_headers
        
        for attempt in range(1, REQUEST_ATTEMPTS+1):
            try:
                response = await self._session.request(
                    method = method,
                    url = url,
                    params = params,
                    json = json,
                    **request_kwargs
                )
            except RequestsError as msg_error:
                logger.error(f'Поток {self.thread} | Попытка запроса [<y>{attempt}</y>/<r>{REQUEST_ATTEMPTS}</r>], сон 10 сек. - <r>RequestsError: {msg_error}</r>')
                await asyncio.sleep(10)
                continue
            else:
                self._session.headers = original_headers
                return response
        else:
            self._session.headers = original_headers
            raise RequestsAttempts('Попытки запросов исчерпаны')

    async def get(
            self,
            url: str,
            params: dict | list | tuple | None = None,
            custom_headers: dict | None = None,
            **request_kwargs
        ) -> Response:
        return await self._request(
            method = 'GET',
            url = url,
            params = params,
            custom_headers = custom_headers,
            **request_kwargs
        )

    async def post(
            self,
            url: str,
            params: dict | list | tuple | None = None,
            json: dict = None,
            custom_headers: dict | None = None,
            **request_kwargs
        ) -> Response:
        return await self._request(
            method = 'POST',
            url = url,
            params = params,
            json = json,
            custom_headers = custom_headers,
            **request_kwargs
        )

    async def head(
            self,
            url: str,
            params: dict | list | tuple | None = None,
            json: dict = None,
            custom_headers: dict | None = None,
            **request_kwargs
        ) -> Response:
        return await self._request(
            method = 'HEAD',
            url = url,
            params = params,
            json = json,
            custom_headers = custom_headers,
            **request_kwargs
        )

    async def put(
            self,
            url: str,
            params: dict | list | tuple | None = None,
            json: dict = None,
            custom_headers: dict | None = None,
            **request_kwargs
        ) -> Response:
        return await self._request(
            method = 'PUT',
            url = url,
            params = params,
            json = json,
            custom_headers = custom_headers,
            **request_kwargs
        )
    
    async def patch(
            self,
            url: str,
            params: dict | list | tuple | None = None,
            json: dict = None,
            custom_headers: dict | None = None,
            **request_kwargs
        ) -> Response:
        return await self._request(
            method = 'PATCH',
            url = url,
            params = params,
            json = json,
            custom_headers = custom_headers,
            **request_kwargs
        )
    
    async def delete(
            self,
            url: str,
            params: dict | list | tuple | None = None,
            json: dict = None,
            custom_headers: dict | None = None,
            **request_kwargs
        ) -> Response:
        return await self._request(
            method = 'DELETE',
            url = url,
            params = params,
            json = json,
            custom_headers = custom_headers,
            **request_kwargs
        )
    
    async def options(
            self,
            url: str,
            params: dict | list | tuple | None = None,
            json: dict = None,
            custom_headers: dict | None = None,
            **request_kwargs
        ) -> Response:
        return await self._request(
            method = 'OPTIONS',
            url = url,
            params = params,
            json = json,
            custom_headers = custom_headers,
            **request_kwargs
        )

