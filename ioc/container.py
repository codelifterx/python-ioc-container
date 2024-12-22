from typing import TypeVar, Type, Any, Protocol, runtime_checkable
from dataclasses import dataclass
from contextlib import asynccontextmanager
import inspect

T = TypeVar('T')


class Lifetime:
    SINGLETON = "singleton"
    TRANSIENT = "transient"


@runtime_checkable
class Disposable(Protocol):
    """可释放资源的协议"""

    def dispose(self) -> None: ...


@dataclass
class ServiceInfo:
    """服务信息数据类"""
    implementation: Type[Any]
    lifetime: str


class Container:
    def __init__(self):
        self._services: dict[str, ServiceInfo] = {}
        self._instances: dict[str, Any] = {}
        self._disposables: set[Disposable] = set()

    def register(self, service_type: Type, implementation: Type, lifetime: str = Lifetime.SINGLETON) -> None:
        """注册服务"""
        self._services[service_type.__name__] = ServiceInfo(
            implementation, lifetime)

    def resolve(self, service_type: type[T]) -> T:
        """解析服务"""
        key = service_type.__name__

        if key not in self._services:
            raise Exception(f"Service {key} not registered")

        service_info = self._services[key]

        if service_info.lifetime == Lifetime.SINGLETON and key in self._instances:
            return self._instances[key]

        instance = self._create_instance(service_info.implementation)

        if service_info.lifetime == Lifetime.SINGLETON:
            self._instances[key] = instance

        return instance

    def _create_instance(self, implementation: Type) -> Any:
        """创建服务实例"""
        constructor = implementation.__init__
        if constructor == object.__init__:
            instance = implementation()
        else:
            params = inspect.signature(constructor).parameters
            args = {}
            for name, param in params.items():
                if name == 'self':
                    continue
                param_type = param.annotation
                if param_type is inspect.Parameter.empty:
                    raise Exception(
                        f"Parameter {name} missing type annotation")
                args[name] = self.resolve(param_type)
            instance = implementation(**args)

        if isinstance(instance, Disposable):
            self._disposables.add(instance)

        return instance

    @asynccontextmanager
    async def scoped(self):
        """使用上下文管理器管理容器生命周期"""
        try:
            yield self
        finally:
            await self.dispose()

    async def dispose(self):
        """释放所有资源"""
        for disposable in self._disposables:
            await disposable.dispose()
        self._disposables.clear()
        self._instances.clear()

    def auto_register(self, module):
        """自动注册模块中所有带@injectable的服务"""
        for name, obj in module.__dict__.items():
            if hasattr(obj, "__injectable__"):
                lifetime = getattr(obj, "__lifetime__", Lifetime.SINGLETON)
                self.register(obj, obj, lifetime)
