from manim import *
import networkx as nx
import json
import ast


class Geometry:
    def __init__(self):
        pass

    def get_intersection(self, line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
           return None

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

class Node:
    def __init__(self, id, label, priority):
        self.id = id
        self.priority = priority
        self.n_eq = Tex("$\\frac{%s}{%s}$" % (str(label), str(priority)))


class AnimPriorityQueue:
    def __init__(self, q_head, q_screen):
        self.q_head = q_head
        self.q_screen = q_screen
        self.content = []

    def enqueue(self, id, label, priority):
        i = 0
        while i < len(self.content):
            if self.content[i].priority >= priority:
                break
            else:
                i += 1
        vg = VGroup()
        vg.add(*[x.n_eq for x in self.content[i:]])
        self.q_screen.play(ApplyMethod(vg.shift, RIGHT))
        n = Node(id, label, priority)
        n.n_eq.move_to(self.q_head + i * RIGHT)
        self.q_screen.play(Write(n.n_eq))
        self.content = self.content[0:i] + [n] + self.content[i:]

    def dequeue(self, h_callback=None):
        h = None
        if len(self.content) > 0:
            h = self.content[0]
            if h_callback is not None:
                h_callback(h)
            self.content = self.content[1:]
            vg = VGroup()
            vg.add(*[x.n_eq for x in self.content])
            self.q_screen.play(ApplyMethod(vg.shift, LEFT))
        return h

    def is_empty(self):
        return len(self.content) == 0


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
    def __init__(self, topo_file, configs, **attr):
        super().__init__(**attr)
        radius = configs["radius"] if "radius" in configs else 0.35
        shift = configs["shift"] if "shift" in configs else 0 * RIGHT
        weights = iter([1, 11, 7, 6, 8, 3, 2, 9, 12, 5, 4, 10])
        n_col = 3
        with open(topo_file) as json_file:
            data = json.load(json_file)
            for n in data["nodes"]:
                nv = ast.literal_eval(n)
                self.add_node(nv, circle=None, id=nv[0] * n_col + nv[1], label=None, neighbors=None)
                c = Circle(radius=radius)
                c.move_to(1.5 * DOWN * nv[0] + 1.5 * RIGHT * (nv[1] - n_col / 2) + shift)
                c.set_fill(PINK, opacity=0.5)
                self.nodes[nv]["circle"] = c
                #
                n_eq = Tex("$v_%d$" % self.nodes[nv]["id"])
                n_eq.move_to(c.get_center())
                self.nodes[nv]["label"] = n_eq
            for n1 in data["edges"]:
                for n2 in data["edges"][n1]:
                    n1v = ast.literal_eval(n1)
                    n2v = ast.literal_eval(n2)
                    self.add_edge(n1v, n2v, line=None, w=next(weights), w_label=None)
                    #
                    r1, r2 = self.get_line_coords(n1v, n2v)
                    line = Line(r1, r2).set_color(RED)
                    self.edges[(n1v, n2v)]["line"] = line
                    #
                    if ast.literal_eval(data["weighted"]) and "weighted" in configs and configs["weighted"]:
                        wl = Tex("$%d$" % self.edges[(n1v, n2v)]["w"]).scale(0.8)
                        if "wxs" in data["edges"][n1][n2]:
                            wl.move_to((r1 + r2) / 2 + data["edges"][n1][n2]["wxs"] * RIGHT * 0.3)
                        if "wys" in data["edges"][n1][n2]:
                            wl.move_to((r1 + r2) / 2 + data["edges"][n1][n2]["wys"] * DOWN * 0.3)
                        self.edges[(n1v, n2v)]["w_label"] = wl

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