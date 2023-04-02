from core.database.crud import CRUDBase
from core.database.models.server import Server, ServerCreate, ServerUpdate


class CRUDServer(CRUDBase[Server, ServerCreate, ServerUpdate]):
    pass


crud = CRUDServer(Server)
