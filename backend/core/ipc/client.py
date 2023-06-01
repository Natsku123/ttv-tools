from nextcord.ext.ipc import Client as OriginalClient


class Client(OriginalClient):

    async def __aenter__(self):
        await self.init_sock()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def close(self):
        await self.session.close()
