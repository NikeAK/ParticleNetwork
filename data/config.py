#----------------------------------------------- Settings -----------------------------------------------
'''
Укажите цифру для выбора основной EVM сети "MAIN_NETWORK = ..."
1 - Ethereum     6 - Blast
2 - Arbitrum     7 - Polygon
3 - Optimism     8 - BSC
4 - Base         9 - Avalanche
5 - Linea        10 - B2network

MAIN_NETWORK        - Выберите основную сеть, указав число

DEPOSIT_USDG        - Укажите числа [min, max] для суммы депозита USDG в вашей сети.
                      Генерирует случайное число и округляет до 6 знаков после запятой.

DEPOSIT_PRATICLE    - Укажите числа [min, max] для суммы пополнения ParticleWallet в вашей сети.
                      Генерирует случайное число и округляет до 6 знаков после запятой.

MULTIPLIER_GAS      - Множитель газа для ускорения/экономии транзакций.

MAKE_TRANSACTIONS   - Накручивать 100 транзакций для выполнение ежедневного задания
                        USE UNIVERSAL GAS TO TRANSACT?

MAX_GAS_USDG        - Максимальный газ USDG для оплаты, у каждой сети сильно отличается.

TRANSFER_AMOUNT     - Укажите числа [min, max] для суммы перевода при накрутки транзакций.
                      Генерирует случайное число и округляет до 6 знаков после запятой.

DELAY_TRANSACTIONS  - Укажите числа [min, max] для выставления задержки между транзакциями.
                      Генерирует случайное число для задержки.

RANDOM_TX           - Также чтобы при накрутке транзакций не было отправки только с ParticleWallet, 
                      софт генерирует случайное число от 1 до 12. Если выпадет число 1, софт сделает 
                      долнительную транзакцию DEPOSIT_PRATICLE. Если выпадет число 12, софт сделает 
                      дополнительную транзакцию DEPOSIT_USDG. Отключить True/False

TIMEOUT_PROXY       - Максимальное время ожидания при проверке прокси в секундах

REQUEST_ATTEMPTS    - Количество попыток при не удачных запросах

Не забудьте что на вашем EVM кошельке должно быть достаточно тестовых токенов, рассчитывай коммисию и суммы перевода.
'''

MAIN_NETWORK = 8    

DEPOSIT_USDG = [0.0001, 0.0015]        
DEPOSIT_PRATICLE = [0.0001, 0.0025]      # Указывайте чуть больше чем TRANSFER_AMOUNT
MULTIPLIER_GAS = 1

MAKE_TRANSACTIONS = True
MAX_GAS_USDG = 0.5
TRANSFER_AMOUNT = [0.000001, 0.008]
DELAY_TRANSACTIONS = [10, 60]
RANDOM_TX = True

TIMEOUT_PROXY = 7
REQUEST_ATTEMPTS = 5

#-------------------------------------------- Captcha ApiKey --------------------------------------------

CAPMONSTER_API_KEY  = ''
RUCAPTCHA_API_KEY   = ''
ANTICAPTCHA_API_KEY = ''
TWOCAPTCHA_API_KEY  = ''

#------------------------------------------------ Export ------------------------------------------------

GET_ALL_BALANCES = True                 # Получать актуальный баланс всех EVM сетей? 
DELAY_ALL_BALANCES = 5                  # Задержка в секундах между получением баланса в 1 сети/1 кошелька

EXPORT_DATA = 'address, private_key, check_in, today_tx, total_tx, total_points'
EXPORT_SEPARATOR = ':'

'''
EXPORT_DATA         = Используемые данные для экспорта, записываются через запятую [test1, test2, ...]
EXPORT_SEPARATOR    = Символ разделения данных для экспорта в TXT

id                  - Уникальный номер аккаунта в БД

address             - Адрес кошелька Main
private_key         - Приватный ключ Main

twitter_token       - Твиттер auth_token
discord_token       - Дискорд auth_token
proxy               - Прокси

device_id           - Уникальный идентификатор аккаунта

address_particle    - Адрес кошелька Particle
invite_code         - Рефкод аккаунта

refcode             - Используемый рефкод при регистрации
referrer_address    - Адрес кошелька пригласителя

check_in            - CheckIn
today_tx            - Транзакций за 24 часа Particle
total_tx            - Всего транзакций Particle

referral_points     - Поинтов за рефов
checkin_points      - Поинтов за CheckIn
deposit_points      - Понитов за депозит
transactions_points - Понитов за транзакции
total_points        - Всего поинтов

ethereum_main       - Баланс Etherium  Main
arbitrum_main       - Баланс Arbitrum  Main
optimism_main       - Баланс Optimism  Main
base_main           - Баланс Base      Main
linea_main          - Баланс Linea     Main
blast_main          - Баланс Blast     Main
polygon_main        - Баланс Polygon   Main
bnb_main            - Баланс BNB       Main
avalanche_main      - Баланс Avalanche Main
b2network_main      - Баланс B2Network Main

ethereum_particle   - Баланс Etherium  Particle
arbitrum_particle   - Баланс Arbitrum  Particle
optimism_particle   - Баланс Optimism  Particle
base_particle       - Баланс Base      Particle
linea_particle      - Баланс Linea     Particle
blast_particle      - Баланс Blast     Particle
polygon_particle    - Баланс Polygon   Particle
bnb_particle        - Баланс BNB       Particle
avalanche_particle  - Баланс Avalanche Particle
b2network_particle  - Баланс B2Network Particle
'''

