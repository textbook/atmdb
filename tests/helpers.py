import asyncio
import json


def future_from(result):
    future = asyncio.Future()
    future.set_result(result)
    return future


class SimpleSessionMock:

    call_args_list = []

    # mocking

    @classmethod
    def configure_mock(cls, *, side_effect=None):
        cls.side_effect = side_effect
        cls.call_args_list = []

    @classmethod
    def assert_called_with(cls, url, *, headers=None):
        return dict(url=url, headers=headers) in cls.call_args_list

    # asyncio.ClientSession

    def __init__(self, **kwargs):
        if kwargs:
            raise ValueError('configuration not implemented')

    def get(self, url, *, headers=None, **kwargs):
        if kwargs:
            raise ValueError('configuration not implemented')
        if not self.side_effect:
            raise ValueError('unexpected GET call with %r', (url, headers))
        data = self.side_effect.pop(0)
        self._code = data.get('code')
        self._body = data.get('body')
        self._headers = data.get('headers')
        SimpleSessionMock.call_args_list.append(dict(url=url, headers=headers))
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    # response context

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass

    async def read(self):
        return json.dumps(self._body).encode('utf-8')

    @property
    def headers(self):
        return self._headers

    @property
    def status(self):
        return self._code
