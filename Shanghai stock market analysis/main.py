import requests
import matplotlib.pyplot as plt
import json
import time
import math
import os
import sys
import copy


stock_list_url = ["http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?cb"
                  "=jQuery11240590191491396463_1557047798748&type=CT&token=4f1862fc3b5e77c150a2b985b12db0fd&sty"
                  "=FCOIATC&js=(%7Bdata%3A%5B(x)%5D%2CrecordsFiltered%3A(tot)%7D)&cmd=C.BK07071&st=("
                  "ChangePercent)&sr=-1&p=", "&ps=20&_="]

stock_page_url = ["http://quote.eastmoney.com/sh", ".html"]

stock_data_url = ["http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?rtntype=5&token=4f1862fc3b5e77c150a2b985b12db0fd"
                  "&cb=jQuery18303474420119495003_",
                  "&id=",
                  "1&type=k&authorityType=&_="]


# 聚类分析类
class ClusterAnalysis:
    node_num = 0
    parameter_x = 0.0
    parameter_y = 0.0

    line_dat = []
    node_dat = []

    k_friends = []
    community = []
    community_num = 0

    node_community_info = []
    node_multi_community = []
    node_none_community = []

    community_center = []
    community_radius = []

    center_radius = 0.0
    multi_abandon_radius = 0.0
    node_pos = []

    def __init__(self):  # 初始化
        self.node_num = 0
        self.parameter_x = 0.0
        self.parameter_y = 0.0
        self.line_dat = []
        self.node_dat = []
        self.k_friends = []
        self.community = []
        self.node_community_info = []
        self.node_multi_community = []
        self.node_none_community = []
        self.community_center = []
        self.community_radius = []
        self.community_num = 0
        self.center_radius = 0.0
        self.multi_abandon_radius = 0.0
        self.node_pos = []

    def read(self, arr, num):  # 继承特征矩阵与节点个数
        self.__init__()
        self.node_num = num + 1
        for i in range(self.node_num + 1):
            self.node_dat.append([])
        self.line_dat = copy.deepcopy(arr)
        for line in self.line_dat:
            line[0] += 1
            line[1] += 1
            self.node_dat[line[0]].append(line[1])
            self.node_dat[line[1]].append(line[0])

    def cluster(self, p2=0.5):  # 聚类分析
        self.parameter_x = 0.0
        self.parameter_y = p2
        for elem_x in range(self.node_num + 1):  # 产生ego net
            self.k_friends.append([])
            self.community.append([elem_x])
            for elem_y in self.node_dat[elem_x]:
                fr = 0
                for i in self.node_dat[elem_y]:
                    if i in self.node_dat[elem_x]:
                        fr += 1
                if self.parameter_x < (fr + 1) / min(len(self.node_dat[elem_x]), len(self.node_dat[elem_y])):
                    self.k_friends[elem_x].append(True)
                    self.community[elem_x].append(elem_y)
                else:
                    self.k_friends[elem_x].append(False)
        break_flag = True
        print(self.community)
        while break_flag:  # 聚类算法核心：社区合并；迭代直至不再产生新的社区合并为止
            break_flag = False
            com_x = 0
            while com_x < len(self.community):
                com_y = com_x + 1
                while com_y < len(self.community):
                    if self.parameter_y < len(list((set(self.community[com_x]).union(set(self.community[com_y]))) ^ (
                            set(self.community[com_x]) ^ set(self.community[com_y])))) / \
                            min(len(self.community[com_x]), len(self.community[com_y])):
                        self.community[com_x] = list(set(self.community[com_x]).union(set(self.community[com_y])))
                        del self.community[com_y]
                        break_flag = True
                    com_y += 1
                com_x += 1
        self.node_community_info = []  # 记录节点对应社区编号
        for i in range(self.node_num + 1):
            self.node_community_info.append([])
        for i in range(len(self.community)):
            for j in self.community[i]:
                self.node_community_info[j].append(i)
        self.node_none_community = []
        self.node_multi_community = []
        for i in range(self.node_num + 1):
            if len(self.node_community_info[i]) > 1:
                self.node_multi_community.append(i)
                for j in self.node_community_info[i]:
                    self.community[j].remove(i)
        break_flag = True
        while break_flag:  # 删除只有一个节点的社区
            break_flag = False
            for i in range(len(self.community)):
                if len(self.community[i]) <= 1:
                    del (self.community[i])
                    break_flag = True
                    break
        self.node_community_info = []
        for i in range(self.node_num + 1):
            self.node_community_info.append([])
        for i in range(len(self.community)):
            for j in self.community[i]:
                self.node_community_info[j].append(i)
        self.community_num = len(self.community)  # 统计社区个数
        for i in range(1, self.node_num + 1):
            if len(self.node_community_info[i]) == 0 and i not in self.node_multi_community:
                self.node_none_community.append(i)

    def visualize(self):  # 与可视化相关的计算
        r = 0
        for i in range(self.community_num):
            self.community_radius.append(len(self.community[i]) / 2 / math.pi)
            r = r + self.community_radius[i]
        self.multi_abandon_radius = (len(self.node_multi_community) + len(self.node_none_community)) / 2 / math.pi
        if len(self.community_radius) != 0:
            self.center_radius = max(1.2 * r / math.pi, 1.4 * self.multi_abandon_radius + max(self.community_radius))
        else:
            self.center_radius = max(1.2 * r / math.pi, 1.4 * self.multi_abandon_radius)
        node_cnt_in_community = 0
        for i in self.community:
            node_cnt_in_community += len(i)
        if node_cnt_in_community == 0:
            print('No community, nothing to do')
            sys.exit()
        angle = 0.0
        self.community_center = []
        for i in range(self.community_num):
            self.community_center.append(
                [self.center_radius * math.cos(angle + math.pi * len(self.community[i]) / node_cnt_in_community),
                 self.center_radius * math.sin(angle + math.pi * len(self.community[i]) / node_cnt_in_community)])
            angle += 2 * math.pi * len(self.community[i]) / node_cnt_in_community
        self.node_pos = []
        for i in range(self.node_num + 1):
            self.node_pos.append([-1, -1])
        for i in range(self.community_num):
            angle = 0.0
            for j in range(len(self.community[i])):
                self.node_pos[self.community[i][j]][0] = self.community_center[i][0] + self.community_radius[
                    i] * math.cos(angle)
                self.node_pos[self.community[i][j]][1] = self.community_center[i][1] + self.community_radius[
                    i] * math.sin(angle)
                angle += 2 * math.pi / len(self.community[i])
        node_in_center = sorted(list(set(self.node_none_community).union(set(self.node_multi_community))))
        angle = 0.0
        for i in range(len(node_in_center)):
            self.node_pos[node_in_center[i]][0] = self.multi_abandon_radius * math.cos(angle)
            self.node_pos[node_in_center[i]][1] = self.multi_abandon_radius * math.sin(angle)
            angle += 2 * math.pi / len(node_in_center)

    @staticmethod
    def __rgb2hex(r, g, b):  # rgb转hex辅助静态函数
        return '#' + (str(hex(r))[2:]).zfill(2) + (str(hex(g))[2:]).zfill(2) + (str(hex(b))[2:]).zfill(2)

    def show(self, draw_label=False, draw_line=True):  # 可视化函数
        color = [[255, 0, 0], [255, 165, 0], [255, 255, 0], [0, 255, 0], [0, 127, 255], [0, 0, 255], [139, 0, 255]]
        node_color = [[]]
        for i in range(1, self.node_num + 1):
            if len(self.node_community_info[i]) >= 1:
                c = [0, 0, 0]
                for j in range(len(self.node_community_info[i])):
                    c[0] = color[self.node_community_info[i][j] % len(color)][0]
                    c[1] = color[self.node_community_info[i][j] % len(color)][1]
                    c[2] = color[self.node_community_info[i][j] % len(color)][2]
                node_color.append([c[0] / len(self.node_community_info[i]),
                                   c[1] / len(self.node_community_info[i]),
                                   c[2] / len(self.node_community_info[i])])
            else:
                node_color.append([128, 128, 128])
        line_color = []
        for i in range(len(self.line_dat)):
            x = self.line_dat[i][0]
            y = self.line_dat[i][1]
            line_color.append([(node_color[x][0] + node_color[y][0]) / 2,
                               (node_color[x][1] + node_color[y][1]) / 2,
                               (node_color[x][2] + node_color[y][2]) / 2])
        for i in range(1, self.node_num + 1):
            if draw_label:
                plt.text(self.node_pos[i][0], self.node_pos[i][1], i, color='black', fontsize=7,
                         verticalalignment='top', horizontalalignment='right')
            plt.plot(self.node_pos[i][0], self.node_pos[i][1], "ro",
                     color=self.__rgb2hex(int(node_color[i][0]), int(node_color[i][1]), int(node_color[i][2])),
                     markersize=3)
        if draw_line:
            for i in range(len(self.line_dat)):
                plt.plot([self.node_pos[self.line_dat[i][0]][0], self.node_pos[self.line_dat[i][1]][0]],
                         [self.node_pos[self.line_dat[i][0]][1], self.node_pos[self.line_dat[i][1]][1]],
                         color=self.__rgb2hex(int(line_color[i][0]), int(line_color[i][1]), int(line_color[i][2])),
                         linewidth=0.5)
        plt.savefig('output.png')
        plt.show()
        plt.clf()

    def dbg(self):  # 打印日志
        print('node_num', self.node_num)
        print('community_num', self.community_num)
        with open('bin/log.txt', 'w') as file:
            file.write('node_num\n' + str(self.node_num))
            file.write('\n\n')
            file.write('line_dat\n' + str(self.line_dat))
            file.write('\n\n')
            file.write('node_dat\n' + str(self.node_dat))
            file.write('\n\n')
            file.write('k_friends\n' + str(self.k_friends))
            file.write('\n\n')
            file.write('community\n' + str(self.community))
            file.write('\n\n')
            file.write('node_community_info\n' + str(self.node_community_info))
            file.write('\n\n')
            file.write('node_multi_community\n' + str(self.node_multi_community))
            file.write('\n\n')
            file.write('node_none_community\n' + str(self.node_none_community))
            file.write('\n\n')
            file.write('community_center\n' + str(self.community_center))
            file.write('\n\n')
            file.write('community_radius\n' + str(self.community_radius))


# 股市分析类
class StockAnalysis:
    def __init__(self):  # 初始化函数
        self.session = requests.session()
        self.current_time = str(int(time.time() * 1000))
        self.stock_num = 0
        self.stock_list = []
        self.stock_data = []
        self.regression = []
        # if not os.path.exists(self.current_time):
        #     os.mkdir(self.current_time)
        if os.path.exists('bin'):  # 创建日志目录
            if os.path.exists('bin/stock_list.json'):
                os.remove('bin/stock_list.json')
            if os.path.exists('bin/stock_list.txt'):
                os.remove('bin/stock_list.txt')
            if os.path.exists('bin/stock_data.json'):
                os.remove('bin/stock_data.json')
            if os.path.exists('bin/stock_data.txt'):
                os.remove('bin/stock_data.txt')
        else:
            os.mkdir('bin')

    def get_stock_list(self):  # 爬取沪股清单，获取代码和股票中文名称
        self.stock_list = []
        file = open('bin/stock_list.txt', 'w')
        page = 0
        pre_list = ''
        break_flag = False
        print('loading stocks', end='', flush=True)
        while not break_flag:
            page += 1
            while True:
                try:
                    dat = self.session.get(stock_list_url[0] + str(page) + stock_list_url[1] + self.current_time,
                                           timeout=20).text
                    if dat == pre_list:
                        break_flag = True
                        break
                    pre_list = dat
                    time.sleep(0.1)
                    json_file = json.loads(dat[dat.find('['):dat.find(']') + 1])
                    with open('./bin/stock_list.json', 'a', encoding='utf-8') as js_file:
                        json.dump(json_file, js_file, ensure_ascii=False)
                    for i in json_file:
                        cur = i.split(',')
                        for elem in cur:
                            file.write(elem + '\t')
                        file.write('\n')
                        self.stock_list.append([cur[1], cur[2]])
                    print('.', end='', flush=True)
                    break
                except Exception as ERR:  # 异常处理，常见有网络错误或超时
                    print('\n' + str(ERR))
                    time.sleep(5)
        file.close()
        self.stock_num = len(self.stock_list)
        print('\n' + str(self.stock_num) + ' stocks in all...')

    def get_stock_data(self):  # 爬取个股历史收盘价
        if self.stock_num == 0:
            self.get_stock_list()
        self.stock_data = []
        for i in range(self.stock_num):
            self.stock_data.append([])
            while True:
                try:
                    self.session.get(stock_page_url[0] + self.stock_list[i][0] + stock_page_url[1], timeout=10)
                    dat = self.session.get(
                        stock_data_url[0] + self.current_time + stock_data_url[1] + self.stock_list[i][0] +
                        stock_data_url[2] + self.current_time,
                        timeout=10).text
                    json_file = json.loads(dat[dat.find('['):dat.find(']') + 1])
                    with open('./bin/stock_data.json', 'a', encoding='utf-8') as js_file:
                        json.dump(json_file, js_file, ensure_ascii=False)
                    pre = -1.0
                    for elem in json_file:
                        cur = elem.split(',')
                        if pre != -1.0:
                            self.stock_data[i].append(max(-100, min(100, int((float(cur[2]) - pre) / pre * 1000))))
                        pre = float(cur[2])
                    time.sleep(0.2)
                    print(self.stock_list[i][1], self.stock_data[i])
                    break
                except Exception as ERR:  # 异常处理，常见有网络错误或超时
                    print('\n' + str(ERR), flush=True)
                    time.sleep(5)
        file = open('bin/stock_data.txt', 'w')
        for i in range(self.stock_num):
            file.write(
                self.stock_list[i][0] + '\t' + self.stock_list[i][1] + '\t' + str(len(self.stock_data[i])) + '\n')
            for j in range(len(self.stock_data[i])):
                file.write(str(self.stock_data[i][j] / 10) + '%\t')
            file.write('\n')
        file.close()

    def get_regression(self):  # 数据清洗与曼哈顿距离分析
        print('regression analysis...', end='', flush=True)
        self.regression = []
        for i in range(self.stock_num):
            self.regression.append([])
            for j in range(self.stock_num):
                if i == j:
                    self.regression[i].append(0.00)
                    continue
                if i > j:
                    self.regression[i].append(self.regression[j][i])
                    continue
                len1 = len(self.stock_data[i])
                len2 = len(self.stock_data[j])
                min_date = min(len1, len2) - 10
                if min_date <= 10:
                    self.regression[i].append(3.33)
                    continue
                summon = 0
                for date in range(min_date):
                    summon += abs(self.stock_data[i][len1 - date - 1] - self.stock_data[j][len2 - date - 1])
                self.regression[i].append(summon / min_date)
        file = open('bin/regression_analysis.txt', 'w')
        for i in range(self.stock_num):
            file.write(str(i) + '\n')
            for j in range(self.stock_num):
                file.write(str(round(self.regression[i][j], 2)) + ' ')
            file.write('\n\n')
        file.close()
        print('done')

    def show_image(self):  # 输出可调图形：沪股相似度分布直方图
        x = ['0.0-10.0', '10.0-20.0', '20.0-30.0', '30.0-40.0', '40.0-50.0',
             '50.0-60.0', '60.0-70.0', '70.0-80.0', '80.0-90.0', '90.0-100.0']
        height = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(self.stock_num):
            for j in range(i+1, self.stock_num):
                height[int(math.floor(self.regression[i][j]))//10] += 1
        plt.figure(figsize=(14, 8))
        plt.bar(x, height, 0.35, color='#87CEFA', align='center', edgecolor='black')
        plt.xlabel('Similarity Degree(%)')
        plt.ylabel('Number of stocks')
        plt.xticks(rotation=30)
        plt.yticks(rotation=30)
        for i in range(10):
            plt.text(i, height[i], height[i], ha='center', va='bottom', fontsize=7)
        plt.title('Similarity Distribution of Shanghai Stock Market')
        plt.savefig('Similarity_Distribution_of_Shanghai_Stock_Market.png', dpi=800)
        plt.show()
        print(height)

    def cluster_analysis(self, x1=0.1, x2=0.7):  # 调用聚类分析类，实现沪股聚类分析与预测
        ca = ClusterAnalysis()
        regression_data = []
        cnt = 0
        for i in range(self.stock_num):
            for j in range(i+1, self.stock_num):
                if self.regression[i][j] < x1 * 100:
                    regression_data.append([j, i])
                    cnt += 1
        print(cnt)
        ca.read(regression_data, self.stock_num)
        ca.cluster(x2)
        # ca.visualize()
        # ca.show(True, True)
        ca.dbg()
        result = copy.deepcopy(ca.community)
        for i in range(len(result)):
            print('the ' + str(i + 1) + 'th cluster')
            for elem in result[i]:
                print(self.stock_list[elem + 1][0] + '\t' + self.stock_list[elem + 1][1])
            print('')
        with open('bin/cluster_result.txt', 'w') as file:
            for i in range(len(result)):
                file.write('the ' + str(i + 1) + 'th cluster\n')
                for elem in result[i]:
                    file.write(self.stock_list[elem + 1][0] + '\t' + self.stock_list[elem + 1][1] + '\n')
                file.write('\n')


def main():  # 主函数
    stk = StockAnalysis()               # 创建股市分析类实体对象
    stk.get_stock_data()                # 爬取沪股表单和历史收盘价
    stk.get_regression()                # 相似度分析
    stk.show_image()                    # 输出可调图形
    x1 = float(input('x1: '))           # 输入聚类参数x1
    x2 = float(input('x2: '))           # 输入聚类参数x2
    stk.cluster_analysis(x1, x2)        # 进行聚类分析


if __name__ == '__main__':
    main()  # 运行主函数
