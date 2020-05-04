import matplotlib.pyplot as plt
import math
import sys


class cluster_analysis:
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

    def __init__(self):
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

    def read_file(self, file_name):
        self.__init__()
        try:
            with open(file_name, 'r') as file:
                for line in file.readlines():
                    line_list = list(map(int, line.strip().split('\t')))
                    if line_list[0] > line_list[1]:
                        self.node_num = max(self.node_num, line_list[0])
                        while len(self.node_dat) < line_list[0] + 1:
                            self.node_dat.append([])
                        self.line_dat.append(line_list)
                        self.node_dat[line_list[1]].append(line_list[0])
                        self.node_dat[line_list[0]].append(line_list[1])
        except OSError as error:
            print(error)

    def cluster(self, p1=0.5, p2=0.5):
        self.parameter_x = p1
        self.parameter_y = p2
        for elem_x in range(self.node_num + 1):
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
        while break_flag:
            break_flag = False
            com_x = 0
            while com_x < len(self.community):
                com_y = com_x + 1
                while com_y < len(self.community):
                    if self.parameter_x < len(list((set(self.community[com_x]).union(set(self.community[com_y]))) ^ (
                            set(self.community[com_x]) ^ set(self.community[com_y])))) / \
                            min(len(self.community[com_x]), len(self.community[com_y])):
                        self.community[com_x] = list(set(self.community[com_x]).union(set(self.community[com_y])))
                        del self.community[com_y]
                        break_flag = True
                    com_y += 1
                com_x += 1
        self.node_community_info = []
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
        while break_flag:
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
        self.community_num = len(self.community)
        for i in range(1, self.node_num + 1):
            if len(self.node_community_info[i]) == 0 and i not in self.node_multi_community:
                self.node_none_community.append(i)

    def visualize(self):
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
    def __rgb2hex(r, g, b):
        return '#' + (str(hex(r))[2:]).zfill(2) + (str(hex(g))[2:]).zfill(2) + (str(hex(b))[2:]).zfill(2)

    def show(self, draw_label=True, draw_line=True):
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

    def dbg(self):
        print('node_num', self.node_num)
        print('community_num', self.community_num)
        with open('log.txt', 'w') as file:
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


def main():
    ca = cluster_analysis()

    # ca.__init__()
    # ca.read_file('network.dat')
    # ca.cluster(0, 0)
    # ca.visualize()
    # ca.show()

    ca.__init__()
    ca.read_file('network.dat')
    ca.cluster(0.5, 0.5)
    ca.visualize()
    ca.show(True,True)

    ca.dbg()


if __name__ == '__main__':
    main()
