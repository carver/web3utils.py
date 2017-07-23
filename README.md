
# web3utils.py - Some sugar on top of web3.py

web3utils is a very thin layer over [web3.py](https://github.com/pipermerriam/web3.py) --
these are the main features:

* immediate access to a `web3` and `eth` object if you have a standard setup
* shorter way to call contract functions
* encode all contract string arguments as utf-8
* autoset encoding of input value to `web3.sha3(value)`, if `type(value) == bytes`
* return `None` from a contract call, in place of '0x0000000...'

This handful of changes made for quicker shell usage and coding for me. I hope it does for you, too!

I have also contributed a bit to web3.py, and intend to push these pieces upstream, if they want it.

This is a Python3-only library. It turns out that the distinction between strings and bytes is
pretty important. If you want to write code for the future (Ethereum), don't use a language from the
past.

### Setup

To use in your code, simply: `pip install web3utils`


If you want to contribute:

```
git clone git@github.com/carver/web3utils.py.git
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

### Usage

#### Instant access to web3 and eth

Print your primary account balance, denominated in ether:

```
from web3utils import web3, eth

wei = eth.getBalance(eth.accounts[0])
balance = web3.fromWei(wei, 'ether')

print(balance)
```

#### Succinct contract access

Several important changes:
 * quicker method calls like `contract.owner()` instead of `contract.call().owner()`
 * encode all method argument strings as utf-8
 * instead of returning `"0x000..."` on empty results, return `None`

Short contract calls will be assumed to be read-only (equivalent to `.call()` in web3.py),
unless it is modified first.

Note that this will *not* prevent you from calling a method that tries to alter state.
That state change will just never be sent to the rest of the network as a transaction.

You can switch back to a transaction like so:

```
contract.withdraw(amount, transact={'from': eth.accounts[1], 'gas': 100000, ...})
```

Which is equivalent to this web3.py approach:


```
contract.transact({'from': eth.accounts[1], 'gas': 100000, ...}).withdraw(amount)
```

### Wishlist

Filters can timeout and cause the following exception.

Instead, catch the exception in web3.py and notify watchers with an error
  (or even better, recreate the filter and pick up events where you left off)

```
Exception in thread Thread-22:8957
Traceback (most recent call last):
  File "/usr/lib/python2.7/threading.py", line 801, in __bootstrap_inner
    self.run()
  File "/usr/lib/python2.7/threading.py", line 754, in run
    self.__target(*self.__args, **self.__kwargs)
  File "/home/carver/filter_listener/venv/local/lib/python2.7/site-packages/web3/utils/filters.py", line 84, in _run
    changes = self.web3.eth.getFilterChanges(self.filter_id)
  File "/home/carver/filter_listener/venv/local/lib/python2.7/site-packages/web3/utils/functional.py", line 14, in inner
    value = fn(*args, **kwargs)
  File "/home/carver/filter_listener/venv/local/lib/python2.7/site-packages/web3/eth.py", line 312, in getFilterChanges
    "eth_getFilterChanges", [filter_id],
  File "/home/carver/filter_listener/venv/local/lib/python2.7/site-packages/web3/providers/manager.py", line 35, in request_blocking
    raise ValueError(response["error"])
ValueError: {u'message': u'filter not found', u'code': -32000}
```
