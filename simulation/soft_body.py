from manim import *
import numpy as np
import networkx as nx
from util.util import Geometry


def to_coord(v):
    return v[0] * RIGHT + v[1] * UP


class Polygon:
    def __init__(self):
        self.shape = nx.Graph()

    def add_edge(self, x, y):
        if x not in self.shape.nodes():
            self.shape.add_node(x)
        if y not in self.shape.nodes():
            self.shape.add_node(y)
        if (x, y) not in self.shape.edges():
            self.shape.add_edge(x, y, q=set(), e=[np.array(x).reshape((2, 1)), np.array(y).reshape((2, 1))])

    def add_edges(self, edge_list):
        for e in edge_list:
            self.add_edge(e[0], e[1])

    def draw(self, q_screen):
        for e in self.shape.edges():
            l = Line(to_coord(e[0]), to_coord(e[1])).set_color(BLUE)
            self.shape.edges[e]['q'].add(l)
            q_screen.add(l)

    def point_inside(self, p):
        x = p[0]
        y = p[1]
        n = 0
        corner_meet = 0
        for e in self.shape.edges():
            if e[0][0] < x < e[1][0] or e[1][0] < x < e[0][0]:
                yp = (x - e[0][0]) * (e[1][1] - e[0][1]) / (e[1][0] - e[0][0]) + e[0][1]
                if yp < y:
                    n += 1
            if x == e[0][0]:
                if e[0][1] < y:
                    corner_meet += 1
            if x == e[1][0]:
                if e[1][1] < y:
                    corner_meet += 1

        return (n + corner_meet // 2) % 2 != 0

    def get_intersection(self, p1, p2):
        g = Geometry()
        candidates = None
        for e in self.shape.edges():
            r = g.get_line_segment_intersection(self.shape.edges[e]['e'], [p1, p2])
            if r is not None:
                if candidates is None:
                    candidates = r
                if np.linalg.norm(r - p1) < np.linalg.norm(candidates - p1):
                    candidates = r
        return candidates


class Point:
    def __init__(self, x, y):
        self.id = (x, y)
        self.position = np.array([x, y], dtype='float64').reshape((2, 1))
        self.velocity = np.zeros(2, dtype='float64').reshape((2, 1))
        self.force = np.zeros(2, dtype='float64').reshape((2, 1))
        self.latent_force = np.zeros(2, dtype='float64').reshape((2, 1))
        self.mass = np.random.uniform(1, 2, 1)[0]

    def set_force_gravity(self):
        self.force[0, 0] = self.force[0, 0] - self.mass * 0.9

    def set_velocity(self, dt):
        self.velocity = self.velocity + self.force * dt / self.mass

    def set_position(self, dt):
        self.position = self.position + self.velocity * dt

    def reset_force(self):
        self.force = np.array(self.latent_force)
        self.latent_force = np.zeros(2, dtype='float64').reshape((2, 1))

    def apply_force(self, fd, f):
        unit_x = np.array([1, 0], dtype='float64').reshape((2, 1))
        unit_y = np.array([0, 1], dtype='float64').reshape((2, 1))
        self.force[0, 0] = self.force[0, 0] + np.dot(np.transpose(fd), unit_x) * f
        self.force[1, 0] = self.force[1, 0] + np.dot(np.transpose(fd), unit_y) * f

    def get_next_position(self, dt):
        v = self.velocity + self.force * dt / self.mass
        return self.position + v * dt


class Spring:
    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.L0 = np.linalg.norm(self.A.position - self.B.position)
        self.ks = 15.7
        self.kd = 0.3

    def set_force_spring(self):
        norm1 = np.linalg.norm(self.A.position - self.B.position)
        abu = self.B.position - self.A.position / norm1
        bau = -1 * abu
        f1 = self.ks * (np.linalg.norm(self.A.position - self.B.position) - self.L0)
        self.A.apply_force(abu, f1)
        self.B.apply_force(bau, f1)
        fa = np.dot(np.transpose(abu), self.B.velocity - self.A.velocity) * self.kd
        self.A.apply_force(abu, fa)
        fb = np.dot(np.transpose(bau), self.A.velocity - self.B.velocity) * self.kd
        self.B.apply_force(bau, fb)


class SoftRectangle:
    def __init__(self, w, h):
        self.lines = set()
        self.g = nx.Graph()
        for i in range(w):
            for j in range(h):
                c = Circle(radius=0.1)
                c.move_to(i * RIGHT + j * UP)
                c.set_fill(PINK, opacity=0.5)
                self.g.add_node((i, j), p=Point(i, j), c=c)
                neighbors = [(i-1, j), (i, j-1), (i-1, j-1)]
                for n in neighbors:
                    if n[0] >= 0 and n[1] >= 0:
                        self.g.add_edge((i, j), n, s=Spring(self.g.nodes[(i, j)]['p'], self.g.nodes[n]['p']))

    def step(self):
        for n in self.g.nodes():
            self.g.nodes[n]['p'].reset_force()
            self.g.nodes[n]['p'].set_force_gravity()
        for e in self.g.edges():
            self.g.edges[e]['s'].set_force_spring()
        for n in self.g.nodes():
            print(">", n, self.g.nodes[n]['p'].force)

    def update_positions(self, dt, p):
        for n in self.g.nodes():
            c_p = self.g.nodes[n]['p'].position
            n_p = self.g.nodes[n]['p'].get_next_position(dt)
            if p.point_inside(n_p):
                t = p.get_intersection(c_p, n_p)
                print("t:", c_p, n_p, t)
                self.g.nodes[n]['p'].latent_force = -1 * self.g.nodes[n]['p'].force
                self.g.nodes[n]['p'].position = t
            else:
                self.g.nodes[n]['p'].set_velocity(dt)
                self.g.nodes[n]['p'].set_position(dt)

    def move_atom(self, n, d):
        self.g.nodes[n]['p'].position += d

    def move_anim(self, q_screen):
        for l in self.lines:
            q_screen.remove(l)
        for e in self.g.edges():
            e1 = self.g.nodes[e[0]]['p'].position[0, 0] * RIGHT + self.g.nodes[e[0]]['p'].position[1, 0] * UP
            e2 = self.g.nodes[e[1]]['p'].position[0, 0] * RIGHT + self.g.nodes[e[1]]['p'].position[1, 0] * UP
            l = Line(e1, e2).set_color(PINK).set_opacity(0.5)
            self.lines.add(l)
            q_screen.add(l)
        for n in self.g.nodes():
            self.g.nodes[n]['c'].move_to(
                self.g.nodes[n]['p'].position[0, 0] * RIGHT +
                self.g.nodes[n]['p'].position[1, 0] * UP
            )


class SoftBody(Scene):
    def construct(self):
        s = SoftRectangle(2, 2)
        for n in s.g.nodes():
            self.add(s.g.nodes[n]['c'])
        s.move_anim(self)
        p = Polygon()
        p.add_edges([
            [(-2, -1), (-1, -1)], [(-1, -1), (-1, 3)], [(-1, 3), (-2, 3)], [(-2, 3), (-2, -1)]
        ])
        p.draw(self)
        self.wait(1)

        s.move_atom((0, 0), np.array([-0.5, 0], dtype='float64').reshape((2, 1)))
        s.move_atom((1, 0), np.array([0.5, 0], dtype='float64').reshape((2, 1)))
        s.move_anim(self)
        self.wait(1)

        dt = 0.05
        for _ in range(250):
            s.step()
            s.update_positions(dt, p)
            s.move_anim(self)
            self.wait(2 * dt)


def main():
    p1 = np.array([-1, 1])
    p2 = np.array([1, 1])
    p3 = np.array([1, 2])
    p4 = np.array([-1, 0])
    line1 = [p2, p1]
    line2 = [p3, p4]
    g = Geometry()
    print(g.get_reflection(line1, line2))


if __name__ == "__main__":
    main()