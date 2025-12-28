import asyncio

stop_event = asyncio.Event()
exit_code: int = 0  # default 0