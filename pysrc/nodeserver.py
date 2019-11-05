#!/usr/bin/python
#-*- coding: UTF-8 -*-
#
# @file: nodeserver.py
#   区块链网络中的一个节点
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

import hashlib, json

from textwrap import dedent
from time import time
from uuid import uuid4

# 使用 Python Flask 框架，这是一个轻量 Web 应用框架，它方便将网络请求映射到 Python 函数，
#   让 Blockchain 运行在基于 Flask web 上。
from flask import Flask, jsonify, request

from blockchain import Blockchain

#######################################################################
# 区块链网络中的一个节点
#  创建三个接口：
#     /transactions/new  创建一个交易并添加到区块
#     /mine              告诉服务器去挖掘新的区块
#     /chain             返回整个区块链
#     /nodes/register    注册节点, 每个节点注册全部节点
#     /nodes/resolve     解决冲突, 每个节点解决冲突
#######################################################################
# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # 挖矿很简单，做了三件事：
    #  1. 计算工作量证明 PoW
    #  2. 通过新增一个交易授予矿工(自己)一个币
    #  3. 构造新区块并将其添加到链中
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # 给工作量证明的节点提供奖励.
    # 发送者为 "0" 表明是新挖出的币
    blockchain.new_transaction("0", node_identifier, 1)

    # Forge the new Block by adding it to the chain
    block = blockchain.new_block(proof)

    response = {
        'message': "New Block Forged",
        'index':   block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': 'Transaction will be added to Block {index}'.format(index=index)}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    print "=request=", request
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


#######################################################################
# 在一台机机开启不同的网络端口来模拟多节点的网络，这里在同一台机器开启不同的端口演示，
# 在不同的终端运行命令，就启动了两个节点：
#   $ python nodeserver.py 5001
#   $ python nodeserver.py 5002
#
# node1:  http://yourhost:5001
# node2:  http://yourhost:5002
#
# 1) 挖矿:
#   http://192.168.94.107:5001/mine
#
# 2) 添加一个新交易 (curl 或 firefox rested plugin)
#   $ curl -X POST -H "Content-Type: application/json" -d '{
#        "sender": "d4ee26eee15148ee92c6cd394edd974e",
#        "recipient": "someone-other-address",
#        "amount": 5
#    }' "http://localhost:5001/transactions/new"
#
# 3) 得到所有的块信息:
#   http://192.168.94.107:5001/chain
#
#
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s PORT" % sys.argv[0]
        sys.exit(1)

    port = int(sys.argv[1])
    print "blockchain nodeserver starting on port %d ..." % port

    app.run(host='0.0.0.0', port=port)
