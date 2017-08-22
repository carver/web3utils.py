
import datetime
import time


def stalecheck(web3, **kwargs):
    '''
    Use to require that a function will run only of the blockchain is recently updated.

    If the chain is old, raise a StaleBlockchain exception

    Define how stale the chain can be with keyword arguments from datetime.timedelta,
    like stalecheck(web3, days=2)

    Turn off the staleness check at runtime with:
    wrapped_func(..., assertfresh=False)
    '''
    allowable_delay = datetime.timedelta(**kwargs).total_seconds()

    def decorator(func):
        def wrapper(*args, assertfresh=True, **kwargs):
            if assertfresh:
                last_block = web3.eth.getBlock('latest')
                if not last_block or time.time() - last_block.timestamp > allowable_delay:
                    raise StaleBlockchain(last_block, allowable_delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class StaleBlockchain(Exception):
    def __init__(self, block, allowable_delay):
        last_block_date = datetime.datetime.fromtimestamp(block.timestamp).strftime('%c')
        super().__init__(
                "The latest block, #%d, is %d seconds old, but is only allowed to be %d s old. "
                "The date of the most recent block is %s. Continue syncing and try again..." %
                (block.number, time.time() - block.timestamp, allowable_delay, last_block_date)
                )
