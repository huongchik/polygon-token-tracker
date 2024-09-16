import pandas as pd


def print_balances(balances):
    df = pd.DataFrame(balances, columns=["Address", "Balance", "Symbol"])
    print(df)


def print_top_addresses(top_addresses):
    df = pd.DataFrame(top_addresses, columns=[
                      "Address", "Balance", "Last Transaction"])
    print(df)


def print_token_info(token_info):
    if token_info is None:
        print("No token information available.")
        return
    df = pd.DataFrame([token_info], columns=[
                      "symbol", "name", "totalSupply"])
    print(df)


def print_top_addresses_without_time(top_addresses):
    df = pd.DataFrame(top_addresses, columns=["Address", "Balance"])
    print(df)
