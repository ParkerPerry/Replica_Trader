# import ccxt
from config import replica_config, account_config
import ccxt.pro as ccxtpro
from asyncio import run


async def place_order(replica, account, order):
    try:
        balance = await replica.fetch_balance()
        replica_balance = balance['USD']['free']

        balance = await account.fetch_balance()
        account_balance = balance['USD']['free']

        factor = replica_balance / account_balance
        amount = order['amount'] / factor

        await account.load_markets()
        market = account.market(order['symbol'])

        if amount < market['limits']['amount']['min']:
            amount = market['limits']['amount']['min']

        positions = await replica.fetch_positions()
        replica_position = next((x for x in positions if x['symbol'] == order['symbol'] and x['contracts'] > 0), None)
        positions = await account.fetch_positions()
        account_position = next((x for x in positions if x['symbol'] == order['symbol'] and x['contracts'] > 0), None)

        if replica_position is None and account_position is not None:
            amount = account_position['contracts']
        elif replica_position is None and account_position is None:
            return

        await account.create_order(order['symbol'], order['type'], order['side'], amount, ...)
    except Exception as e:
        print(e)


async def watch_orders(replica, account):
    while True:
        try:
            orders = await replica.watch_orders()
            for order in orders:
                await place_order(replica, account, order)
        except Exception as e:
            print(e)
            break


replica = ccxtpro.ftx({
    'apiKey': replica_config['apiKey'],
    'secret': replica_config['secret'],
    'headers': {
        'FTX-SUBACCOUNT': replica_config['subaccount']
    }
})
account = ccxtpro.ftx({
    'apiKey': account_config['apiKey'],
    'secret': account_config['secret'],
    'headers': {
        'FTX-SUBACCOUNT': account_config['subaccount']
    }
})

run(watch_orders(replica, account))
