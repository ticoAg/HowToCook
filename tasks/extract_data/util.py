import asyncio
import time
from functools import wraps
from typing import Callable

from loguru import logger


def timer_decorator(func: Callable) -> Callable:
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Function {func.__name__} took {elapsed_time:.4f} seconds to execute.")
        return result

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Function {func.__name__} took {elapsed_time:.4f} seconds to execute.")
        return result

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def get_git_commit_hash() -> str:
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def get_git_commit_time() -> str:
    import subprocess

    try:
        # 获取提交时间
        time_result = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=iso"],
            capture_output=True,
            text=True,
            check=True,
        )
        return time_result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"
