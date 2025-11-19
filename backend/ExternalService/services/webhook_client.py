import httpx

__all__ = ["WebhookClient", "httpx"]


class WebhookClient:
    def __init__(self, http_client: httpx.AsyncClient | None = None):
        # тесты ожидают, что у экземпляра есть атрибут httpx
        self.httpx = httpx
        self.http_client = http_client or httpx.AsyncClient()

    async def send(self, url: str, payload: dict):
        try:
            response = await self.http_client.post(
                url,
                json=payload,
                timeout=5,
            )
            return True, response.status_code, response.text
        except Exception as e:
            return False, None, str(e)
