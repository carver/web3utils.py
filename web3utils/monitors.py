
from __future__ import print_function

import sys

from . import eth


class TransactionMonitor(object):
    '''
    For now, assume that the python process will shut down when the caller is done using it.
    (ie~ don't offer unwatch option, and be super lazy about stopping filters)
    '''

    def __init__(self, confident_depth=3):
        '''
        @param confident_depth the number of blocks deep before a transaction
            is considered to be mined confidently for your application
        '''
        # variables use "solid" as a shorter way to describe confidence
        self.solid_depth = confident_depth
        self.solid_height = 0
        self.solid_block_id = None
        self.solid_watchers = []
        self.block_watchers = []
        self.pending_tx_watchers = []
        self.phantom_txids = set()
        self.last_block_num = None

    def watch_confident_blocks(self, callback):
        '''
        Callback will receive two arguments:
        * the block object now considered confident
        * a list of transaction objects in that block
        '''
        self.solid_watchers.append(callback)
        self._start_watching_blocks()

    def watch_blocks(self, callback):
        '''
        Callback will receive one argument: the block object just observed.

        Callback will receive duplicates of any given block number,
        because the chain forks regularly at the tip

        This is equivalent to `eth.filter('latest')`
        '''
        self.block_watchers.append(callback)
        self._start_watching_blocks()

    def watch_pending_transactions(self, callback):
        '''
        Callback will receive one argument: the transaction object just observed

        This is equivalent to `eth.filter('pending')`
        '''
        self.pending_tx_watchers.append(callback)
        if len(self.pending_tx_watchers) == 1:
            eth.filter('pending').watch(self._new_pending_tx)

    def _start_watching_blocks(self):
        '''
        Internal: call immediately after registering a block watcher
        If the new watcher is the first, then start watching web3 remotely
        '''
        if sum(map(len, (self.solid_watchers, self.block_watchers))) == 1:
            eth.filter('latest').watch(self._new_block)

    def _new_pending_tx(self, txid):
        tx = eth.getTransaction(txid)
        if not tx:
            self.phantom_txids.add(txid)
            return
        for watcher in self.pending_tx_watchers:
            watcher(tx)

    def _new_block(self, blockid):
        block = eth.getBlock(blockid)
        if not block:
            print('WARNING: cannot find block ' + blockid, file=sys.stderr)
            return
        if self.last_block_num and block['number'] > self.last_block_num + 1:
            print('WARNING: skipped blocks from %d to %d' % (self.last_block_num, block['number']),
                  file=sys.stderr)
        for watcher in self.block_watchers:
            watcher(block)
        self._recover_phantom_txs()
        self._solid_monitor(block['number'])
        self.last_block_num = block['number']

    def _solid_monitor(self, latest_block_num):
        solid_block_num = latest_block_num - self.solid_depth
        new_solid_block = eth.getBlock(solid_block_num)
        if self.solid_height and solid_block_num <= self.solid_height:
            self._detect_reorg(new_solid_block)
            return
        solid_txs = []
        for txid in new_solid_block['transactions']:
            tx = eth.getTransaction(txid)
            assert tx is not None, "Confident tx %s was None in block %d" % (txid, solid_block_num)
            solid_txs.append(tx)
        for watcher in self.solid_watchers:
            watcher(new_solid_block, solid_txs)
        self.solid_height = solid_block_num
        self.solid_block_id = new_solid_block['hash']

    def _detect_reorg(self, new_solid_block):
        if new_solid_block['number'] == self.solid_height and \
                new_solid_block['hash'] != self.solid_block_id:
            print(
                'WARNING! reorganized the confident block',
                self.solid_height,
                'from',
                self.solid_depth,
                'blocks back! changed from hash',
                self.solid_block_id,
                'to hash',
                new_solid_block['hash'],
                '. Ignoring...',
                file=sys.stderr
                )

    def _recover_phantom_txs(self):
        phantom_copy = list(self.phantom_txids)
        for txid in phantom_copy:
            self.phantom_txids.remove(txid)
            tx = eth.getTransaction(txid)
            if tx:
                if tx.blockNumber is None or tx.blockNumber > self.solid_height:
                    self._new_pending_tx(txid)
