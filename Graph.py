import time
import random

FACTOR = 0.8
DEFAULT_Q = 0.0


def calc_q(factor: float, reward: float, max_q: float) -> float:
    return reward + factor * max_q


class Edge:

    def __init__(self, start, end, weight: int, q=DEFAULT_Q) -> None:
        self.start = start
        self.end = end
        self.weight = weight
        self.q = q

    def __str__(self) -> str:
        return f'{self.start.name} -> {self.end.name} ({self.weight} - {self.q})'


class Vertex:

    def __init__(self, id: int, name: str, r=0.0) -> None:
        self.id = id
        self.name = name
        self.edges = []
        self.r = r

    def add_edge(self, edge: Edge) -> None:
        for e in self.edges:
            if e.end == edge.end:
                return
        self.edges.append(edge)

    def get_vertex_by_name(self, name: str) -> 'Vertex':
        for edge in self.edges:
            if edge.end.name == name:
                return edge.end
        return None

    def get_bigger_q_action(self) -> float:
        bigger_q = DEFAULT_Q
        for edge in self.edges:
            if edge.q > bigger_q:
                bigger_q = edge.q
        if bigger_q != DEFAULT_Q:
            print(f'Maior Q de {self.name} = {bigger_q}')
        return bigger_q

    def get_best_edge_end_index(self):
        edge_destiny = self.edges[0]
        for edge in self.edges:
            if edge.q > edge_destiny.q:
                edge_destiny = edge
        return self.edges.index(edge_destiny)

    def get_best_edge_end(self):
        edge_destiny = self.edges[0]
        for edge in self.edges:
            if edge.q > edge_destiny.q:
                edge_destiny = edge
        return edge_destiny.end

    def __str__(self) -> str:
        return f'{self.name} - (R={self.r})'


class Graph:

    def __init__(self) -> None:
        self.vertex = []
        self.start = None
        self.goal = None

    def get_all_vertex(self) -> list:
        return self.vertex

    def get_all_vertex_names(self) -> list:
        names = []
        for vertex in self.vertex:
            names.append(vertex.name)
        return names

    def get_all_edges(self) -> list:
        edges = []
        for vertex in self.vertex:
            for edge in vertex.edges:
                edges.append(edge)
        return edges

    def get_all_edges_names(self) -> list:
        edges = []
        for vertex in self.vertex:
            for edge in vertex.edges:
                edges.append(f'{edge.start.name} -> {edge.end.name}')
        return edges

    def add_vertex(self, vertex: Vertex) -> None:
        self.vertex.append(vertex)

    def get_vertex_by_name(self, name: str) -> Vertex:
        for vertex in self.vertex:
            if vertex.name == name:
                return vertex
        # raise Exception(f'Vertex with name {name} not found')
        return Vertex(0, '0', 0.0)

    def set_goal(self, goal: str) -> None:
        self.goal = self.get_vertex_by_name(goal)

    def set_start(self, start: str) -> None:
        self.start = self.get_vertex_by_name(start)

    def add_edge(self, start: str, end: str, weight: int) -> None:
        start = self.get_vertex_by_name(start)
        end = self.get_vertex_by_name(end)
        start.add_edge(Edge(start, end, weight))
        end.add_edge(Edge(end, start, weight))

    def define_reward(self, reward: float, vertex: Vertex) -> None:
        vertex.r = reward


class Agent:

    def update_q(self) -> None:
        print('Atualizando Q')
        if len(self.path) > 1:
            last_vertex = self.graph.get_vertex_by_name(self.path[-2].name)
            for edge in last_vertex.edges:
                if edge.end == self.path[-1]:
                    edge.q = calc_q(FACTOR, self.path[-1].r,
                                    self.path[-1].get_bigger_q_action())
                    print(
                        f'Q de {edge.start.name}->{edge.end.name} = {edge.q}')

        # for i in range(len(self.path) - 1):
        #     for edge in self.path[i].edges:
        #         if edge.end == self.path[i + 1]:
        #             edge.q = calc_q(FACTOR, self.path[i].r,
        #                             self.path[i + 1].get_bigger_q_action())
        #             print(FACTOR, self.path[i].r,
        #                   self.path[i + 1].get_bigger_q_action())
        #             print(
        #                 f'Q de {edge.start.name} -> {edge.end.name} atualizado para {edge.q}'
        #             )

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.current = graph.start
        self.path = []
        self.path.append(self.current)

    def __str__(self) -> str:
        return f'Current: {self.current.name}'

    def move(self) -> None:
        bigger_q = self.current.get_bigger_q_action()
        if bigger_q == DEFAULT_Q:
            action_generated = int(random.random() * len(self.current.edges))
        else:
            action_generated = self.current.get_best_edge_end_index()
            print(f'Action generated: {action_generated}')

        print(f'Action generated: {action_generated}')
        print(f'Current: {self.current}')
        for e in self.current.edges:
            print(f'Edge: {e.start.name} -> {e.end.name} | Q: {e.q}')
        self.path.append(self.current.edges[action_generated].end)
        self.current = self.path[-1]
        self.update_q()

        if self.current == self.graph.goal:
            self.update_q()


def print_graph(g: Graph) -> None:
    for vertex in g.get_all_vertex():
        print(vertex)
        for edge in vertex.edges:
            print(f'\t{edge}')
        print('')


def debug(a: Agent, g: Graph, v: list):
    print('Start: ' + a.path[0].name)
    print('Goal: ' + a.path[-1].name)

    print('Vertex:')
    for vertex in v:
        print(vertex)

    print('Path:')
    for vertex in a.path:
        print(vertex.name + ' -> ', end='')

    print()

    print('Edges:')
    for edge in g.get_all_edges():
        print(edge)


def main():
    g = Graph()
    # extract the data of vertices.csv
    _file = open('vertices.csv', 'r', encoding='utf-8')
    for line in _file:
        line = line.split(',')
        g.add_vertex(Vertex(int(line[0]), str(line[0])))

    _file.close()

    _file = open('arestas.csv', 'r', encoding='utf-8-sig')
    for line in _file:
        line = line.split(',')
        g.add_edge(str(int(line[0])+1), str(int(line[1])+1), int(line[2]))

    _file.close()

    g.set_start('1')
    g.set_goal('21')

    print_graph(g)
    g.define_reward(10.0, g.goal)
    a = Agent(g)

    # v = g.get_all_vertex()
    # times = 5
    # for i in range(times):

    #     a.graph.set_start(random.random() * len(g.vertex))
    #     print('-=' * 15 + f'Iteração {i + 1}' + '-=' * 15)
    #     print('Current: ' + a.current.name)
    #     while a.current != g.goal:
    #         a.move()

    #     a.current = g.start
    #     a.path = []
    #     a.path.append(a.current)

    # # # debug(a, g, v)
    # print_graph(g)


if __name__ == "__main__":
    main()
