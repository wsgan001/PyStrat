import sys
import pickle

import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt

from tqdm import trange


def get_neighbor(i, N):
    x,y = i
    r = lambda: np.random.randint(-1,2)
    return (x+r()) % N, (y+r()) % N

def get_threshold(i, lattice):
    val = lattice[i]
    return np.sum(lattice==val) / lattice.size

def takespread(sequence, num):
    length = float(len(sequence))
    for i in range(num):
        yield sequence[int(np.ceil(i * length / num))]

def simulate(resolution=40000, fname='data.dat'):
    """ Simulate Bornholdt/Sneppen model
    """
    N = 128
    tmax = resolution*2#80000
    alpha = 25e-6

    freq = int(tmax / resolution)

    lattice = np.zeros((N,N))
    strategy_num = np.unique(lattice).size

    strats = {} # strategy history of each node
    snapshots = []

    get_random = lambda: tuple(np.random.randint(N, size=2)) # get index of random node in system

    for index, s in np.ndenumerate(lattice):
        strats[index] = set([s])

    # simulate system
    for t in trange(tmax*N**2):
        i = get_random()
        j = get_neighbor(i, N)

        thres = get_threshold(j, lattice) # n_j / N^2
        if np.random.random() < thres and not lattice[j] in strats[i]:
            lattice[i] = lattice[j]
            strats[i].add(lattice[i])

        if np.random.random() < alpha:
            k = get_random()
            lattice[k] = strategy_num
            strats[k].add(lattice[k])
            strategy_num += 1

        if t % int(freq*N**2) == 0:
            snapshots.append((t, lattice.copy()))

    # save result
    with open(fname, 'wb') as fd:
        pickle.dump({
            'snapshots': snapshots,
            'config': {
                'N': N,
                'tmax': tmax,
                'alpha': alpha
            }
        }, fd)

def plot(fname):
    """ Plot result generated by simulation
    """
    with open(fname, 'rb') as fd:
        data = pickle.load(fd)

    N = data['config']['N']
    print('Parsing', len(data['snapshots']), 'entries')

    # compute statistics
    strat_nums = []
    for t, lattice in data['snapshots']:
        snum = np.unique(lattice).size
        strat_nums.append((t/N**2, snum))

    snapshots = list(takespread(data['snapshots'], 5))

    # plotting
    gs = mpl.gridspec.GridSpec(2, len(snapshots))

    for i, (t, lattice) in enumerate(sorted(snapshots)):
        ax = plt.subplot(gs[0, i])
        ax.imshow(lattice, interpolation='nearest')
        ax.set_title(r'$t={:d}$'.format(int(t/N**2)), fontsize=10)
        ax.tick_params(axis='both', which='both', labelsize=5)

    ax = plt.subplot(gs[1, :])
    ax.plot(*zip(*strat_nums))
    ax.set_xlabel(r'$t$')
    ax.set_ylabel('#strategies')

    plt.savefig('result.pdf')

if __name__ == '__main__':
    if len(sys.argv) > 2:
        print('Usage: {} [data file]'.format(sys.argv[0]))
        exit(-1)

    if len(sys.argv) == 1:
        simulate()
    else:
        plot(sys.argv[1])
