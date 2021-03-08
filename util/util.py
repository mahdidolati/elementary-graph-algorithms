from manim import *
import networkx as nx


class AnimQueue:
    def __init__(self, cur_tail, q_screen):
        self.cur_tail = cur_tail
        self.q_screen = q_screen
        self.content = []

    def enqueue(self, val):
        n_eq = Tex("$%s$" % str(val))
        n_eq.move_to(self.cur_tail)
        self.q_screen.play(Write(n_eq))
        self.cur_tail += RIGHT
        self.content.append(n_eq)

    def enqueue_anim_elem(self, elem):
        self.q_screen.play(ApplyMethod(elem.move_to, self.cur_tail))
        self.cur_tail += RIGHT
        self.content.append(elem)

    def dequeue(self, h_callback=None):
        h = None
        if len(self.content) > 0:
            h = self.content[0]
            if h_callback is not None:
                h_callback(h)
            self.content = self.content[1:]
            vg = VGroup()
            vg.add(*self.content)
            self.q_screen.play(ApplyMethod(vg.shift, LEFT))
            self.cur_tail += LEFT
        return h


class AnimStack:
    def __init__(self, top, scr):
        self.top = top
        self.scr = scr
        self.stack = []

    def push(self, val):
        if len(self.stack) > 0:
            self.scr.play(ApplyMethod(VGroup(*self.stack).shift, RIGHT))
        n_eq = Tex("$%s$" % str(val))
        n_eq.move_to(self.top)
        self.scr.play(Write(n_eq))
        self.stack.insert(0, n_eq)

    def push_anim_elem(self, elem):
        if len(self.stack) > 0:
            self.scr.play(ApplyMethod(VGroup(*self.stack).shift, RIGHT))
        self.scr.play(ApplyMethod(elem.move_to, self.top))
        self.stack.append(elem)

    def pop(self, pop_callback=None):
        t = None
        if len(self.stack) > 0:
            t = self.stack[0]
            if pop_callback is not None:
                pop_callback(t)
            self.stack = self.stack[1:]
            if len(self.stack) > 0:
                self.scr.play(ApplyMethod(VGroup(*self.stack).shift, LEFT))
        return t


class LinedCode:
    def __init__(self, code, c_screen, text_scale=0.6):
        self.prev_highlight = []
        self.code_tex = []
        self.c_screen = c_screen
        for i in range(len(code)):
            indent = 0
            for j in range(len(code[i])):
                if code[i][j] == ' ':
                    indent += 0.5
                else:
                    break
            ct = Tex(r"%s" % code[i])
            ct = ct.scale(text_scale)
            ct = ct.to_edge()
            ct = ct.shift(DOWN * 0.4 * i)
            ct = ct.shift(RIGHT * 0.4 * indent)
            self.code_tex.append(ct)

    def highlight(self, new_lines):
        for l in self.prev_highlight:
            self.c_screen.play(ApplyMethod(self.code_tex[l].set_color, WHITE), run_time=0.15)
        self.prev_highlight = []
        for ln in new_lines:
            self.c_screen.play(ApplyMethod(self.code_tex[ln].set_color, BLUE), run_time=0.15)
            self.prev_highlight.append(ln)


class GridNetwork(nx.Graph):
    def __init__(self, n_row, n_col, **attr):
        super().__init__(**attr)
        radius = 0.4
        for i in range(n_row):
            for j in range(n_col):
                self.add_node((i,j), circle=None, id=i*n_col+j, label=None, neighbors=None)
                if i > 0:
                    self.add_edge((i, j), (i - 1, j), line=None)
                if j > 0:
                    self.add_edge((i, j), (i, j - 1), line=None)
        down_shift = 0.2
        right_shift = 1.0
        for n in self.nodes():
            c = Circle(radius=radius)
            c.move_to(1.4 * DOWN * (n[0] + down_shift) + 1.4 * RIGHT * (n[1] - n_col/2 + right_shift))
            c.set_fill(PINK, opacity=0.5)
            self.nodes[n]["circle"] = c
            #
            n_eq = Tex("$%d$" % self.nodes[n]["id"])
            n_eq.move_to(c.get_center())
            self.nodes[n]["label"] = n_eq
        for e in self.edges():
            if e[0][0] < e[1][0]:
                r1 = self.nodes[e[0]]["circle"].get_center() - [0, self.nodes[e[0]]["circle"].radius, 0]
                r2 = self.nodes[e[1]]["circle"].get_center() + [0, self.nodes[e[0]]["circle"].radius, 0]
            elif e[0][1] < e[1][1]:
                r1 = self.nodes[e[0]]["circle"].get_center() + [self.nodes[e[0]]["circle"].radius, 0, 0]
                r2 = self.nodes[e[1]]["circle"].get_center() - [self.nodes[e[0]]["circle"].radius, 0, 0]
            elif e[1][0] < e[0][0]:
                r1 = self.nodes[e[1]]["circle"].get_center() - [0, self.nodes[e[0]]["circle"].radius, 0]
                r2 = self.nodes[e[0]]["circle"].get_center() + [0, self.nodes[e[0]]["circle"].radius, 0]
            elif e[1][1] < e[0][1]:
                r1 = self.nodes[e[1]]["circle"].get_center() + [self.nodes[e[0]]["circle"].radius, 0, 0]
                r2 = self.nodes[e[0]]["circle"].get_center() - [self.nodes[e[0]]["circle"].radius, 0, 0]

            line = Line(r1, r2).set_color(RED)
            self.edges[e]["line"] = line

    def get_line_coords(self, src_node, dst_node):
        if src_node[0] < dst_node[0]:
            r1 = self.nodes[src_node]["circle"].get_center() - [0, self.nodes[src_node]["circle"].radius, 0]
            r2 = self.nodes[dst_node]["circle"].get_center() + [0, self.nodes[src_node]["circle"].radius, 0]
        elif src_node[1] < dst_node[1]:
            r1 = self.nodes[src_node]["circle"].get_center() + [self.nodes[src_node]["circle"].radius, 0, 0]
            r2 = self.nodes[dst_node]["circle"].get_center() - [self.nodes[src_node]["circle"].radius, 0, 0]
        elif dst_node[0] < src_node[0]:
            r2 = self.nodes[dst_node]["circle"].get_center() - [0, self.nodes[src_node]["circle"].radius, 0]
            r1 = self.nodes[src_node]["circle"].get_center() + [0, self.nodes[src_node]["circle"].radius, 0]
        elif dst_node[1] < src_node[1]:
            r2 = self.nodes[dst_node]["circle"].get_center() + [self.nodes[src_node]["circle"].radius, 0, 0]
            r1 = self.nodes[src_node]["circle"].get_center() - [self.nodes[src_node]["circle"].radius, 0, 0]
        return r1, r2