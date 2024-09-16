import requests
from collections import defaultdict
from datetime import datetime, timezone
from web3 import Web3
from utils import print_balances, print_token_info, print_top_addresses, print_top_addresses_without_time
import time
import logging
import concurrent.futures
from requests.exceptions import RequestException
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.ERROR)

# Получение конфиденциальных данных из переменных окружения
polygon_rpc_url = os.getenv("POLYGON_RPC_URL")
token_address = os.getenv("TOKEN_ADDRESS")
api_key = os.getenv("POLYGONSCAN_API_KEY")

# Проверка наличия переменных окружения
if not polygon_rpc_url or not token_address or not api_key:
    raise EnvironmentError("Missing necessary environment variables")

# Инициализация подключения к сети Polygon
web3 = Web3(Web3.HTTPProvider(polygon_rpc_url))
if not web3.is_connected():
    logging.error("Connection to Polygon network failed")
    raise ConnectionError("Failed to connect to the Polygon network")

# Стандартный ABI для контракта токена ERC20
erc20_abi = '''
[{
    "constant": true,
    "inputs": [],
    "name": "decimals",
    "outputs": [{"name": "", "type": "uint8"}],
    "type": "function"
}, {
    "constant": true,
    "inputs": [{"name": "_owner", "type": "address"}],
    "name": "balanceOf",
    "outputs": [{"name": "balance", "type": "uint256"}],
    "type": "function"
}, {
    "constant": true,
    "inputs": [],
    "name": "symbol",
    "outputs": [{"name": "", "type": "string"}],
    "type": "function"
}]
'''

# Инициализация контракта токена
try:
    token_contract = web3.eth.contract(
        address=Web3.to_checksum_address(token_address), abi=erc20_abi)
except Exception as e:
    logging.error(f"Failed to initialize token contract: {e}")
    raise


def get_token_balance(address):
    # Получение баланса токена для данного адреса
    try:
        balance = token_contract.functions.balanceOf(
            Web3.to_checksum_address(address)).call()
        decimals = token_contract.functions.decimals().call()
        symbol = token_contract.functions.symbol().call()
        readable_balance = balance / (10 ** decimals)
        return readable_balance, symbol
    except Exception as e:
        logging.error(f"Error fetching balance for address {address}: {e}")
        return None, None


def get_multi_token_balances(addresses):
    # Получение балансов токенов для нескольких адресов (с использованием параллелизации)
    balances = []

    # Использование многопоточности для ускорения процесса
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_address = {executor.submit(
            get_token_balance, address): address for address in addresses}
        for future in concurrent.futures.as_completed(future_to_address):
            address = future_to_address[future]
            try:
                balance, symbol = future.result()
                balances.append((address, balance, symbol))
            except Exception as e:
                logging.error(
                    f"Error fetching balance for address {address}: {e}")

    return balances


def get_all_token_transactions(token_address):
    # Получение всех транзакций для указанного токена
    transactions = []
    page = 1
    offset = 10000

    while True:
        try:
            params = {
                "module": "account",
                "action": "tokentx",
                "contractaddress": token_address,
                "page": page,
                "offset": offset,
                "sort": "asc",
                "apikey": api_key
            }
            response = requests.get(
                "https://api.polygonscan.com/api", params=params)
            data = response.json()

            if data['status'] != '1' or not data['result']:
                break

            transactions.extend(data['result'])

            if len(data['result']) < offset:
                break

            page += 1
            # Задержка между запросами для предотвращения блокировки API
            time.sleep(1)

        except RequestException as e:
            logging.error(f"Error fetching transactions: {e}")
            break

    return transactions


def get_top_addresses_with_time_info(transactions, top_n=10):
    # Получение топ-адресов с балансами и временем последней транзакции
    balances = defaultdict(int)
    last_tx_time = {}

    for tx in transactions:
        from_addr = tx['from'].lower()
        to_addr = tx['to'].lower()
        value = int(tx['value'])
        time_stamp = int(tx['timeStamp'])

        balances[from_addr] -= value
        balances[to_addr] += value

        last_tx_time[from_addr] = max(
            time_stamp, last_tx_time.get(from_addr, 0))
        last_tx_time[to_addr] = max(time_stamp, last_tx_time.get(to_addr, 0))

    balance_list = [(addr, balance, last_tx_time[addr])
                    for addr, balance in balances.items()]
    balance_list.sort(key=lambda x: x[1], reverse=True)

    top_addresses = []
    for addr, balance, timestamp in balance_list[:top_n]:
        last_tx_date = datetime.fromtimestamp(
            timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        top_addresses.append((addr, balance, last_tx_date))

    return top_addresses


def get_top_addresses(transactions, top_n=10):
    # Получение топ-адресов с наибольшими балансами
    balances = defaultdict(int)

    for tx in transactions:
        from_addr = tx['from'].lower()
        to_addr = tx['to'].lower()
        value = int(tx['value'])

        balances[from_addr] -= value
        balances[to_addr] += value

    balance_list = [(addr, balance) for addr, balance in balances.items()]
    balance_list.sort(key=lambda x: x[1], reverse=True)

    return balance_list[:top_n]


def get_token_info(token_address):
    # Получение базовой информации о токене
    erc20_abi = '''
    [
        {"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"type":"function"},
        {"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
        {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
        {"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"}
    ]
    '''
    token_address = Web3.to_checksum_address(token_address)
    token_contract = web3.eth.contract(address=token_address, abi=erc20_abi)

    try:
        name = token_contract.functions.name().call()
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()
        total_supply = token_contract.functions.totalSupply().call() / (10 ** decimals)
        return {
            "symbol": symbol,
            "name": name,
            "totalSupply": total_supply
        }
    except Exception as e:
        logging.error(f"Error fetching token info: {e}")
        return None


if __name__ == "__main__":
    addresses = [
        "0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d",
        "0x4830AF4aB9cd9E381602aE50f71AE481a7727f7C"
    ]
    print(get_token_balance('0x51f1774249Fc2B0C2603542Ac6184Ae1d048351d'))
    balances = get_multi_token_balances(addresses)
    print_balances(balances)
    transactions = get_all_token_transactions(token_address)
    print(f"Total transactions: {len(transactions)}")

    top_addresses_with_time = get_top_addresses_with_time_info(transactions)
    print_top_addresses(top_addresses_with_time)

    top_addresses = get_top_addresses(transactions, top_n=10)
    print_top_addresses_without_time(top_addresses)

    token_info = get_token_info(token_address)
    print_token_info(token_info)
