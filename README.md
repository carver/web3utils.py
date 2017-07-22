
# web3utils.py - Some sugar on top of web3.py

web3utils is a very thin layer over [web3.py](https://github.com/pipermerriam/web3.py) --
these are the main features:

* immediate access to a `web3` and `eth` object if you have a standard setup
* shorter way to call contract functions
* encode all contract string arguments as utf-8
* autoset encoding of `web3.sha3(value)`, if `type(value) == bytes`
* return `None` from a contract call, in place of '0x0000000...'

This handful of changes made for quicker shell usage and coding for me. I hope it does for you, too!

I have also contributed a bit to web3.py, and intend to push these pieces upstream, if they want it.

This is a Python3-only library. It turns out that the distinction between strings and bytes is
pretty important. If you want to write code for the future (Ethereum), don't use a language from the
past.

### Setup

`pip install web3utils`

If you want to contribute:

```
git clone git@github.com/carver/web3utils.py.git
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

### Usage

Print your primary account balance, denominated in ether:

```
from web3utils import web3, eth

wei = eth.getBalance(eth.accounts[0])
balance = web3.fromWei(wei, 'ether')

print(balance)
```

Confirm the owner of the '.eth' domain in the Ethereum Name Service

```
import codecs

ENS_ABI = { ... <define abi> ... }
ENS_ADDR = '0x314159265dd8dbb310642f98f50c066173c1259b'

ens = eth.contract(abi=ENS_ABI, address=ENS_ADDR)

AUCTION_REGISTRAR_NODE = codecs.decode('93cdeb708b7545dc668eb9280176169d1c33cfd8ed6f04690a0bcc88a93fc4ae', 'hex')

assert ens.owner(AUCTION_REGISTRAR_NODE) == '0x6090a6e47849629b7245dfa1ca21d94cd15878ef'

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
  File "/home/jcarver/code/ens-register/venv/local/lib/python2.7/site-packages/web3/utils/filters.py", line 84, in _run
    changes = self.web3.eth.getFilterChanges(self.filter_id)
  File "/home/jcarver/code/ens-register/venv/local/lib/python2.7/site-packages/web3/utils/functional.py", line 14, in inner
    value = fn(*args, **kwargs)
  File "/home/jcarver/code/ens-register/venv/local/lib/python2.7/site-packages/web3/eth.py", line 312, in getFilterChanges
    "eth_getFilterChanges", [filter_id],
  File "/home/jcarver/code/ens-register/venv/local/lib/python2.7/site-packages/web3/providers/manager.py", line 35, in request_blocking
    raise ValueError(response["error"])
ValueError: {u'message': u'filter not found', u'code': -32000}
```
