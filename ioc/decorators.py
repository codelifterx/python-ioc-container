def injectable(lifetime: str = "singleton"):
    """服务注册装饰器"""
    def decorator(cls):
        setattr(cls, "__injectable__", True)
        setattr(cls, "__lifetime__", lifetime)
        return cls
    return decorator