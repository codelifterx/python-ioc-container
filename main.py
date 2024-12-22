from ioc.container import Container
from services import ILogger, IDatabase, ConsoleLogger, Database, UserService


async def main():
    container = Container()

    # 自动注册所有带@injectable的服务
    import services
    container.auto_register(services)

    # 使用Protocol类型注册
    container.register(ILogger, ConsoleLogger)
    container.register(IDatabase, Database)

    # 获取服务并使用
    async with container.scoped() as ioc:
        user_service = ioc.resolve(UserService)
        user = user_service.get_user(1)
        print(user)  # {'id': 1, 'name': 'Test User'}

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
