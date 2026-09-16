# Funcoes de transformacao usadas nos exercicios da AC02

import numpy as np
import matplotlib.pyplot as plt


def translate(points, translation):
    return points + np.array(translation)


def scale(points, sx, sy):
    matriz = np.array([[sx, 0],
                       [0, sy]])
    return points.dot(matriz.T)


def rotate(points, angulo_graus):
    # angulo positivo = sentido anti-horario
    a = np.radians(angulo_graus)
    matriz = np.array([[np.cos(a), -np.sin(a)],
                       [np.sin(a), np.cos(a)]])
    return points.dot(matriz.T)


def reflect_x(points):
    # reflexao em relacao ao eixo x (inverte o y)
    matriz = np.array([[1, 0],
                       [0, -1]])
    return points.dot(matriz.T)


def reflect_y(points):
    # reflexao em relacao ao eixo y (inverte o x)
    matriz = np.array([[-1, 0],
                       [0, 1]])
    return points.dot(matriz.T)


def shear_x(points, k):
    matriz = np.array([[1, k],
                       [0, 1]])
    return points.dot(matriz.T)


def plot_shapes(original_shape, transformed_shape, title):
    plt.figure()
    plt.plot(*zip(*original_shape, original_shape[0]), label="Original")
    plt.plot(*zip(*transformed_shape, transformed_shape[0]), label="Transformado", linestyle="--")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.axis("equal")
    plt.show()


def plot_points(original_point, transformed_point, title):
    plt.figure()
    plt.scatter(original_point[0], original_point[1], label="Original")
    plt.scatter(transformed_point[0], transformed_point[1], label="Transformado", marker="x")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.axhline(0, color="black", linewidth=0.5)
    plt.axvline(0, color="black", linewidth=0.5)
    plt.axis("equal")
    plt.show()
