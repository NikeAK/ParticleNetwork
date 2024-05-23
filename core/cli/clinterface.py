import os
import inquirer
import pyfiglet

from core.utils import logger
from .models import CLInterfaceModels

from core.utils import FileManager

from core.database.database import MainDB
from core.database.models import Accounts

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.root import Core


class Helper:
    @staticmethod
    def proceed(func):
        def wrapper(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
            except KeyboardInterrupt:
                print("")
                logger.critical("Прервано пользователем")
            finally:
                input("\nНажмите [ENTER], чтобы продолжить...")
                CLInterface.clear_console()
                CLInterface.show_main_logo()
                self.show_main_menu()
        return wrapper


class CLInterface:
    def __init__(self, core: 'Core') -> None:
        self.__core = core

    @staticmethod
    def __show_logo__(model: CLInterfaceModels):
        return pyfiglet.print_figlet(**model)
    
    @staticmethod
    def __promt__(model: CLInterfaceModels):
        return inquirer.prompt(model, raise_keyboard_interrupt=True)[model[0].name]
    
    @staticmethod
    def clear_console():
        return os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def show_main_logo():
        CLInterface.__show_logo__(CLInterfaceModels.main_logo)
        print("| 👦 Software Author: IKEK2K \n| ✈️  Telegram: https://t.me/oxcode1")

    def show_main_menu(self):
        answer = CLInterface.__promt__(CLInterfaceModels.main_menu).lower().replace(' ', '_')
        CLInterface.clear_console()

        return getattr(
            self,
            f'_selected_{answer}_'
        )()
    
    @Helper.proceed
    def _selected_launch_(self):
        CLInterface.__show_logo__(CLInterfaceModels.launch_logo)

        storage, filter_ = CLInterface.__promt__(CLInterfaceModels.launch_storage_menu), None
        CLInterface.clear_console()

        if storage == 'Launch DataBase':
            CLInterface.__show_logo__(CLInterfaceModels.launch_logo)

            answer = CLInterface.__promt__(CLInterfaceModels.launch_database_menu)
            CLInterface.clear_console()

            if answer == 'Select by filter wallets':
                CLInterface.__show_logo__(CLInterfaceModels.launch_logo)

                filter_ = CLInterface.__promt__(CLInterfaceModels.launch_filter_menu)
                CLInterface.clear_console()

                wallets = MainDB().get_accounts_filtered(
                    checkin=(
                        True if 'Check-in failed' in filter_  else False
                    ),
                    todaytx=(
                        True if 'No 100 transactions' in filter_ else False
                    )
                )
            else:
                wallets = MainDB().get_accounts()
        else:
            wallets = FileManager.read_file('data/wallets.txt')
    
        CLInterface.__show_logo__(CLInterfaceModels.launch_logo)

        if not wallets:
            logger.error(f'Не найдено кошельков!')
            return
        
        logger.info(f'📥  Загружено кошельков - <g>{len(wallets)}</g>\n')

        while True:
            try:
                threads = int(CLInterface.__promt__(CLInterfaceModels.enter_thread))
                if threads > 0:
                    break
                else:
                    logger.warning("❌  Пожалуйста введите положительное число.\n")
            except ValueError:
                logger.warning("❌  Пожалуйста введите цифру.\n")

        CLInterface.clear_console()
        CLInterface.__show_logo__(CLInterfaceModels.launch_logo)

        return self.__core.task_launch(threads, storage, filter_=filter_)
    
    @Helper.proceed
    def _selected_generate_wallets_(self):
        CLInterface.__show_logo__(CLInterfaceModels.generate_logo)

        while True:
            try:
                number = int(CLInterface.__promt__(CLInterfaceModels.enter_count))
                if number > 0:
                    break
                else:
                    logger.warning("❌  Пожалуйста введите положительное число.\n")
            except ValueError:
                logger.warning("❌  Пожалуйста введите цифру.\n")
        
        CLInterface.clear_console()
        CLInterface.__show_logo__(CLInterfaceModels.generate_logo)

        return self.__core.task_generate(1, number)

    @Helper.proceed
    def _selected_export_info_(self):
        CLInterface.__show_logo__(CLInterfaceModels.export_logo)

        dirty_keys = CLInterface.__promt__(CLInterfaceModels.export_data_menu)
        keys = [key.split('-')[0].strip() for key in dirty_keys]

        CLInterface.clear_console()
        CLInterface.__show_logo__(CLInterfaceModels.export_logo)

        format_ = CLInterface.__promt__(CLInterfaceModels.export_format_menu)

        CLInterface.clear_console()
        CLInterface.__show_logo__(CLInterfaceModels.export_logo)

        return self.__core.task_export(1, keys, format_)

    def _selected_exit_(self):
        return exit()

