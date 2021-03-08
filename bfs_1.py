from manim import *
from util import LinedCode, AnimQueue, GridNetwork


class BFS(Scene):
    def construct(self):
        # Illustration of the BFS algorithm in a 3x3 grid: Check after dequeue
        # self.time = 0
        # self.add_sound("Le_grand_cahier.mp3")
        bfs1 = Tex(
            "BFS: Check After Dequeue." + "\\\\",
            r"When a node reaches the head of the queue for the first" + "\\\\",
            r"time, we enqueue all of its neighbors. Then, we dequeue" + "\\\\",
            r"that node and add it to the BFS solution. If we have seen" + "\\\\",
            r"the node already, we omit it."
        ).scale(0.9)
        self.play(Write(bfs1), run_time=10.0)
        self.wait(3)
        self.clear()

        bfs1_code = LinedCode([
            "q = Queue()",
            "BFS = list()",
            "q.add(0)",
            "while q not empty:",
            "  head = q.pop()",
            "  if head not in BFS:",
            "    for n in neighbors(head):",
            "      q.add(n)",
            "    BFS.append(head)"
        ], self)
        for c in bfs1_code.code_tex:
            self.add(c)

        grid = GridNetwork(3, 3)
        for e in grid.edges():
            self.add(grid.edges[e]["line"])
        for n in grid.nodes():
            self.add(grid.nodes[n]["circle"])
            self.bring_to_front(grid.nodes[n]["label"])
            self.add(grid.nodes[n]["label"])
        self.wait(2)

        # Important coordinates
        q_coord = UP * 3 + LEFT * 5
        h_coord = q_coord + DOWN
        bfs_coord = h_coord + DOWN

        q_label = Tex("Queue:").set_color(GREEN).move_to(q_coord + 1.2 * LEFT)
        self.play(Write(q_label))
        h_label = Tex("Head:").set_color(BLUE).move_to(h_coord + 1.1 * LEFT)
        self.play(Write(h_label))
        bfs_label = Tex("BFS:").set_color(YELLOW).move_to(bfs_coord + 1 * LEFT)
        self.play(Write(bfs_label))

        a_q = AnimQueue(q_coord, self)
        a_bfs = AnimQueue(bfs_coord, self)
        bfs1_code.highlight([0])
        bfs1_code.highlight([1])

        q = []
        bfs = []
        cur = (0, 0)

        bfs1_code.highlight([2])
        q.append(cur)
        grid.nodes[cur]["circle"].set_color(GREEN)
        self.play(ApplyMethod(grid.nodes[cur]["circle"].scale, 1.1), run_time=0.5)
        self.play(ApplyMethod(grid.nodes[cur]["circle"].scale, 1.0 / 1.1), run_time=0.5)
        a_q.enqueue(grid.nodes[cur]["id"])

        bfs1_code.highlight([3])
        h = None
        while len(q) > 0:
            bfs1_code.highlight([4])
            cur = q[0]
            q = q[1:]
            if h is not None:
                self.play(FadeOut(h))
                self.remove(h)
            h = a_q.dequeue(lambda x: self.play(ApplyMethod(x.move_to, h_coord)))
            bfs1_code.highlight([5])
            if cur not in bfs:
                bfs1_code.highlight([6])
                self.play(ApplyMethod(grid.nodes[cur]["circle"].set_color, BLUE), run_time=0.5)
                for n in grid.neighbors(cur):
                    line = Line(*grid.get_line_coords(cur, n)).set_color(BLUE).set_stroke(width=7)
                    if n not in bfs and n not in q:
                        line.set_color(YELLOW)
                    self.play(ShowCreation(line), run_time=0.5)
                    if n not in bfs and n not in q:
                        grid.edges[(cur, n)]["line"].set_color(YELLOW)
                    if n not in bfs and n not in q:
                        grid.nodes[n]["circle"].set_color(GREEN)
                    self.play(ApplyMethod(grid.nodes[n]["circle"].scale, 1.1), run_time=0.5)
                    q.append(n)
                    bfs1_code.highlight([7])
                    a_q.enqueue(grid.nodes[n]["id"])
                    self.play(ApplyMethod(grid.nodes[n]["circle"].scale, 1.0 / 1.1), run_time=0.5)
                    self.play(FadeOut(line))
                    bfs1_code.highlight([6])
                bfs1_code.highlight([8])
                bfs.append(cur)
                a_bfs.enqueue_anim_elem(h)
                h = None
                self.play(ApplyMethod(grid.nodes[cur]["circle"].set_color, YELLOW), run_time=0.5)
            bfs1_code.highlight([3])
        #
        bfs1_code.highlight([])
        if h is not None:
            self.play(FadeOut(h))
            self.remove(h)
        self.wait(2)
        self.clear()
        self.wait(3)
