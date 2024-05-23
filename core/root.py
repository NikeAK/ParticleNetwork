import platform
import asyncio
import traceback

from core.task_manager import TaskManager
from core.utils import logger
from core.cli import CLInterface

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Decor:
    @staticmethod
    def asyncstart(func):
        def wrapper(self, *args, **kwargs):
            try:
                asyncio.run(func(self, *args, **kwargs))
            except KeyboardInterrupt:
                logger.critical("Прервано пользователем!")
            except Exception as error:
                logger.critical(f"Непредвиденная ошибка: <r>{type(error).__name__}</r> - <r>{str(error)}</r>")
                logger.critical(f"Полный traceback ошибки:\n<r>{traceback.format_exc()}</r>")
        return wrapper
    

class Core:
    def __init__(self) -> None:
        self.__cli = CLInterface(self)
    
    def initialization(self):
        self.__cli.clear_console()
        self.__cli.show_main_logo()
        self.__cli.show_main_menu()
    
    @staticmethod
    async def setup_task(threads: int, task_type: str, *args):

        task_manager = TaskManager()

        tasks = []
        for thread in range(1, threads+1):
            task_func = getattr(task_manager, task_type)
            tasks.append(asyncio.create_task(task_func(thread, *args)))

        if task_type in ['launch']:
            logger.info(f'♻️  Сгенерировано <g>{threads}</g> потоков.\n')
        
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        first_completed_result = next(iter(done)).result()

        await asyncio.gather(*pending)

        messages = {
            'notwitter': "cписок твиттер-токенов закончился!",
            'noproxy': "cписок прокси закончился!",
            'nowallet': "cписок приватных ключей закончился!",
            'noaccount': "cписок аккаунтов БД отбработан :)",
        }

        for flag, message in messages.items():
            if flag in first_completed_result:
                print("")
                logger.info(f"Все потоки завершены, {message}")
                break
                
    @Decor.asyncstart
    def task_launch(self, threads: int, *args):
        return Core.setup_task(threads, 'launch', *args)
    
    @Decor.asyncstart
    def task_generate(self, threads: int, *args):
        return Core.setup_task(threads, 'generate_wallets', *args)

    @Decor.asyncstart
    def task_export(self, threads: int, *args):
        return Core.setup_task(threads, 'export_info', *args)

