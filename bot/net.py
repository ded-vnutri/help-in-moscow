import aiohttp
from aiohttp_socks import ProxyConnector


def make_session(proxy_url: str | None, **kwargs) -> aiohttp.ClientSession:
    """aiohttp session that goes through PROXY_URL (http or socks5) when it is set."""
    if proxy_url:
        kwargs["connector"] = ProxyConnector.from_url(proxy_url)
    return aiohttp.ClientSession(**kwargs)
