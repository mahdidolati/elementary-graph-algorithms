from manim import *
from util.util import LinedCode, AnimQueue, GridNetwork, AnimStack


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
        self.s_coord = UP * 3 + LEFT * 4.7
        self.t_coord = self.s_coord + DOWN
        self.dfs_coord = self.t_coord + DOWN

    def construct(self):
        # Illustration of the DFS algorithm in a 3x3 grid: Recursive
        bfs1 = Tex(
            "DFS: Stack-based, pop after all descendants" + "\\\\",
            r"The top of the stack pushes at most one new node from" + "\\\\",
            r"its neighbors, and the stack processing continues." + "\\\\",
            r"If there is no new neighbor, the top is popped" + "\\\\",
            r"and then added to the DFS."
        ).scale(0.9)
        self.play(Write(bfs1), run_time=10.0)
        self.wait(3)
        self.clear()

        self.dfs_code = LinedCode([
            "s = Stack().push(0)",
            "while s not empty:",
            "  top = s.top()",
            "  if neighbors(top).hasNext():",
            "    n = neighbors(top).getNext()",
            "    if n not in s or DFS:",
            "      s.push(n)",
            "  else:",
            "    s.pop()",
            "    add top to DFS",
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

        # Prepare iterators
        for n in self.grid.nodes():
            self.grid.nodes[n]["neighbors"] = iter(self.grid.neighbors(n))

        q_label = Tex("Stack:").set_color(GREEN).move_to(self.s_coord + 1.1 * LEFT)
        self.play(Write(q_label))
        h_label = Tex("Top:").set_color(BLUE).move_to(self.t_coord + 1.0 * LEFT)
        self.play(Write(h_label))
        bfs_label = Tex("DFS:").set_color(YELLOW).move_to(self.dfs_coord + 1.0 * LEFT)
        self.play(Write(bfs_label))

        self.a_mark = AnimStack(self.s_coord, self)
        self.a_dfs = AnimQueue(self.dfs_coord, self)

        cur = (0, 0)
        q = [cur]
        self.dfs_code.highlight([0])
        self.a_mark.push(self.grid.nodes[cur]["id"])
        self.grid.nodes[cur]["circle"].set_color(GREEN)
        self.play(ApplyMethod(self.grid.nodes[cur]["circle"].scale, 1.1), run_time=0.25)
        self.play(ApplyMethod(self.grid.nodes[cur]["circle"].scale, 1.0 / 1.1), run_time=0.5)

        n_eq = None
        self.dfs_code.highlight([1])
        had_push = True
        prev_head = None
        while len(q) > 0:
            self.dfs_code.highlight([2])
            cur = q[0]
            if had_push or n_eq is None:
                if n_eq is not None:
                    self.play(FadeOut(n_eq))
                    self.remove(n_eq)
                    self.play(
                        ApplyMethod(self.grid.nodes[cur]["circle"].set_color, BLUE),
                        ApplyMethod(self.grid.nodes[prev_head]["circle"].set_color, GREEN),
                        run_time=0.5
                    )
                else:
                    self.play(ApplyMethod(self.grid.nodes[cur]["circle"].set_color, BLUE), run_time=0.5)
                n_eq = Tex("$%s$" % str(self.grid.nodes[cur]["id"]))
                n_eq.move_to(self.s_coord)
                self.play(n_eq.animate.shift(DOWN))
            had_push = False
            prev_head = cur
            self.dfs_code.highlight([3])
            try:
                n = next(self.grid.nodes[cur]["neighbors"])
                self.dfs_code.highlight([4])
                r1, r2 = self.grid.get_line_coords(cur, n)
                line = Line(r1, r2).set_stroke(width=7)
                self.add(Circle(radius=0.05).move_to(r1).set_fill(PINK, opacity=1.0))
                if n not in q and n not in self.dfs:
                    line.set_color(YELLOW)
                    self.play(ShowCreation(line), run_time=0.5)
                    self.grid.nodes[n]["circle"].set_color(GREEN)
                    self.play(ApplyMethod(self.grid.nodes[n]["circle"].scale, 1.1), run_time=0.25)
                    self.dfs_code.highlight([5])
                    self.dfs_code.highlight([6])
                    self.a_mark.push(self.grid.nodes[n]["id"])
                    self.grid.edges[(cur, n)]["line"].set_color(YELLOW)
                    self.play(
                        FadeOut(line),
                        ApplyMethod(self.grid.nodes[n]["circle"].scale, 1.0 / 1.1),
                        run_time=0.5
                    )
                    q.insert(0, n)
                    had_push = True
                else:
                    line.set_color(BLUE)
                    self.play(ShowCreation(line), run_time=0.5)
                    self.play(ApplyMethod(self.grid.nodes[n]["circle"].scale, 1.1), run_time=0.25)
                    self.dfs_code.highlight([5])
                    self.play(
                        FadeOut(line),
                        ApplyMethod(self.grid.nodes[n]["circle"].scale, 1.0 / 1.1),
                        run_time=0.5
                    )
            except StopIteration:
                self.dfs_code.highlight([7])
                q = q[1:]
                self.dfs.append(cur)
                self.dfs_code.highlight([8])
                self.a_mark.pop(lambda x: self.play(FadeOut(x), run_time=0.5))
                self.dfs_code.highlight([9])
                self.a_dfs.enqueue_anim_elem(n_eq)
                self.play(ApplyMethod(self.grid.nodes[cur]["circle"].set_color, YELLOW), run_time=0.5)
                n_eq = None
            self.dfs_code.highlight([1])

        self.dfs_code.highlight([])
        self.wait(3.0)
