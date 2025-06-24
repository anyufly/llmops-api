import asyncio
import concurrent.futures
import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple

from llmops_api.base.logger import logger


@dataclass(order=True)
class TaskDefinition:
    """任务定义（包含执行逻辑和回调）"""

    priority: int
    func: Callable = field(compare=False)
    args: Tuple = field(compare=False, default_factory=tuple)
    kwargs: Dict = field(compare=False, default_factory=dict)
    on_success: Optional[Callable] = field(compare=False, default=None)
    on_error: Optional[Callable] = field(compare=False, default=None)


class Task:
    """任务实例（包含执行状态和结果）"""

    __slots__ = ("task_id", "definition", "future", "timestamp")

    def __init__(
        self,
        definition: TaskDefinition,
        future: concurrent.futures.Future,
    ):
        self.task_id = uuid.uuid4().hex
        self.definition = definition
        self.future = future
        self.timestamp = time.time()


class PriorityTaskQueue:
    def __init__(self):
        self._queue = queue.PriorityQueue()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._stop_event = threading.Event()
        self._futures: Dict[str, concurrent.futures.Future] = {}
        self._worker_thread.start()
        self._logger = logger.bind(name="PriorityTaskQueue")

    def add_task(
        self,
        func: Callable,
        priority: int = 0,
        args: Tuple = (),
        kwargs: Optional[Dict] = None,
        on_success: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ) -> concurrent.futures.Future:
        """添加任务到队列，返回Future对象用于等待结果"""
        kwargs = kwargs or {}
        definition = TaskDefinition(
            priority=priority,
            func=func,
            args=args,
            kwargs=kwargs,
            on_success=on_success,
            on_error=on_error,
        )
        future = concurrent.futures.Future()
        task = Task(definition, future)
        self._futures[task.task_id] = future

        # 优先级 + 时间戳确保相同优先级的任务按添加顺序执行
        self._queue.put((priority, task.timestamp, task))
        return future

    def _worker(self):
        """工作线程循环处理任务"""
        while not self._stop_event.is_set():
            try:
                _, _, task = self._queue.get(timeout=1)
                if task.future.cancelled():
                    self._cleanup_task(task)
                    self._queue.task_done()
                    continue

                self._execute_task(task)
                self._cleanup_task(task)
                self._queue.task_done()
            except queue.Empty:
                continue

    def _execute_task(self, task: Task):
        """执行任务并处理结果/异常"""
        try:
            result = task.definition.func(*task.definition.args, **task.definition.kwargs)
            task.future.set_result(result)

            # 执行同步回调（如果存在）
            if task.definition.on_success is not None:
                try:
                    task.definition.on_success(result)
                except Exception as ex:
                    self._logger.opt(exception=ex).error("成功回调执行失败")
        except Exception as e:
            task.future.set_exception(e)

            # 执行错误回调（如果存在）
            if task.definition.on_error is not None:
                try:
                    task.definition.on_error(e)
                except Exception as ex:
                    self._logger.opt(exception=ex).error("错误回调执行失败")

    def _cleanup_task(self, task: Task):
        """清理任务资源"""
        if task.task_id in self._futures:
            del self._futures[task.task_id]

    async def add_task_async(
        self,
        func: Callable,
        priority: int = 0,
        args: Tuple = (),
        kwargs: Optional[Dict] = None,
    ) -> Any:
        """异步添加任务并等待结果（协程版本）

        注意：此方法不接收on_success/on_error回调，
        因为结果处理应在await之后直接进行

        Args:
            func: 可调用对象
            priority: 优先级数值（越小越优先）
            args: 位置参数
            kwargs: 关键字参数

        Returns:
            任务执行结果
        """
        # 创建同步future，不传递任何回调
        sync_future = self.add_task(
            func,
            priority,
            args,
            kwargs or {},
            None,  # 不传on_success
            None,  # 不传on_error
        )
        # 转换为异步future
        async_future = asyncio.wrap_future(sync_future)
        return await async_future

    def shutdown(self):
        """关闭任务队列"""
        self._stop_event.set()

        self._worker_thread.join(timeout=5.0)  # 等待工作线程结束

        # 清空队列并取消所有未执行的任务
        while not self._queue.empty():
            try:
                _, _, task = self._queue.get_nowait()
                if not task.future.done():
                    task.future.cancel()  # 安全取消未执行的任务
                self._cleanup_task(task)
                self._queue.task_done()  # 关键：平衡队列计数
            except queue.Empty:
                break
        # 强制取消任何可能剩余的任务（双重保障）
        for task_id, future in list(self._futures.items()):
            if not future.done():
                future.cancel()
            del self._futures[task_id]
