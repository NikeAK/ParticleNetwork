import inquirer
from dataclasses import dataclass


@dataclass
class CLInterfaceModels:
    main_menu = [
        inquirer.List(
            name='menu_item',
            message='Main Menu',
            choices=[
                'Launch',
                'Export Info',
                'Generate Wallets',
                'Exit'
            ]
        )
    ]

    launch_storage_menu = [
        inquirer.List(
            name='menu_item',
            message='Where to launch from',
            choices=[
                'Launch DataBase',
                'Add account to database - TXT'
            ]
        )
    ]

    launch_database_menu = [
        inquirer.List(
            name='menu_item',
            message='Wallet selection',
            choices=[
                'All Wallets',
                'Select by filter wallets'
            ]
        )
    ]

    launch_filter_menu = [
        inquirer.Checkbox(
            name='menu_item',
            message='Filter selection <- ->, and press [ENTER]',
            choices=[
                'Check-in failed',
                'No 100 transactions'
            ]
        )
    ]

    export_format_menu = [
        inquirer.List(
            name='menu_item',
            message='Format selection',
            choices=[
                'TXT',
                'Excel'
            ]
        )
    ]

    export_data_menu = [
        inquirer.Checkbox(
            name='menu_item',
            message='Data selection <- ->, and press [ENTER]',
            choices=[
                'From config.py      - Ключи из config.py? (по умолчанию = да)',
                'id                  - Номер аккаунта в БД',
                'address             - Адрес кошелька Main',
                'private_key         - Приватный ключ',

                'twitter_token       - Твиттер auth_token',
                'proxy               - Прокси',

                'device_id           - Уникальный идентификатор аккаунта',

                'address_particle    - Адрес кошелька Particle',
                'invite_code         - Рефкод аккаунта',
                
                'refcode             - Используемый рефкод при регистрации',
                'referrer_address    - Адрес кошелька пригласителя',

                'check_in            - CheckIn',
                'today_tx            - Транзакций за 24 часа Particle',
                'total_tx            - Всего транзакций Particle',
                
                'referral_points     - Поинтов за рефов',
                'checkin_points      - Поинтов за CheckIn',
                'deposit_points      - Понитов за депозит',
                'transactions_points - Понитов за транзакции',
                'retweet_points      - Поинтов за ретвит',
                'total_points        - Всего поинтов',

                'ethereum_main       - Баланс Etherium Main',
                'arbitrum_main       - Баланс Arbitrum Main',
                'optimism_main       - Баланс Optimism Main',
                'base_main           - Баланс Base Main',
                'linea_main          - Баланс Linea Main',
                'blast_main          - Баланс Blast Main',
                'polygon_main        - Баланс Polygon Main',
                'bnb_main            - Баланс BNB Main',
                'avalanche_main      - Баланс Avalanche Main',
                'b2network_main      - Баланс B2Network Main',

                'ethereum_particle   - Баланс Etherium Particle',
                'arbitrum_particle   - Баланс Arbitrum Particle',
                'optimism_particle   - Баланс Optimism Particle',
                'base_particle       - Баланс Base Particle',
                'linea_particle      - Баланс Linea Particle',
                'blast_particle      - Баланс Blast Particle',
                'polygon_particle    - Баланс Polygon Particle',
                'bnb_particle        - Баланс BNB Particle',
                'avalanche_particle  - Баланс Avalanche Particle',
                'b2network_particle  - Баланс B2Network Particle',
            ],
            default=[
                'From config.py      - Ключи из config.py? (по умолчанию = да)'
            ]
        )
    ]

    enter_thread = [
        inquirer.Text(
            name='enter_item',
            message="👉 Введите кол-во потоков"
        )
    ]

    enter_count = [
        inquirer.Text(
            name='enter_item',
            message="👉 Введите кол-во аккаунтов"
        )
    ]

    main_logo = {
        'text': 'Particle',
        'font': 'slant',
        'colors': 'LIGHT_MAGENTA'
    }

    launch_logo = {
        'text': 'Launch',
        'font': 'standard',
        'colors': 'CYAN'
    }

    generate_logo = {
        'text': 'Generate',
        'font': 'standard',
        'colors': 'CYAN'
    }

    export_logo = {
        'text': 'Export Info',
        'font': 'standard',
        'colors': 'CYAN'
    }

# COLOR_CODES = {'BLACK': 30, 'RED': 31, 'GREEN': 32, 'YELLOW': 33, 'BLUE': 34, 'MAGENTA': 35, 'CYAN': 36, 'LIGHT_GRAY': 37,
#                'DEFAULT': 39, 'DARK_GRAY': 90, 'LIGHT_RED': 91, 'LIGHT_GREEN': 92, 'LIGHT_YELLOW': 93, 'LIGHT_BLUE': 94,
#                'LIGHT_MAGENTA': 95, 'LIGHT_CYAN': 96, 'WHITE': 97, 'RESET': 0
# }