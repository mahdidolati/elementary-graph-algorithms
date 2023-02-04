from manim import *
import numpy as np
import networkx as nx
from util.util import Geometry


def to_coord(v):
    return v[0] * RIGHT + v[1] * UP


class Polygon:
    def __init__(self):
        self.convex_box = {'left-x': None, 'right-x': None, 'up-y': None, 'down-y': None}
        self.shape = nx.Graph()

    def update_convex_box(self, p):
        if self.convex_box['left-x'] is None:
            self.convex_box['left-x'] = p[0]
            self.convex_box['right-x'] = p[0]
            self.convex_box['up-x'] = p[1]
            self.convex_box['down-x'] = p[1]
            return
        if p[0] < self.convex_box['left-x']:
            self.convex_box['left-x'] = p[0]
        if p[0] > self.convex_box['right-x']:
            self.convex_box['right-x'] = p[0]
        if p[1] < self.convex_box['down-x']:
            self.convex_box['down-x'] = p[1]
        if p[1] > self.convex_box['up-x']:
            self.convex_box['up-x'] = p[1]

    def add_edge(self, x, y):
        if x not in self.shape.nodes():
            self.shape.add_node(x)
            self.update_convex_box(x)
        if y not in self.shape.nodes():
            self.shape.add_node(y)
            self.update_convex_box(y)
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
        if p[0] <= self.convex_box['left-x'] or p[0] >= self.convex_box['right-x']:
            return False
        if p[1] <= self.convex_box['down-x'] or p[1] >= self.convex_box['up-x']:
            return False
        x = p[0, 0]
        y = p[1, 0]
        n = 0
        corner_meet = 0
        for e in self.shape.edges():
            e0 = self.shape.edges[e]['e'][0]
            e1 = self.shape.edges[e]['e'][1]
            if e0[0, 0] < x < e1[0, 0] or e1[0, 0] < x < e0[0, 0]:
                m = (e1[1, 0] - e0[1, 0]) / (e1[0, 0] - e0[0, 0])
                yp = (x - e0[0, 0]) * m + e0[1, 0]
                if np.abs(yp - y) < 0.0001:
                    return False
                if yp < y:
                    n += 1
            if x == e0[0, 0]:
                if e0[1, 0] < y:
                    corner_meet += 1
            if x == e1[0, 0]:
                if e1[1, 0] < y:
                    corner_meet += 1

        return (n + corner_meet // 2) % 2 != 0

    def get_intersection(self, p1, p2):
        g = Geometry()
        candidates = None
        hl = None
        for e in self.shape.edges():
            r = g.get_line_segment_intersection(self.shape.edges[e]['e'], [p1, p2])
            if r is not None:
                if candidates is None:
                    candidates = r
                    hl = self.shape.edges[e]['e']
                if np.linalg.norm(r - p1) < np.linalg.norm(candidates - p1):
                    candidates = r
                    hl = self.shape.edges[e]['e']
        return candidates, hl


class Point:
    def __init__(self, x, y):
        self.id = (x, y)
        self.position = np.array([x, y], dtype='float64').reshape((2, 1))
        self.velocity = np.zeros(2, dtype='float64').reshape((2, 1))
        self.force = np.zeros(2, dtype='float64').reshape((2, 1))
        self.latent_force = np.zeros(2, dtype='float64').reshape((2, 1))
        self.mass = 1.0

    def set_force_gravity(self):
        self.force[1, 0] = self.force[1, 0] - self.mass * 0.25

    def shift(self, dx, dy):
        self.position += np.array([dx, dy], dtype='float64').reshape((2, 1))

    def reset_velocity(self, direction=None):
        if direction is None:
            self.velocity = np.zeros(2, dtype='float64').reshape((2, 1))
        else:
            d = direction / np.linalg.norm(direction)
            t = np.dot(np.transpose(self.velocity), d) * d
            self.velocity -= t

    def set_velocity(self, dt):
        self.velocity = self.velocity + self.force * dt / self.mass

    def set_position(self, dt):
        self.position = self.position + self.velocity * dt

    def reset_force(self):
        self.force = self.latent_force
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
    def __init__(self, A, B, ks):
        self.A = A
        self.B = B
        self.L0 = np.linalg.norm(self.A.position - self.B.position)
        self.ks = ks
        self.kd = 0.9

    def set_force_spring(self):
        norm1 = np.linalg.norm(self.A.position - self.B.position)
        abu = (self.B.position - self.A.position) / norm1
        bau = -1 * abu
        f1 = self.ks * (norm1 - self.L0)
        self.A.apply_force(abu, f1)
        self.B.apply_force(bau, f1)
        fa = np.dot(np.transpose(abu), self.B.velocity - self.A.velocity) * self.kd
        self.A.apply_force(abu, fa)
        fb = np.dot(np.transpose(bau), self.A.velocity - self.B.velocity) * self.kd
        self.B.apply_force(bau, fb)


class SoftRectangle:
    def __init__(self, w, h, ks):
        self.lines = set()
        self.g = nx.Graph()
        for i in range(w):
            for j in range(h):
                c = Circle(radius=0.1)
                x = 0.5 * i
                y = 0.5 * j
                c.move_to(x * RIGHT + y * UP)
                c.set_fill(PINK, opacity=0.5)
                self.g.add_node((i, j), p=Point(x, y), c=c)
                if i % 2 == 0:
                    neighbors = [(i-1, j), (i, j-1), (i-1, j-1)]
                else:
                    neighbors = [(i - 1, j), (i, j - 1), (i - 1, j + 1)]
                for n in neighbors:
                    if n[0] >= 0 and 0 <= n[1] < h:
                        self.g.add_edge((i, j), n, s=Spring(self.g.nodes[(i, j)]['p'], self.g.nodes[n]['p'], ks))

    def shift(self, dx, dy):
        for n in self.g.nodes():
            self.g.nodes[n]['p'].shift(dx, dy)

    def step(self):
        for n in self.g.nodes():
            self.g.nodes[n]['p'].reset_force()
            self.g.nodes[n]['p'].set_force_gravity()
        for e in self.g.edges():
            self.g.edges[e]['s'].set_force_spring()

    def update_positions(self, dt, p):
        for n in self.g.nodes():
            c_p = self.g.nodes[n]['p'].position
            n_p = self.g.nodes[n]['p'].get_next_position(dt)
            if p.point_inside(n_p):
                t, hl = p.get_intersection(c_p, n_p)
                g = Geometry()
                force = self.g.nodes[n]['p'].force
                p_dir = g.get_force_reflection(hl)
                f = -1 * np.dot(np.transpose(force), p_dir) * p_dir
                self.g.nodes[n]['p'].latent_force = f
                self.g.nodes[n]['p'].reset_velocity(p_dir)
                self.g.nodes[n]['p'].position = t
            else:
                self.g.nodes[n]['p'].latent_force = np.zeros(2, dtype='float64').reshape((2, 1))
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
    def draw_body(self, body):
        for n in body.g.nodes():
            self.add(body.g.nodes[n]['c'])
        body.move_anim(self)

    def move_body(self, body, dt, p):
        body.step()
        body.update_positions(dt, p)
        body.move_anim(self)

    def construct(self):
        bodies = [SoftRectangle(3, 3, 72), SoftRectangle(3, 3, 24), SoftRectangle(3, 3, 8)]
        body_shifts = [(-4, 1.5), (-1, 1.5), (2, 1.5)]
        for i in range(len(bodies)):
            bodies[i].shift(*body_shifts[i])
            self.draw_body(bodies[i])

        p = Polygon()
        p.add_edges([
            # [(-1, -2), (3, -2)], [(3, -2), (-1, 2)], [(-1, 2), (-1, -2)]
            [(-5, -2), (4, -2)], [(4, -2), (4, -1)], [(4, -1), (-5, -1)], [(-5, -1), (-5, -2)]
        ])
        p.draw(self)
        self.wait(1)

        # s.move_atom((0, 0), np.array([-0.5, 0], dtype='float64').reshape((2, 1)))
        # s.move_atom((1, 0), np.array([0.5, 0], dtype='float64').reshape((2, 1)))
        # s.move_anim(self)
        # self.wait(1)

        dt = 0.05
        for _ in range(400):
            for b in bodies:
                self.move_body(b, dt, p)
            self.wait(2 * dt)


if __name__ == "__main__":
    pass
