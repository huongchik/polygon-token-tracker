from flask import Flask, request, jsonify
from token_analysis import get_multi_token_balances, get_all_token_transactions, get_top_addresses_with_time_info, get_token_info, get_token_balance

app = Flask(__name__)


@app.route('/get_balance', methods=['GET'])
def get_balance_route():
    address = request.args.get('address')
    if not address:
        return jsonify({"error": "Параметр 'address' отсутствует"}), 400

    try:
        balance, symbol = get_token_balance(address)
        if balance is None:
            return jsonify({"error": "Не удалось получить баланс"}), 500

        return jsonify({"address": address, "balance": balance, "symbol": symbol})
    except Exception as e:
        print(f"Ошибка при обработке запроса для адреса {address}: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@app.route('/get_balance_batch', methods=['POST'])
def get_balance_batch_route():
    data = request.get_json()
    addresses = data.get('addresses')

    if not addresses or not isinstance(addresses, list):
        return jsonify({"error": "Список 'addresses' отсутствует или некорректен"}), 400
    balances = get_multi_token_balances(addresses)

    if not balances:
        return jsonify({"error": "Не удалось получить балансы"}), 500

    response = [{"address": addr, "balance": balance, "symbol": symbol}
                for addr, balance, symbol in balances]

    return jsonify(response)


@app.route('/get_top_with_transactions', methods=['GET'])
def get_top_with_transactions_route():
    n = request.args.get('N')
    token_address = request.args.get('token_address')

    if not n or not n.isdigit():

        return jsonify({"error": "Параметр 'N' отсутствует или некорректен"}), 400

    if not token_address:
        return jsonify({"error": "Параметр 'token_address' отсутствует"}), 400

    n = int(n)

    transactions = get_all_token_transactions(token_address)
    top_addresses = get_top_addresses_with_time_info(transactions, top_n=n)
    if not top_addresses:
        return jsonify({"error": "Не удалось получить топ адресов"}), 500

    response = [{"address": addr, "balance": balance, "last_transaction": last_tx}
                for addr, balance, last_tx in top_addresses]

    return jsonify(response)


@app.route('/get_token_info', methods=['GET'])
def get_token_info_route():
    token_addr = request.args.get('token_address')

    if not token_addr:
        return jsonify({"error": "Параметр 'token_address' отсутствует"}), 400

    info = get_token_info(token_addr)

    if not info:
        return jsonify({"error": "Не удалось получить информацию о токене"}), 500

    return jsonify(info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
