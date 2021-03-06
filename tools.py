import numpy as np
import numpy.fft as fft
import os
import errno

def cent2edge(x):
    x = np.array(x)
    n = len(x) + 1
    dx = x[1] - x[0]
    x_out = np.zeros(n)
    x_out[:-1] = x[:] - dx / 2
    x_out[-1] = x[-1] + dx / 2
    return x_out


def edge2cent(x):
    x = np.array(x)
    return (x[:-1] + x[1:]) * 0.5

def create_map_2d(power_spectrum_function, x, y):
    n_x = len(x)-1
    n_y = len(y)-1
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    A  = ((x[-1] - x[0])*(y[-1] - y[0]))
    fftfield = np.zeros((n_x, n_y), dtype=complex)
    # z = P(k) = A < |d_k|^2 >
    z = power_spectrum_function(np.abs(np.sqrt(fft.fftfreq(n_x, d=dx)[:, None]**2 + fft.fftfreq(n_y, d=dy)[None, :]**2)))


    # plt.figure()
    # plt.imshow(np.abs(fft.fftshift(fftfield)),
    #            extent=(fft.fftshift(fft.fftfreq(n_x, dx))[0], fft.fftshift(fft.fftfreq(n_x, dx))[- 1],
    #                    fft.fftshift(fft.fftfreq(n_y, dy))[0], fft.fftshift(fft.fftfreq(n_y, dy))[- 1]),
    #            interpolation='none')
    # plt.title('fft')
    # plt.colorbar()
    field = np.random.randn(n_x, n_y, 2)
    # Multiply by n_x * n_y, because inverse function in python divides by N, but that is
    # not in the cosmological convention
    fftfield[:] = n_x * n_y * (field[:, :, 0] + 1j * field[:, :, 1])*np.sqrt(z/A)
    return np.real(np.fft.ifft2(fftfield))


def create_map_3d(power_spectrum_function, x, y, z):
    n_x = len(x) - 1
    n_y = len(y) - 1
    n_z = len(z) - 1
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    dz = z[1] - z[0]
    V = ((x[-1] - x[0]) * (y[-1] - y[0]) * (z[-1] - z[0]))
    fftfield = np.zeros((n_x, n_y, n_z), dtype=complex)
    # z = P(k) = A < |d_k|^2 >
    z = power_spectrum_function(
        np.abs(np.sqrt(fft.fftfreq(n_x, d=dx)[:, None, None]**2
                       + fft.fftfreq(n_y, d=dy)[None, :, None]**2
                       + fft.fftfreq(n_z, d=dz)[None, None, :]**2))
    )

    field = np.random.randn(n_x, n_y, n_z, 2)
    # Multiply by n_x * n_y, because inverse function in python divides by N, but that is
    # not in the cosmological convention
    fftfield[:] = n_x * n_y * n_z * (field[:, :, :, 0] + 1j * field[:, :, :, 1])*np.sqrt(z/V)
    return np.real(np.fft.ifftn(fftfield))


def compute_power_spec2d(x, k_bin_edges, dx=1, dy=1):
    n_x, n_y = x.shape
    Pk_2D = np.abs(fft.fftn(x)) ** 2 * dx * dy / (n_x * n_y)

    kx = np.fft.fftfreq(n_x, dx)
    ky = np.fft.fftfreq(n_y, dy)

    kgrid = np.sqrt(sum(ki ** 2 for ki in np.meshgrid(kx, ky, indexing='ij')))

    Pk_nmodes = np.histogram(kgrid[kgrid > 0], bins=k_bin_edges, weights=Pk_2D[kgrid > 0])[0]
    nmodes = np.histogram(kgrid[kgrid > 0], bins=k_bin_edges)[0]

    # Pk = Pk_nmodes / nmodes
    # k = (k_bin_edges[1:] + k_bin_edges[:-1]) / 2.0
    k = (k_bin_edges[1:] + k_bin_edges[:-1]) / 2.0
    Pk = np.zeros_like(k)
    Pk[np.where(nmodes > 0)] = Pk_nmodes[np.where(nmodes > 0)] / nmodes[np.where(nmodes > 0)]
    return Pk, k, nmodes


def compute_power_spec3d(x, k_bin_edges, dx=1, dy=1, dz=1):
    n_x, n_y, n_z = x.shape
    Pk_3D = np.abs(fft.fftn(x)) ** 2 * dx * dy * dz / (n_x * n_y * n_z)

    kx = np.fft.fftfreq(n_x, dx) * 2 * np.pi
    ky = np.fft.fftfreq(n_y, dy) * 2 * np.pi
    kz = np.fft.fftfreq(n_z, dz) * 2 * np.pi

    kgrid = np.sqrt(sum(ki ** 2 for ki in np.meshgrid(kx, ky, kz, indexing='ij')))

    ###### comment this out later
    # kperp = np.sqrt(sum(ki ** 2 for ki in np.meshgrid(kx, ky, indexing='ij')))
    # kperp = kperp[:, :, None] + 0.0 * Pk_3D

    # kpar = np.abs(kz)
    # kpar = kpar[None, None, :] + 0.0 * Pk_3D
    # kmin = np.min(kperp.flatten())
    # print(kmin, np.min(kpar.flatten()))
    # kgrid[np.where(np.log10(kperp) < -1.0)] = 0.0
    ##########

    Pk_nmodes = np.histogram(kgrid[kgrid > 0], bins=k_bin_edges, weights=Pk_3D[kgrid > 0])[0]
    nmodes = np.histogram(kgrid[kgrid > 0], bins=k_bin_edges)[0]

    k = (k_bin_edges[1:] + k_bin_edges[:-1]) / 2.0
    Pk = np.zeros_like(k)
    Pk[np.where(nmodes > 0)] = Pk_nmodes[np.where(nmodes > 0)] / nmodes[np.where(nmodes > 0)]
    return Pk, k, nmodes

def compute_power_spec_perp_vs_par(x, k_bin_edges, dx=1, dy=1, dz=1): #for each k-vec get absolute value in parallel (redshift) and perp (angle) direction
    n_x, n_y, n_z = x.shape
    Pk_3D = np.abs(fft.fftn(x)) ** 2 * dx * dy * dz / (n_x * n_y * n_z)

    kx = np.fft.fftfreq(n_x, dx) * 2 * np.pi
    ky = np.fft.fftfreq(n_y, dy) * 2 * np.pi
    kz = np.fft.fftfreq(n_z, dz) * 2 * np.pi

    kperp = np.sqrt(sum(ki ** 2 for ki in np.meshgrid(kx, ky, indexing='ij')))
    kperp = kperp[:, :, None] + 0.0 * Pk_3D

    kpar = np.abs(kz)
    kpar = kpar[None, None, :] + 0.0 * Pk_3D

    Pk_nmodes = np.histogram2d(kperp.flatten(), kpar.flatten(), bins=k_bin_edges, weights=Pk_3D.flatten())[0]
    nmodes = np.histogram2d(kperp.flatten(), kpar.flatten(), bins=k_bin_edges)[0]

    k = [(k_edges[1:] + k_edges[:-1]) / 2.0 for k_edges in k_bin_edges]
    Pk = np.zeros((len(k[0]), len(k[1])))
    Pk[np.where(nmodes > 0)] = Pk_nmodes[np.where(nmodes > 0)] / nmodes[np.where(nmodes > 0)]
    return Pk, k, nmodes


def compute_cross_spec3d(x, k_bin_edges, dx=1, dy=1, dz=1):
    n_x, n_y, n_z = x[0].shape
    Ck_3D = np.real(fft.fftn(x[0]) * np.conj(fft.fftn(x[1]))) * dx * dy * dz / (n_x * n_y * n_z)

    kx = np.fft.fftfreq(n_x, dx) * 2 * np.pi
    ky = np.fft.fftfreq(n_y, dy) * 2 * np.pi
    kz = np.fft.fftfreq(n_z, dz) * 2 * np.pi

    kgrid = np.sqrt(sum(ki ** 2 for ki in np.meshgrid(kx, ky, kz, indexing='ij')))

    Ck_nmodes = np.histogram(kgrid[kgrid > 0], bins=k_bin_edges, weights=Ck_3D[kgrid > 0])[0]
    nmodes = np.histogram(kgrid[kgrid > 0], bins=k_bin_edges)[0]

    k = (k_bin_edges[1:] + k_bin_edges[:-1]) / 2.0
    Ck = np.zeros_like(k)
    Ck[np.where(nmodes > 0)] = Ck_nmodes[np.where(nmodes > 0)] / nmodes[np.where(nmodes > 0)]
    return Ck, k, nmodes


def compute_cross_spec_perp_vs_par(x, k_bin_edges, dx=1, dy=1, dz=1): #for each k-vec get absolute value in parallel (redshift) and perp (angle) direction
    n_x, n_y, n_z = x[0].shape
    Ck_3D = np.real(fft.fftn(x[0]) * np.conj(fft.fftn(x[1]))) * dx * dy * dz / (n_x * n_y * n_z)

    kx = np.fft.fftfreq(n_x, dx) * 2 * np.pi
    ky = np.fft.fftfreq(n_y, dy) * 2 * np.pi
    kz = np.fft.fftfreq(n_z, dz) * 2 * np.pi

    kperp = np.sqrt(sum(ki ** 2 for ki in np.meshgrid(kx, ky, indexing='ij')))
    kperp = kperp[:, :, None] + 0.0 * Ck_3D

    kpar = np.abs(kz)
    kpar = kpar[None, None, :] + 0.0 * Ck_3D

    Ck_nmodes = np.histogram2d(kperp.flatten(), kpar.flatten(), bins=k_bin_edges, weights=Ck_3D.flatten())[0]
    nmodes = np.histogram2d(kperp.flatten(), kpar.flatten(), bins=k_bin_edges)[0]

    k = [(k_edges[1:] + k_edges[:-1]) / 2.0 for k_edges in k_bin_edges]
    Ck = np.zeros((len(k[0]), len(k[1])))
    Ck[np.where(nmodes > 0)] = Ck_nmodes[np.where(nmodes > 0)] / nmodes[np.where(nmodes > 0)]
    return Ck, k, nmodes


def distribute_indices(n_indices, n_processes, my_rank):
    divide = n_indices // n_processes
    leftovers = n_indices % n_processes

    if my_rank < leftovers:
        my_n_cubes = divide + 1
        my_offset = my_rank
    else:
        my_n_cubes = divide
        my_offset = leftovers
    start_index = my_rank * divide + my_offset
    my_indices = range(start_index, start_index + my_n_cubes)
    return my_indices

# From Tony Li

def ensure_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
