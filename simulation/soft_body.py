from manim import *
import numpy as np
import networkx as nx


class Point:
    def __init__(self, x, y):
        self.id = (x, y)
        self.position = np.array([x, y], dtype='float64').reshape((2, 1))
        self.velocity = np.zeros((2, 1), dtype='float64')
        self.force = np.zeros((2, 1), dtype='float64')
        self.mass = np.random.uniform(1, 2, 1)[0]

    def set_force_gravity(self):
        self.force[1, 0] = self.force[1, 0] - self.mass * 9.8

    def set_velocity(self, dt):
        self.velocity = self.velocity + self.force * dt / self.mass

    def set_position(self, dt):
        self.position = self.position + self.velocity * dt

    def reset_force(self):
        self.force = np.zeros((2, 1), dtype='float64')

    def apply_force(self, fd, f):
        unit_x = np.array([1, 0], dtype='float64').reshape((2, 1))
        unit_y = np.array([0, 1], dtype='float64').reshape((2, 1))
        self.force[0, 0] = self.force[0, 0] + np.dot(np.transpose(unit_x), fd) * f
        self.force[1, 0] = self.force[1, 0] + np.dot(np.transpose(unit_y), fd) * f


class Spring:
    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.L0 = np.linalg.norm(self.A.position - self.B.position)
        self.ks = 0.7
        self.kd = 0.1

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

    def step(self, dt):
        for n in self.g.nodes():
            self.g.nodes[n]['p'].reset_force()
            self.g.nodes[n]['p'].set_force_gravity()
        for e in self.g.edges():
            self.g.edges[e]['s'].set_force_spring()
        for n in self.g.nodes():
            self.g.nodes[n]['p'].set_velocity(dt)
            self.g.nodes[n]['p'].set_position(dt)
            self.g.nodes[n]['c'].move_to(
                self.g.nodes[n]['p'].position[0, 0] * RIGHT +
                self.g.nodes[n]['p'].position[1, 0] * UP
            )

    def move_atom(self, n, d):
        self.g.nodes[n]['p'].position += d
        self.g.nodes[n]['c'].move_to(
            self.g.nodes[n]['p'].position[0, 0] * RIGHT +
            self.g.nodes[n]['p'].position[1, 0] * UP
        )


class SoftBody(Scene):
    def construct(self):
        s = SoftRectangle(2, 1)
        for n in s.g.nodes():
            self.add(s.g.nodes[n]['c'])
        self.wait(1)

        s.move_atom((0, 0), np.array([-0.5, 0], dtype='float64').reshape((2, 1)))
        s.move_atom((1, 0), np.array([0.5, 0], dtype='float64').reshape((2, 1)))
        self.wait(1)

        dt = 0.05
        for _ in range(500):
            s.step(dt)
            self.wait(2 * dt)
