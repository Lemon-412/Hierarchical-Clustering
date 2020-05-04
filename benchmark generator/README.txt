想要正确使用benchmark生成数据，请进行如下步骤：

1.使用cmd指令进入benchmark.exe所在目录下
2.输入benchmark 回车
3.根据benchmark提供的参数输入：
-N              [number of nodes]
-k              [average degree]
-maxk           [maximum degree]
-mu             [mixing parameter]
-t1             [minus exponent for the degree sequence]
-t2             [minus exponent for the community size distribution]
-minc           [minimum for the community sizes]
-maxc           [maximum for the community sizes]
-on             [number of overlapping nodes]
-om             [number of memberships of the overlapping nodes]
-C              [Average clustering coefficient]

样例：
benchmark -N 1000 -k 15 -maxk 50 -mu 0.1 -minc 20 -maxc 50 -C 0.7

输出文件:
所有文件输出在当前目录下
community.dat	表示每一个节点编号所应该对应的社区编号
network.dat	表示网络中的每一条边，这也是项目唯一用到的原始数据
statistics.dat	包含有各类生成数据的信息，如混合度、平均度数等 
time_seed.dat	随机数种子

在“一些合适的数据”文件夹中，我们给出了一些精心挑选的有趣的数据，以备调试