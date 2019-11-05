#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# @file: blockchain.py
#
# @refer:
#   https://learnblockchain.cn/2017/10/27/build_blockchain_by_python/
#
# prepare install on ubuntu with python2.7
#   sudo apt install python-pip
#   sudo pip install Flask
#   sudo pip install requests
#######################################################################
import os, sys, stat, signal, shutil, inspect, commands, datetime

import hashlib, json, requests

from time import time

# python3: from urllib.parse import urlparse
from urlparse import urlparse


#######################################################################
# Blockchain 类
#   用来管理链条，它能存储交易，加入新块等
class Blockchain(object):
    def __init__(self):
        # 用 set 来储存节点，这是一种避免重复添加节点的简单方法。
        self.nodes = set()

        # 储存区块链
        self.chain = []

        # 储存交易
        self.current_transactions = []

        # 构造一个创世块（没有前区块的第一个区块），并且给它加上一个工作量证明。
        # 每个区块都需要经过工作量证明，俗称挖矿。
        self.new_block(proof=100, previous_hash=1)
        pass


    def new_block(self, proof, previous_hash=None):
        """
        生成新块, 每个区块包含属性：
            索引 (index)
            Unix 时间戳 (timestamp)
            交易列表 (transactions)
            工作量证明 (proof)
            前一个区块的 Hash 值 (previous_hash)
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block


    # 向列表中添加一个交易记录，并返回该记录将被添加到的区块 (下一个待挖掘的区块) 的索引,
    # 等下在用户提交交易时会有用。
    def new_transaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of transactions
        """
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

 
    @staticmethod
    def hash(block):
        """
        生成块的 SHA-256 hash值
        :param block: <dict> Block
        :return: <str>
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        # Returns the last Block in the chain
        return self.chain[-1]


    # 工作量证明(PoW)的核心思想:
    #   新的区块依赖工作量证明算法来构造。
    #   PoW 的目标是找出一个符合特定条件的数字，这个数字很难计算出来，但容易验证。
    def proof_of_work(self, last_proof):
        """
        简单的工作量证明:
         - 查找一个 p' 使得 hash(pp') 以4个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof


    @staticmethod
    def valid_proof(last_proof, proof):
        """
        验证证明: 是否hash(last_proof, proof)以4个0开头?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        guess = '{last_proof}{proof}'.format(last_proof=last_proof, proof=proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    # 注册节点
    # 在实现一致性算法之前，需要找到一种方式让一个节点知道它相邻的节点。每个节点都需要保存一份包含网络中其它节点的记录。
    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.94.107:5001'
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


    # 一致性（共识）
    # 区块链系统应该是分布式的。既然是分布式的，那么我们究竟拿什么保证所有节点有同样的链呢？这就是一致性问题，
    # 我们要想在网络上有多个节点，就必须实现一个一致性的算法。
    #
    # 实现共识算法
    # 冲突是指不同的节点拥有不同的链，为了解决这个问题，规定最长的、有效的链才是最终的链，换句话说，网络中有效最长链才是实际的链。
    # 使用 valid_chain 和 resolve_conflicts 的算法，来达到网络中的共识。
    #
    # 用来检查是否是有效链，遍历每个块验证 hash 和 proof
    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print('{last_block}'.format(last_block=last_block))
            print('{block}'.format(block=block))

            print("\n-----------\n")

            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True


    # 用来解决冲突，遍历所有的邻居节点，并用valid_chain()检查链的有效性，如果发现有效更长链，就替换掉自己的链
    def resolve_conflicts(self):
        """
        共识算法解决冲突
        使用网络中最长的链.
        :return: <bool> True 如果链被取代, 否则为False
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get('http://{node}/chain'.format(node=node))

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False