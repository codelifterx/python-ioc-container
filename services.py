from typing import Protocol, runtime_checkable
from ioc.decorators import injectable
from ioc.container import Lifetime, Disposable


@runtime_checkable
class ILogger(Protocol):
    def log(self, message: str) -> None: ...


@runtime_checkable
class IDatabase(Protocol):
    def connect(self) -> None: ...


@injectable(Lifetime.SINGLETON)
class ConsoleLogger:
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")


@injectable()
class Database(Disposable):
    def __init__(self):
        self.is_connected = False

    def connect(self):
        self.is_connected = True
        print("Connected to database")

    async def dispose(self):
        if self.is_connected:
            print("Closing database connection...")
            self.is_connected = False


@injectable()
class UserRepository:
    def __init__(self, db: IDatabase, logger: ILogger):
        self.db = db
        self.logger = logger

    def get_user(self, id: int):
        self.db.connect()
        self.logger.log(f"Fetching user {id}")
        return {"id": id, "name": "Test User"}


@injectable()
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_user(self, id: int):
        return self.user_repo.get_user(id)
