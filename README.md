# blockchain-sample

** 一个简明的python示例说明区块链原理**

参考文章：

[用 Python 从零开始创建区块链](https://learnblockchain.cn/2017/10/27/build_blockchain_by_python/)

[Learn Blockchains by Building One](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46)

区块链技术原理并不复杂，是一种建立在p2p网络之上的分布式数据加密存储模型。理论上每个节点都存储一个数据的加密备份，并能验证数据的正确性和不可篡改。有多种开源实现，但是场景各有不同。本文是按照

## 示例代码

pysrc/blockchain.py - 区块链算法模拟实现
pysrc/nodeserver.py - 区块链网络服务模拟实现

## 启动节点测试

- 在一台机器上（假设ip=yourhost)，打开终端，分别启动1个节点（端口不同）

	$ python nodeserver.py 5001
	$ python nodeserver.py 5002

- 打开firefox浏览器，确保已经安装了插件 RESTED - A REST client for the rest of us 

- firefox浏览器添加以下浏览地址：

	1)
		http://yourhost:5001/transactions/new  创建一个交易并添加到区块
		http://yourhost:5001/mine              挖掘新的区块
		http://yourhost:5001/chain             返回整个区块链
		http://yourhost:5001/nodes/register    注册节点, 每个节点注册全部节点
		http://yourhost:5001/nodes/resolve     解决节点冲突

	2)
		http://yourhost:5002/transactions/new  创建一个交易并添加到区块
		http://yourhost:5002/mine              挖掘新的区块
		http://yourhost:5002/chain             返回整个区块链
		http://yourhost:5002/nodes/register    注册节点, 每个节点注册全部节点
		http://yourhost:5002/nodes/resolve     解决节点冲突

## 注册节点

使用 RESTED 插件，在每个节点上执行注册（？=1，2）：

POST=http://yourhost:500？/nodes/register
Type=JSON
Name=nodes Value=["http://yourhost:5001","http://yourhost:5002"]

或者：

	$ curl -X POST -H "Content-Type: application/json" -d '{
        "nodes": ["http://yourhost:5001","http://yourhost:5002"]
        }' "http://yourhost:500？/nodes/register"

## 节点挖矿

分别刷新地址，例如5001上按3次，5002上按5次：

	http://yourhost:500？/mine

查看每个节点块链数目（http://yourhost:500？/chain) 已经不同了。这时在5001上刷新解决冲突地址：

	http://yourhost:5001/nodes/resolve

再次查看5001和5002节点数目，已经完全一样了。

### End