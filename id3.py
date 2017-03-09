import pandas as pd
import math


class ID3(object):
    class Node(object):
        def __init__(self, _id):
            self.id = _id
            self.attribute = None
            self.branches = {}

        def __str__(self):
            return self.attribute

        __repr__ = __str__

        @property
        def node_name(self):
            # 可视化时，每个node，必须要有独一无二的name
            return ''.join([self.attribute, str(self.id)])

        def add_branch_node(self, value, node):
            self.branches[value] = node

        def add_to_graph(self, graph):
            graph.node(self.node_name, self.__str__())
            for edge_name, branch_node in self.branches.items():
                branch_node.add_to_graph(graph)
                graph.edge(self.node_name, branch_node.node_name, label=str(edge_name))

    def __init__(self, data, target):
        self.node_counter = 0 # 方便可视化
        self.root_node = None
        self.data = data
        self.target = target
        self.attribute_values = {}
        for attribute in data.columns:
            self.attribute_values[attribute] = data[attribute].unique()

    def entropy(self, data, attribute):
        value_freq = data[attribute].value_counts()
        data_entropy = 0.0
        N = len(data)
        for value, freq in value_freq.items():
            p = freq / N
            data_entropy += p * self.info(data, attribute, value)
        return data_entropy

    def info(self, data, attribute, attribute_value):
        data = data[data[attribute] == attribute_value]
        target_value_freq = data[self.target].value_counts()
        data_info = 0.0
        N = len(data)
        for freq in target_value_freq.values:
            p = freq / N
            data_info -= p * math.log(p, 2)
        return data_info

    def make_up_counts(self, attribute, counts):
        new_counts = dict.fromkeys(self.attribute_values[self.target], 0.0)
        new_counts.update(counts)
        return new_counts

    def make_decision_tree(self, data, node):
        # 当数据都为同一类数据时，直接返回
        if len(data[self.target].value_counts()) == 1:
            node.attribute = data[self.target].value_counts().index[0]
            return
        # 寻找熵最小的属性
        min_entropy = 1.0
        for attribute in data.columns:
            if attribute == self.target:
                continue
            temp_entropy = self.entropy(data, attribute)
            if temp_entropy < min_entropy:
                min_entropy = temp_entropy
                node.attribute = attribute

        for value in data[node.attribute].value_counts().index:
            branch_data = data[data[node.attribute] == value]
            branch_data = branch_data.drop(node.attribute, axis=1)
            branch_node = self.new_node()
            node.add_branch_node(value, branch_node)
            self.make_decision_tree(branch_data, branch_node)

    def run(self):
        self.root_node = self.new_node()
        self.make_decision_tree(self.data, self.root_node)

    def new_node(self):
        self.node_counter += 1
        return self.Node(_id=self.node_counter)

    def render_decision_tree(self, filename):
        if not self.root_node:
            raise ValueError('Tree not decided!')

        from graphviz import Digraph
        dot_graph = Digraph(comment="Decision Tree")
        self.root_node.add_to_graph(dot_graph)
        dot_graph.render(filename)

if __name__ == '__main__':
    test_data = pd.read_csv('golf.csv')
    test_id3 = ID3(test_data, target='play')
    test_id3.run()
    test_id3.render_decision_tree('./dtree')