import time
import random
import matplotlib.pyplot as plt

ALPHA = 0.3  # Taxa de aprendizado
GAMMA = 0.7  # Fator de desconto
EPSILON = 0.9  # Taxa de exploração

DEFAULT_Q = 0.0


def generate_plot(dq: list) -> None:
    plt.plot(dq)
    plt.title("Gráfico de convergência do aprendizado")
    plt.ylabel("Delta Q Total")
    plt.xlabel("Episódios")
    plt.show()


def get_delta_q(actual_q: float, reward: float, max_q: float) -> float:
    return ALPHA * (reward + GAMMA * max_q - actual_q)


def is_converged(dq: list) -> bool:
    # Verifica se os últimos 4 valores de delta q são iguais
    if len(dq) > 4:
        return (dq[-1] == dq[-2] and dq[-1] == dq[-3] and dq[-1] == dq[-4])


def save_delta_q_list(dq: list) -> None:
    _file = open("delta_q.csv", "w", encoding="utf-8")
    for i in dq:
        _file.write(f"{i}\n")
    _file.close()


class Edge:

    def __init__(self, start, end, weight: int, q=DEFAULT_Q) -> None:
        self.start = start
        self.end = end
        self.weight = weight
        self.q = q

    def __str__(self) -> str:
        return f"{self.start.name} -> {self.end.name} ({self.weight} - {self.q})"


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

    def get_vertex_by_name(self, name: str) -> "Vertex":
        for edge in self.edges:
            if edge.end.name == name:
                return edge.end
        return None

    def get_bigger_q_action(self) -> float:
        bigger_q = DEFAULT_Q
        for edge in self.edges:
            if edge.q > bigger_q:
                bigger_q = edge.q
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
        return f"Vertex: {self.name} | R={self.r}"


class Graph:

    def __init__(self) -> None:
        self.vertex = []
        self.start = None
        self.goal = None

    def read_csv(self) -> None:
        _file = open("vertices.csv", "r", encoding="utf-8")
        for line in _file:
            line = line.split(",")
            self.add_vertex(Vertex(int(line[0]), str(line[0])))

        _file.close()

        _file = open("arestas.csv", "r", encoding="utf-8-sig")
        for line in _file:
            line = line.split(",")
            self.add_edge(str(line[0]), str(line[1]), int(line[2]))

        _file.close()

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
                edges.append(f"{edge.start.name} -> {edge.end.name}")
        return edges

    def add_vertex(self, vertex: Vertex) -> None:
        self.vertex.append(vertex)

    def get_vertex_by_name(self, name: str) -> Vertex:
        for vertex in self.vertex:
            if vertex.name == name:
                return vertex
        raise Exception(f"Vertex with name {name} not found")

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

    def read_table_q(self) -> None:
        try:
            _file = open("table_q.csv", "r", encoding="utf-8-sig")
            for line in _file:
                line = line.split(",")
                q = float(line[2])
                start = self.get_vertex_by_name(line[0])
                end = self.get_vertex_by_name(line[1])
                for edge in start.edges:
                    if edge.end == end:
                        edge.q = q

            _file.close()
        except FileNotFoundError:
            print("File not found")
            option = input("Do you want to run without table_q? (y/n) ")
            if option == "y" or option == "Y":
                return
            else:
                exit(1)


class Agent:

    def __init__(self, graph: Graph, delta_q_total=0.0) -> None:
        self.graph = graph
        self.current = graph.start
        self.path = []
        self.epoch = 0
        self.path.append(self.current)
        self.delta_q_total = delta_q_total
        self.list_delta_q = [0]
        self.converged = False

    def __str__(self) -> str:
        return f"Current: {self.current.name}"

    def reset_agent(self) -> None:
        self.current = self.graph.get_vertex_by_name(
            str(int(random.random() * len(self.graph.vertex))))
        self.path = []
        self.path.append(self.current)

    def update_q(self) -> None:
        has_change = False
        if len(self.path) > 1:
            last_vertex = self.graph.get_vertex_by_name(self.path[-2].name)
            for edge in last_vertex.edges:
                if edge.end == self.current:
                    delta_q = get_delta_q(edge.q, self.current.r,
                                          self.current.get_bigger_q_action())
                    self.delta_q_total += delta_q
                    edge.q = edge.q + delta_q
                    if delta_q != 0:
                        has_change = True

            self.epoch += 1

            # if self.epoch % 500 == 0:
            if has_change:
                # delta_q_total_formatted = float("{:.6f}".format(
                #     self.delta_q_total))
                # self.list_delta_q.append(delta_q_total_formatted)
                self.list_delta_q.append(self.delta_q_total)

            if is_converged(self.list_delta_q):
                self.converged = True
                save_delta_q_list(self.list_delta_q)
                generate_plot(self.list_delta_q)

    def move(self) -> None:
        random_value = random.random()
        # Tem uma chance de EPSILON de ir para melhor ação
        if random_value < EPSILON:
            bigger_q = self.current.get_bigger_q_action()
            if bigger_q != DEFAULT_Q:
                action_generated = self.current.get_best_edge_end_index()
            else:
                action_generated = int(random.random() *
                                       len(self.current.edges))
        else:
            action_generated = int(random.random() * len(self.current.edges))

        # Adiciona o vértice escolhido no caminho
        self.path.append(self.current.edges[action_generated].end)
        # O vértice atual é o último vértice escolhido do caminho
        self.current = self.path[-1]
        self.update_q()

    def train(self) -> None:
        while not self.converged:
            while self.current != self.graph.goal:
                self.move()

            # Limpa o caminho do agente e o coloca em um vértice aleatório
            self.reset_agent()

        print(self.list_delta_q)

    def test(self, start_name) -> list:
        path = []
        start = self.graph.get_vertex_by_name(start_name)
        self.current = start

        path.append(self.current)

        while self.current != self.graph.goal:
            action_generated = self.current.get_best_edge_end_index()

            path.append(self.current.edges[action_generated].end)

            self.path.append(self.current.edges[action_generated].end)
            self.current = self.path[-1]

        return path


def print_graph(g: Graph) -> None:
    for vertex in g.get_all_vertex():
        print(vertex)
        for edge in vertex.edges:
            print(f"\t{edge}")
        print("")


def save_table_q(g: Graph) -> None:
    _file = open("table_q.csv", "w", encoding="utf-8")
    for edge in g.get_all_edges():
        _file.write(f"{edge.start.name},{edge.end.name},{edge.q}\n")
    _file.close()


def debug(a: Agent, g: Graph, v: list):
    print("Start: " + a.path[0].name)
    print("Goal: " + a.path[-1].name)

    print("Vertex:")
    for vertex in v:
        print(vertex)

    print("Path:")
    for vertex in a.path:
        print(vertex.name + " -> ", end="")

    print()

    print("Edges:")
    for edge in g.get_all_edges():
        print(edge)


def main():
    g = Graph()

    # extract the data of vertices.csv and arestas.csv
    g.read_csv()

    # define the start and goal
    g.set_start("1")
    g.set_goal("21")
    g.define_reward(1.0, g.goal)

    # Read table q
    # g.read_table_q()

    a = Agent(g)

    a.train()

    save_table_q(g)

    # print_graph(g)

    # Test path
    # path = a.test(start_name="40")

    # print("Path:")
    # for node in path:
    #     print(node.name + " -> ", end="")

    print()
    print("Contador total delta q: " + str(a.delta_q_total))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
TODO: VERIFICAR CONVERGÊNCIA
TODO: APLICAR ATRIBUTOS DE DISTANCIA
"""
