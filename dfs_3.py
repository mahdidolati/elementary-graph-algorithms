from manim import *
from util import LinedCode, AnimQueue, GridNetwork, AnimStack


class DFS(Scene):
    def __init__(self, *args, **kwargs):
        super(DFS, self).__init__(*args, **kwargs)
        self.dfs_code = None
        self.grid = None
        self.a_mark = None
        self.a_dfs = None
        self.mark = []
        self.dfs = []
        # Important coordinates
        self.s_coord = UP * 3 + LEFT * 4.7
        self.t_coord = self.s_coord + DOWN
        self.dfs_coord = self.t_coord + DOWN

    def construct(self):
        # Illustration of the DFS algorithm in a 3x3 grid: Recursive
        bfs1 = Tex(
            "DFS: Stack-based, pop before descendants." + "\\\\",
            r"The algorithm pushes all the neighbors of nodes that" + "\\\\",
            r"reach the top of the stack for the first. It also adds" + "\\\\",
            r"those nodes to the DFS. The algorithm omits nodes that" + "\\\\",
            r"reappear at the top."
        ).scale(0.9)
        self.play(Write(bfs1), run_time=10.0)
        self.wait(3)
        self.clear()

        rev_neigh = Tex(
            "We visit the neighbors in a" + "\\\\",
            r"reversed order to get a similar" + "\\\\",
            r"result as other versions."
        ).scale(0.6).shift(5*RIGHT + 1.5*DOWN).set_color(BLUE)

        self.dfs_code = LinedCode([
            "s = Stack().push(0)",
            "while s not empty:",
            "  top = s.pop()",
            "  if top not in DFS:",
            "    for n in reversed(neighbors(top)):",
            "      s.push(n)",
            "    DFS.push(top)",
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

        q_label = Tex("Stack:").set_color(GREEN).move_to(self.s_coord + 1.1 * LEFT)
        self.play(Write(q_label))
        h_label = Tex("Top:").set_color(BLUE).move_to(self.t_coord + 1.0 * LEFT)
        self.play(Write(h_label))
        bfs_label = Tex("DFS:").set_color(YELLOW).move_to(self.dfs_coord + 1.0 * LEFT)
        self.play(Write(bfs_label))

        self.a_mark = AnimStack(self.s_coord, self)
        self.a_dfs = AnimStack(self.dfs_coord, self)

        cur = (0, 0)
        q = [cur]
        parent = {}
        self.dfs_code.highlight([0])
        self.a_mark.push(self.grid.nodes[cur]["id"])
        self.grid.nodes[cur]["circle"].set_color(GREEN)
        self.play(ApplyMethod(self.grid.nodes[cur]["circle"].scale, 1.1), run_time=0.25)
        self.play(ApplyMethod(self.grid.nodes[cur]["circle"].scale, 1.0 / 1.1), run_time=0.5)

        a_cur = None
        self.dfs_code.highlight([1])
        while len(q) > 0:
            cur = q[0]
            q = q[1:]
            self.dfs_code.highlight([2])
            if a_cur is not None:
                self.play(FadeOut(a_cur), run_time=0.5)
            pop_anims = []
            if cur not in self.dfs:
                if cur in parent:
                    pop_anims.append(ApplyMethod(self.grid.edges[(parent[cur], cur)]["line"].set_color, YELLOW))
                pop_anims.append(ApplyMethod(self.grid.nodes[cur]["circle"].set_color, BLUE))
            a_cur = self.a_mark.pop(
                                        lambda x: self.play(
                                            ApplyMethod(x.shift, DOWN),
                                            *pop_anims,
                                            run_time=0.5
                                        )
                                    )
            self.dfs_code.highlight([3])
            if cur not in self.dfs:
                self.dfs_code.highlight([4])
                if rev_neigh is not None:
                    self.play(Write(rev_neigh), run_time=5.0)
                for n in reversed(list(self.grid.neighbors(cur))):
                    r1, r2 = self.grid.get_line_coords(cur, n)
                    line = Line(r1, r2).set_stroke(width=7).set_color(BLUE)
                    self.add(Circle(radius=0.05).move_to(r1).set_fill(PINK, opacity=1.0))
                    self.play(ShowCreation(line), run_time=0.5)
                    self.play(ApplyMethod(self.grid.nodes[n]["circle"].scale, 1.1), run_time=0.25)
                    if n not in q and n not in self.dfs:
                        self.play(ApplyMethod(self.grid.nodes[n]["circle"].set_color, GREEN), run_time=0.25)
                    q.insert(0, n)
                    parent[n] = cur
                    self.play(
                        FadeOut(line),
                        ApplyMethod(self.grid.nodes[n]["circle"].scale, 1.0 / 1.1),
                        run_time=0.5
                    )
                    self.dfs_code.highlight([5])
                    self.a_mark.push(self.grid.nodes[n]["id"])
                    self.dfs_code.highlight([4])
                if rev_neigh is not None:
                    self.play(FadeOut(rev_neigh))
                    self.remove(rev_neigh)
                    rev_neigh = None
                self.dfs.insert(0, cur)
                self.dfs_code.highlight([6])
                self.a_dfs.push_anim_elem(a_cur)
                a_cur = None
                self.play(ApplyMethod(self.grid.nodes[cur]["circle"].set_color, YELLOW), run_time=0.5)
            #
            self.dfs_code.highlight([1])
        #
        self.dfs_code.highlight([])
        if a_cur is not None:
            self.play(FadeOut(a_cur), run_time=0.5)
        self.wait(3.0)
        self.clear()
        self.wait(3.0)
