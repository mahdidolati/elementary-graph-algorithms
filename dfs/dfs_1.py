from manim import *
from util.util import LinedCode, AnimQueue, GridNetwork


class Dfs(Scene):
    def __init__(self, *args, **kwargs):
        super(Dfs, self).__init__(*args, **kwargs)
        self.dfs_code = None
        self.grid = None
        self.a_mark = None
        self.a_dfs = None
        self.mark = []
        self.dfs = []
        # Important coordinates
        self.m_coord = UP * 3 + LEFT * 4.7
        self.c_coord = self.m_coord + DOWN
        self.dfs_coord = self.c_coord + DOWN

    def dfs_visit(self, cur, prev_head, prev_head_id, prev_line):
        self.dfs_code.highlight([3])
        n_eq = Tex("$%s$" % str(self.grid.nodes[cur]["id"]))
        n_eq.move_to(self.c_coord)
        anim1 = [ApplyMethod(self.grid.nodes[cur]["circle"].set_color, BLUE)]
        anim2 = [ApplyMethod(self.grid.nodes[cur]["circle"].scale, 1.0 / 1.1), Write(n_eq)]
        if prev_head is not None:
            anim1.extend([ApplyMethod(self.grid.nodes[prev_head_id]["circle"].set_color, GREEN),
                          ApplyMethod(self.grid.nodes[cur]["circle"].set_color, BLUE),
                          FadeOut(prev_head)])
            anim2.extend([FadeOut(prev_line)])

        self.play(*anim1)
        self.play(*anim2)

        self.dfs_code.highlight([4])
        self.mark.append(cur)
        self.a_mark.enqueue(self.grid.nodes[cur]["id"])

        self.dfs_code.highlight([5])
        for n in self.grid.neighbors(cur):
            line = Line(*self.grid.get_line_coords(cur, n)).set_stroke(width=7)
            if n not in self.mark:
                line.set_color(YELLOW)
                self.play(ShowCreation(line), run_time=0.5)
                self.grid.edges[(cur, n)]["line"].set_color(YELLOW)
                self.play(ApplyMethod(self.grid.nodes[n]["circle"].scale, 1.1), run_time=0.25)
                self.dfs_code.highlight([6])
                self.dfs_code.highlight([7])
                self.dfs_visit(n, n_eq, cur, line)
                self.play(FadeIn(n_eq))
            else:
                line.set_color(BLUE)
                self.play(ShowCreation(line), run_time=0.5)
                self.play(ApplyMethod(self.grid.nodes[n]["circle"].scale, 1.1), run_time=0.25)
                self.dfs_code.highlight([6])
                self.play(ApplyMethod(self.grid.nodes[n]["circle"].scale, 1.0 / 1.1), run_time=0.5)
                self.play(FadeOut(line))
            self.dfs_code.highlight([5])

        self.dfs_code.highlight([8])
        self.play(ApplyMethod(self.grid.nodes[cur]["circle"].set_color, YELLOW))
        self.a_dfs.enqueue_anim_elem(n_eq)

    def construct(self):
        # Illustration of the DFS algorithm in a 3x3 grid: Recursive
        bfs1 = Tex(
            "DFS: Recursive." + "\\\\",
            r"The recursive function marks the input node at the" + "\\\\",
            r"beginning. Then, it calls itself for all unmarked neighbors." + "\\\\",
            r"When all recursive calls return, the method adds the input" + "\\\\",
            r"to the DFS."
        ).scale(0.9)
        self.play(Write(bfs1), run_time=10.0)
        self.wait(3)
        self.clear()

        self.dfs_code = LinedCode([
            "cur = 1",
            "dfs(cur)",
            "",
            "def dfs(cur):",
            "  mark cur",
            "  for n in neighbors(cur):",
            "    if n is not marked:",
            "      dfs(n)",
            "  add cur to DFS",
        ], self)
        for c in self.dfs_code.code_tex:
            self.add(c)

        self.grid = GridNetwork(3, 3)
        for e in self.grid.edges():
            self.add(self.grid.edges[e]["line"])
        for n in self.grid.nodes():
            self.add(self.grid.nodes[n]["circle"])
            self.bring_to_front(self.grid.nodes[n]["label"])
            self.add(self.grid.nodes[n]["label"])
        self.wait(2)

        q_label = Tex("Marked:").set_color(GREEN).move_to(self.m_coord + 1.2 * LEFT)
        self.play(Write(q_label))
        h_label = Tex("Current:").set_color(BLUE).move_to(self.c_coord + 1.3 * LEFT)
        self.play(Write(h_label))
        bfs_label = Tex("DFS:").set_color(YELLOW).move_to(self.dfs_coord + 1 * LEFT)
        self.play(Write(bfs_label))

        self.a_mark = AnimQueue(self.m_coord, self)
        self.a_dfs = AnimQueue(self.dfs_coord, self)
        self.dfs_code.highlight([0])
        self.dfs_code.highlight([1])

        cur = (0, 0)
        self.play(ApplyMethod(self.grid.nodes[cur]["circle"].scale, 1.1), run_time=0.25)
        self.dfs_visit(cur, None, None, None)
        self.dfs_code.highlight([])
        self.wait(3.0)
