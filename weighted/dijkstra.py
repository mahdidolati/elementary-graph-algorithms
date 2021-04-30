from manim import *
from util.util import LinedCode, GridNetwork, AnimPriorityQueue


class Dijkstra(Scene):
    def __init__(self, *args, **kwargs):
        super(Dijkstra, self).__init__(*args, **kwargs)

    def construct(self):
        bfs1 = Tex(
            "Dijkstra's single-source shortest paths algorithm:" + "\\\\",
            r"The algorithm selects the unmarked node with the shortest" + "\\\\",
            r"distance from the source and uses it to compute shorter" + "\\\\",
            r"paths to that node's neighbors. Then, the selected node" + "\\\\",
            r"is marked."
        ).scale(0.9)
        self.play(Write(bfs1), run_time=10.0)
        self.wait(3)
        self.clear()

        code = LinedCode([
            "q = PriorityQueue().add($v_0$, $0$)",
            "while q is not empty:",
            "  head, val = q.get()",
            "  if head is not marked:",
            "    for n in neighbors(head):",
            "      if dist[n] > val + w(head, n)",
            "        dist[n] = val + w(head, n)",
            "        q.add(n, dist[n])",
            "    Mark head"
        ], self)
        for c in code.code_tex:
            self.add(c.shift(0.1*DOWN))

        grid = GridNetwork(".\\util\\grid_topo", {"shift": 2*RIGHT+0.2*DOWN, "weighted": True})
        for e in grid.edges():
            self.add(grid.edges[e]["line"])
            self.add(grid.edges[e]["w_label"])
        for n in grid.nodes():
            self.add(grid.nodes[n]["circle"])
            self.bring_to_front(grid.nodes[n]["label"])
            self.add(grid.nodes[n]["label"])

        self.wait(3.0)

        # Important coordinates
        q_coord = UP * 3.6 + LEFT * 5
        h_coord = q_coord + DOWN * 0.9
        nodes_coord = h_coord + DOWN * 0.9
        dist_coord = nodes_coord + DOWN * 0.9

        q_label = Tex("Queue:").set_color(GREEN).move_to(q_coord + 1.2 * LEFT)
        self.play(Write(q_label))
        h_label = Tex("Head:").set_color(BLUE).move_to(h_coord + 1.1 * LEFT)
        self.play(Write(h_label))
        bfs_label = Tex("Nodes:").set_color(YELLOW).move_to(nodes_coord + 1.2 * LEFT)
        self.play(Write(bfs_label))
        bfs_label = Tex("Dist:").set_color(YELLOW).move_to(dist_coord + 1 * LEFT)
        self.play(Write(bfs_label))

        a_nodes = []
        a_dist = []
        for n in grid.nodes():
            l1 = Tex("$v_%d$" % grid.nodes[n]["id"]).move_to(nodes_coord + grid.nodes[n]["id"] * RIGHT)
            if grid.nodes[n]["id"] == 0:
                l2 = Tex("$0$").move_to(dist_coord + grid.nodes[n]["id"] * RIGHT)
            else:
                l2 = Tex("$\infty$").move_to(dist_coord + grid.nodes[n]["id"] * RIGHT)
            a_nodes.append(l1)
            a_dist.append(l2)

        self.play(AnimationGroup(*[Write(x) for x in a_nodes], lag_ratio=0.2),
                  AnimationGroup(*[Write(x) for x in a_dist], lag_ratio=0.2))

        code.highlight([0])
        grid.nodes[(0, 0)]["circle"].set_color(GREEN)
        self.play(ApplyMethod(grid.nodes[(0, 0)]["circle"].scale, 1.1), run_time=0.25)
        q = AnimPriorityQueue(q_coord, self)
        q.enqueue((0, 0), "v_%d" % grid.nodes[(0, 0)]["id"], 0)
        self.play(ApplyMethod(grid.nodes[(0, 0)]["circle"].scale, 1.0 / 1.1), run_time=0.5)

        a = Arrow(q_coord + 1.1 * RIGHT + 0.2 * UP, q_coord + 0.1 * RIGHT + 0.2 * UP)
        self.add(a)
        t = Tex("Node").scale(0.5).move_to(q_coord + 1.3 * RIGHT + 0.2 * UP)
        self.play(Write(t))
        self.wait(1)
        self.remove(t)
        self.play(ApplyMethod(a.shift, 0.35 * DOWN))
        t = Tex("Distance from the source serves as the" + "\\\\"
                "precedence in the priority queue").scale(0.5).move_to(q_coord + 3.1 * RIGHT + 0.3 * DOWN)
        self.play(Write(t))
        self.wait(1)
        self.remove(t)
        self.remove(a)

        dist = {(0, 0): 0}
        visited = []
        parent = {}
        h = None
        code.highlight([1])

        def pop_anim(x):
            if x.id in visited:
                self.play(ApplyMethod(x.n_eq.shift, DOWN), run_time=0.75)
            elif x.id not in parent:
                self.play(ApplyMethod(x.n_eq.shift, DOWN),
                          ApplyMethod(grid.nodes[x.id]["circle"].set_color, BLUE),
                          run_time=0.75)
            else:
                self.play(ApplyMethod(x.n_eq.shift, DOWN),
                          ApplyMethod(grid.nodes[x.id]["circle"].set_color, BLUE),
                          ApplyMethod(grid.edges[(x.id, parent[x.id])]["line"].set_color, YELLOW),
                          run_time=0.75)

        while not q.is_empty():
            code.highlight([2])
            if h is not None:
                self.play(FadeOut(h.n_eq))

            h = q.dequeue(pop_anim)

            code.highlight([3])
            if h.id not in visited:
                for n in grid.neighbors(h.id):
                    code.highlight([4])
                    r1, r2 = grid.get_line_coords(h.id, n)
                    line = Line(r1, r2).set_stroke(width=7).set_color(BLUE)
                    self.add(Circle(radius=0.05).move_to(r1).set_fill(PINK, opacity=1.0))
                    self.play(
                            ShowCreation(line),
                            ApplyMethod(grid.edges[(h.id, n)]["w_label"].set_color, BLUE),
                            run_time=0.5
                    )
                    if n not in visited:
                        grid.nodes[n]["circle"].set_color(GREEN)
                    self.play(ApplyMethod(grid.nodes[n]["circle"].scale, 1.1), run_time=0.25)
                    code.highlight([5])
                    if n not in dist or h.priority + grid.edges[(h.id, n)]["w"] < dist[n]:
                        code.highlight([6])
                        dist[n] = h.priority + grid.edges[(h.id, n)]["w"]
                        parent[n] = h.id
                        self.play(FadeOut(a_dist[grid.nodes[n]["id"]]))
                        self.remove(a_dist[grid.nodes[n]["id"]])
                        l2 = Tex("$%d$" % dist[n]).move_to(dist_coord + grid.nodes[n]["id"] * RIGHT)
                        self.play(Write(l2))
                        a_dist[grid.nodes[n]["id"]] = l2
                        code.highlight([7])
                        q.enqueue(n, "v_%d" % grid.nodes[n]["id"], dist[n])
                    self.play(ApplyMethod(grid.nodes[n]["circle"].scale, 1.0 / 1.1), run_time=0.5)
                    self.play(
                            FadeOut(line),
                            ApplyMethod(grid.edges[(h.id, n)]["w_label"].set_color, WHITE)
                    )

                code.highlight([8])
                visited.append(h.id)
                self.play(ApplyMethod(grid.nodes[h.id]["circle"].set_color, YELLOW))

            code.highlight([1])

        self.play(FadeOut(h.n_eq))
        code.highlight([])
        self.wait(3)
        self.clear()
        self.wait(3)
