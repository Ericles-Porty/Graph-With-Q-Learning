import time
import random

FACTOR = 0.8


def calc_q(factor: float, reward: float, max_q: float):
    return reward + factor * max_q


class Edge:

    def __init__(self, start, end, weight: int, q=0.0) -> None:
        self.start = start
        self.end = end
        self.weight = weight
        self.q = q

    def __str__(self) -> str:
        return f'{self.start.name} -> {self.end.name} ({self.weight})'


class Vertex:

    def __init__(self, id: int, name: str, r=0) -> None:
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

    def get_max_action(self) -> float:
        bigger_q = 0
        for edge in self.edges:
            if edge.q > bigger_q:
                bigger_q = edge.q
        return bigger_q

    def get_best_edge_destiny(self):
        edge_destiny = self.edges[0]
        for edge in self.edges:
            if edge.q > edge_destiny.q:
                edge_destiny = edge
        return edge_destiny


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

        raise Exception(f'Vertex with name {name} not found')

    def set_goal(self, goal: str) -> None:
        self.goal = self.get_vertex_by_name(goal)

    def set_start(self, start: str) -> None:
        self.start = self.get_vertex_by_name(start)

    def add_edge(self, start: str, end: str, weight: int) -> None:
        start = self.get_vertex_by_name(start)
        end = self.get_vertex_by_name(end)
        start.add_edge(Edge(start, end, weight))
        end.add_edge(Edge(end, start, weight))


class Agent:

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.current = graph.start
        self.path = []
        self.path.append(self.current)

    def __str__(self) -> str:
        return f'Current: {self.current.name}'

    def move(self) -> None:
        action_generated = int(random.random() * len(self.current.edges))

        self.path.append(self.current.edges[action_generated].end)
        self.current = self.path[-1]

        if self.current == self.graph.goal:
            return


def main():
    g = Graph()

    g.add_vertex(Vertex(1, 'A'))
    g.add_vertex(Vertex(2, 'B'))
    g.add_vertex(Vertex(3, 'C'))
    g.add_vertex(Vertex(4, 'D'))
    g.add_vertex(Vertex(5, 'E'))
    g.add_vertex(Vertex(6, 'F'))

    g.add_edge('A', 'F', 1)
    g.add_edge('A', 'E', 1)
    g.add_edge('A', 'C', 1)
    g.add_edge('C', 'D', 1)
    g.add_edge('C', 'E', 1)
    g.add_edge('B', 'F', 1)
    g.add_edge('B', 'E', 1)
    g.add_edge('B', 'E', 1)

    g.set_start('A')
    g.set_goal('D')

    a = Agent(g)

    # print(g.get_all_vertex_names())

    # for edge in g.get_all_edges_names():
    #     print(edge)

    while a.current != g.goal:
        a.move()

    print('Start: ' + a.path[0].name)
    print('Goal: ' + a.path[-1].name)
    print('Path:')
    for vertex in a.path:
        print(vertex.name + ' -> ', end='')
    print('Goal')


if __name__ == "__main__":
    main()
