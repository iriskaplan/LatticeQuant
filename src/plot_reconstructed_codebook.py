import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial import Voronoi

from closest_point import closest_point_A2
from nested_lattice_quantizer import (NestedLatticeQuantizer as NQuantizer,
                                      HierarchicalNestedLatticeQuantizer as HQuantizer)
from utils import get_a2


def generate_codebook(G, closest_point, q, with_plot=True):
    points = []
    quantizer = NQuantizer(G, closest_point, q=q, beta=1, alpha=1)

    for i in range(q):
        for j in range(q):
            l_p = np.dot(G, np.array([i, j]))
            enc, _ = quantizer._encode(l_p)
            dec = quantizer._decode(enc)
            points.append(dec)

    points = np.array(points)

    if with_plot:
        plot_lattice_points(points, q)

    return points


def plot_lattice_points(points, q):
    plt.figure(figsize=(8, 8))
    plt.scatter(points[:, 0], points[:, 1], color='blue', s=30, label='Lattice Points')
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.legend()
    plt.title(f"Lattice Codebook with Shaping Region, $q$ = {q}")
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


def compare_codebooks(G, closest_point, q, M, with_plot=True):
    lattice_points = []
    mismatches = []
    matches = []
    r_q = (1 - q**(1-M))/ (q- 1)

    h_quantizer = HQuantizer(G, closest_point, q, beta=1, alpha=1, M=M)
    n_quantizer = NQuantizer(G, closest_point, (q**M) * (1 - r_q), beta=1, alpha=1,)

    point_map = {}
    duplicates = []

    d = 1e-9 * np.random.normal(0, 1, size=2)
    for i in range(q ** M):
        for j in range(q**M):
            l_p = np.dot(G, np.array([i, j])) + d

            b_list, _ = h_quantizer._encode(l_p)
            dec = h_quantizer._decode(b_list)

            enc, _ = n_quantizer._encode(l_p)
            l_dec = n_quantizer._decode(enc)

            if np.allclose(l_dec, l_p, atol=1e-7):
                if not np.allclose(dec, l_dec, atol=1e-7):
                    mismatches.append((l_p, dec, l_dec))
                else:
                    matches.append((l_p, dec))

            dec_tuple = tuple(np.round(dec, decimals=9))
            if dec_tuple in point_map:
                duplicates.append((dec_tuple, point_map[dec_tuple], (i, j)))
            else:
                point_map[dec_tuple] = (i, j)

            lattice_points.append(dec)

    lattice_points = np.array(lattice_points)
    print(f"Number of unique points: {len(np.unique(lattice_points, axis=0))}")

    if duplicates:
        print("Duplicate points found:")
        for dup_point, original_values, duplicate_values in duplicates:
            print(f"Point: {dup_point}")
            print(f"Original values: {original_values}")
            print(f"Duplicate values: {duplicate_values}")
    else:
        print("All points are unique.")

    if mismatches:
        print("Mismatched points found:")
        for l_p, dec, l_dec in mismatches:
            print(f"Original point: {l_p}")
            print(f"Nested quantizer decoding: {dec}")
            print(f"Regular quantizer decoding: {l_dec}")
    else:
        print("All points matched correctly.")

    if with_plot:
        plot_with_voronoi(lattice_points, q, r_q, M)


def plot_with_voronoi(lattice_points, q, r_qM, M=2):
    plt.figure(figsize=(8, 8))
    plt.scatter(lattice_points[:, 0], lattice_points[:, 1], c='blue', s=1, label='$\mathcal{C}_{L,q,M}$')

    vor = Voronoi(lattice_points)

    origin_idx = np.where(np.isclose(lattice_points, np.array([0, 0]), atol=1e-2).all(axis=1))[0][0]
    region_idx = vor.point_region[origin_idx]
    vertices = vor.vertices[vor.regions[region_idx]]

    scaled_vertices_q_qm1 = (q**M) * (1 - r_qM) * vertices
    scaled_vertices_q_qp1 = (q**M) * (1 + r_qM) * vertices
    scaled_vertices_q2 = q ** M * vertices

    scaled_vertices_q_qm1 = np.vstack([scaled_vertices_q_qm1, scaled_vertices_q_qm1[0]])
    scaled_vertices_q_qp1 = np.vstack([scaled_vertices_q_qp1, scaled_vertices_q_qp1[0]])
    scaled_vertices_q2 = np.vstack([scaled_vertices_q2, scaled_vertices_q2[0]])

    plt.plot(scaled_vertices_q_qm1[:, 0], scaled_vertices_q_qm1[:, 1],
             color='green', linewidth=2, label=fr'$q^{{M}}(1 - r_{{q,M}})\mathcal{{V}}$')
    plt.plot(scaled_vertices_q2[:, 0], scaled_vertices_q2[:, 1],
             color='orange', linewidth=2, label=rf'$q^{{M}} \mathcal{{V}}$')
    plt.plot(scaled_vertices_q_qp1[:, 0], scaled_vertices_q_qp1[:, 1],
             color='pink', linewidth=2, label=fr'$q^{{M}}(1 + r_{{q,M}})\mathcal{{V}}$')

    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.legend()
    plt.title(rf'Reconstructed Codebook for $A_2$ Lattice with $q^{M}$ = {q ** M}')
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig(f'A2q6M{M}.png')


def main():
    G = get_a2()
    closest_point = closest_point_A2
    q = 4

    M = 2
    compare_codebooks(G, closest_point, q=q, M=M, with_plot=True)

    M = 3
    compare_codebooks(G, closest_point, q=q, M=M, with_plot=True)


if __name__ == "__main__":
    main()
