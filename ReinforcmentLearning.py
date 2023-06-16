import os
import time
import random
import matplotlib.pyplot as plt

ALPHA = 0.3  # Taxa de aprendizado
GAMMA = 0.7  # Fator de desconto
EPSILON = 0.9  # Taxa de exploração
WEIGHT_DISCOUNT = 5  # Desconto do peso da aresta
DEFAULT_Q = 0.0


def generate_plot(dq: list) -> None:
    plt.plot(dq)
    plt.title("Gráfico de convergência do aprendizado")
    plt.ylabel("Delta Q Total")
    plt.xlabel("Episódios")
    plt.show()


def get_delta_q(actual_q: float, reward: float, max_q: float,
                weight: float) -> float:
    return ALPHA * (1 / weight) * ((reward + GAMMA * max_q - actual_q))


def get_delta_q_sarsa(actual_q: float, reward: float, next_q: float,
                      weight: float) -> float:
    return ALPHA * (reward + GAMMA * next_q - actual_q)
    # return ALPHA * (1/weight) (reward + GAMMA * next_q - actual_q)


def belman_equation(actual_vertex, next_vertex) -> float:
    return actual_vertex.r + GAMMA * next_vertex.get_bigger_q_action()


def is_converged(delta_q_list: list, match_numbers: int = 5) -> bool:
    # verify if the last 5 values of delta q are equal
    if len(delta_q_list) > match_numbers:
        for i in range(1, match_numbers):
            # print (delta_q_list[-i], end=" ")
            if delta_q_list[-1] != delta_q_list[-i]:
                # print()
                return False
        # print()
        return True


def save_delta_q_list(dq: list) -> None:
    _file = open("delta_q.csv", "w", encoding="utf-8")
    for i in dq:
        _file.write(f"{i}\n")
    _file.close()


def save_path(path: list) -> None:
    _file = open("path.csv", "w", encoding="utf-8")
    p = [str(i) for i in path]
    _file.write(",".join(p))
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

    def __init__(self, id: int, name: str, category: str, r=0.0) -> None:
        self.id = id
        self.name = name
        self.edges = []
        self.category = category
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

    def get_best_action_index(self) -> int:
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
            self.add_vertex(Vertex(int(line[0]), str(line[1]), str(line[4])))

        _file.close()

        _file = open("arestas.csv", "r", encoding="utf-8-sig")
        for line in _file:
            line = line.split(",")
            self.add_edge(str(line[0]), str(line[1]), int(line[3]))

        _file.close()

    def get_all_vertex(self) -> list():
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

    def get_vertex_by_id(self, id: str) -> Vertex:
        for vertex in self.vertex:
            if str(vertex.id) == str(id):
                return vertex
        raise Exception(f"Vertex with id {id} not found")

    def get_vertex_by_name(self, name: str) -> Vertex:
        for vertex in self.vertex:
            if vertex.name == name:
                return vertex
        raise Exception(f"Vertex with name {name} not found")

    def set_goal(self, goal: str) -> None:
        self.goal = self.get_vertex_by_id(goal)

    def set_start(self, start: str) -> None:
        self.start = self.get_vertex_by_id(start)

    def add_edge(self, start: str, end: str, weight: int) -> None:
        start = self.get_vertex_by_id(start)
        end = self.get_vertex_by_id(end)
        start.add_edge(Edge(start, end, weight))
        end.add_edge(Edge(end, start, weight))

    def define_reward(self, reward: float, vertex: Vertex) -> None:
        vertex.r = reward

    def read_table_q(self, table_name: str = "table_q.csv") -> None:
        table_name = "table_q/" + table_name
        try:
            _file = open(table_name, "r", encoding="utf-8-sig")
            for line in _file:
                line = line.split(",")

                start = self.get_vertex_by_id(line[0])
                end = self.get_vertex_by_id(line[1])
                q = float(line[2])

                for edge in start.edges:
                    if edge.end == end:
                        edge.q = q

            _file.close()
        except FileNotFoundError:
            return
            # option = input("Do you want to run without table_q? (y/n) ")
            # if option == "y" or option == "Y":
            #     return
            # else:
            #     exit(1)


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

    def get_random_action(self) -> int:
        return int(random.random() * len(self.current.edges))

    def random_policy(self) -> int:
        return int(self.get_random_action())

    def greedy_policy(self) -> int:
        # Has a chance of EPSILON to exploit
        if random.random() > EPSILON:
            if self.current.get_bigger_q_action() != DEFAULT_Q:
                return self.current.get_best_action_index()
        # Otherwise, explore
        return self.get_random_action()

    def greater_policy(self) -> int:
        return self.current.get_best_action_index()

    def reset_agent(self) -> None:
        random_vertex = self.graph.get_vertex_by_id(
            str(int(random.random() * len(self.graph.vertex))))

        self.current = random_vertex
        self.path.clear()
        self.path.append(self.current)

    def verify_convergence(self) -> bool:
        if is_converged(self.list_delta_q):
            self.converged = True
            return True
        return False

    def train(self) -> None:
        while not self.converged:
            while self.current != self.graph.goal:
                self.move()

            self.reset_agent()

    def generate_path_interest(self, start_id, category) -> list:
        path = []
        interest_vertexes = []

        # Get all vertexes with the same category
        for vertex in self.graph.get_all_vertex():
            if vertex.category == category:
                interest_vertexes.append(vertex)
        print ("Interest vertexes:", end=" ")
        print([i.name for i in interest_vertexes])

        list_of_tables = []

        # Get all tables of the interest vertexes
        for vertex in interest_vertexes:
            _file = open(f"table_q/table_q_{vertex.id}.csv", "r", encoding="utf-8-sig")
            table = []
            for line in _file:
                line = line.split(",")
                table.append(line)
            list_of_tables.append(table)
        
        start = self.graph.get_vertex_by_id(start_id)
        self.current = start
        path.append(self.current)
        # while list of interest vertexes is not empty
        while len(interest_vertexes) > 0:
            bigger_q = 0
            index = 0
            for i in range(len(list_of_tables)):
                if float(list_of_tables[i][self.current.id][2]) > bigger_q:
                    bigger_q = float(list_of_tables[i][self.current.id][2])
                    index = i

            # while current vertex is not the interest vertex
            while self.current != interest_vertexes[index]:
                self.current = self.graph.get_vertex_by_id(list_of_tables[index][self.current.id][1])
                path.append(self.current)
            
            list_of_tables.pop(index)
            interest_vertexes.pop(index)

        # at the end, append the goal path
        while self.current != self.graph.goal:  
            action_generated = self.current.get_best_action_index()
            self.current = self.current.edges[action_generated].end
            path.append(self.current)

        print ("Path: ", end=" ")
        print([p.id for p in path])
        return path

    def test(self, start_id) -> list:
        path = []
        start = self.graph.get_vertex_by_id(start_id)
        self.current = start

        path.append(self.current)

        while self.current != self.graph.goal:
            action_generated = self.current.get_best_action_index()

            path.append(self.current.edges[action_generated].end)

            self.path.append(self.current.edges[action_generated].end)
            self.current = self.path[-1]

        return path


#create a class QLearningAgent that implements Agent


class QLearningAgent(Agent):

    def __init__(self, graph: Graph, delta_q_total=0.0) -> None:
        super().__init__(graph, delta_q_total)

    def update_q_value(self, next_vertex) -> None:
        has_change = False

        for edge in self.current.edges:
            if edge.end == next_vertex:
                delta_q = get_delta_q(edge.q, next_vertex.r,
                                      next_vertex.get_bigger_q_action(),
                                      edge.weight)
                self.delta_q_total += delta_q
                edge.q = edge.q + delta_q
                if delta_q != 0:
                    has_change = True

        if has_change:
            self.list_delta_q.append(self.delta_q_total)

        self.epoch += 1
        if self.epoch % 5000 == 0:
            if is_converged(self.list_delta_q):
                self.converged = True
                # save_delta_q_list(self.list_delta_q)
                # generate_plot(self.list_delta_q)

    def move(self) -> None:
        action_generated = self.greedy_policy()
        chosen_vertex = self.current.edges[action_generated].end

        self.update_q_value(next_vertex=chosen_vertex)

        self.current = chosen_vertex
        self.path.append(self.current)


class SarsaAgent(Agent):

    def __init__(self, graph: Graph, delta_q_total=0.0) -> None:
        super().__init__(graph, delta_q_total)

    def update_q_value(self, next_vertex) -> None:
        has_change = False

        for edge in self.current.edges:
            if edge.end == next_vertex:

                old_current = self.current
                self.current = next_vertex
                next_action = self.greedy_policy()
                self.current = old_current

                next_edge = next_vertex.edges[next_action]

                delta_q = get_delta_q_sarsa(edge.q, next_vertex.r, next_edge.q,
                                            edge.weight)
                self.delta_q_total += delta_q
                edge.q = edge.q + delta_q
                if delta_q != 0:
                    has_change = True

        if has_change:
            self.list_delta_q.append(self.delta_q_total)

        self.epoch += 1
        # if self.epoch % 5000 == 0:
        #     if is_converged(self.list_delta_q):
        #         self.converged = True
        #         save_delta_q_list(self.list_delta_q)
        #         generate_plot(self.list_delta_q)

        if self.epoch == 500000:  # 300000
            self.converged = True
            save_delta_q_list(self.list_delta_q)

    def move(self) -> None:
        next_action = self.greedy_policy()
        next_vertex = self.current.edges[next_action].end

        self.update_q_value(next_vertex)

        self.current = next_vertex
        self.path.append(self.current)


def print_graph(g: Graph) -> None:
    for vertex in g.get_all_vertex():
        print(vertex)
        for edge in vertex.edges:
            print(f"\t{edge}")
        print("")


def save_table_q(g: Graph, file_name: str = "table_q.csv") -> None:
    if not os.path.exists("table_q"):
        os.mkdir("table_q")

    if file_name in os.listdir("table_q"):
        os.remove(f"table_q/{file_name}")
        # print(f"File {file_name} already exists. It was removed.")
    _file = open(f"table_q/{file_name}", "w", encoding="utf-8")

    # filter just the biggest q for each edge
    for vertex in g.get_all_vertex():
        bigger_q = DEFAULT_Q
        start = vertex
        end = vertex
        for edge in vertex.edges:
            if edge.q > bigger_q:
                bigger_q = edge.q
                start = edge.start
                end = edge.end

        _file.write(f"{start.id},{end.id},{bigger_q}\n")
    _file.close()


# create table q for every vertex
def full_run():
    g = Graph()
    g.read_csv()
    all_vertex = g.get_all_vertex()
    for vertex in all_vertex:
        print(
            f"{int(all_vertex.index(vertex) / len(all_vertex) * 100)}% - Running for vertex {vertex.name} - {vertex.id} of {len(all_vertex)} "
        )
        g = Graph()
        g.read_csv()
        g.set_start("1")
        g.set_goal(vertex.id)
        g.define_reward(10, g.goal)
        a = QLearningAgent(g)
        a.train()
        save_table_q(g, file_name=f"table_q_{vertex.id}.csv")


# create table_q.csv for only one vertex
def single_run(start_id, goal_name):
    g = Graph()
    g.read_csv()
    g.set_start(start_id)
    g.set_goal(goal_name)
    g.define_reward(10.0, g.goal)

    # a = QLearningAgent(g)
    a = SarsaAgent(g)

    a.train()

    save_table_q(g, file_name=f"table_q_{goal_name}.csv")
    path = a.generate_path_interest(start_id=start_id, category="Tech")
    save_path([vertex.id for vertex in path])


def main():
    full_run() # generate table_q for every vertex

    single_run(start_id="0", goal_name="17")

    print("Finished!")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
TODO: MOBILE
"""