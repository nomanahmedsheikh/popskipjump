import pickle
import numpy as np
import matplotlib.pylab as plt
from model_factory import get_model

NUM_ITERATIONS = 30
NUM_IMAGES = 1000

FLIP_PROB = 0.2

model = get_model(key='mnist_noman', dataset='mnist')

G = np.round(10 ** np.linspace(0, -2, num=9), 2)
G = list(G) + [0.00127, 10]

def read_dumps():
    raws = []
    for gamma in G:
        folder = 'det_30_1000_g{}'.format(gamma)
        filepath = 'adv/{}/raw_data.pkl'.format(folder)
        raws.append(pickle.load(open(filepath, 'rb')))
    return raws


raws = read_dumps()

fig, ax1 = plt.subplots(figsize=(7, 7))
ax1.set_xlabel('Iterations of the Attack')
ax1.set_ylabel('Median L2 Distance')
ax1.set_yscale('log')
# ax2 = ax1.twinx()
# ax2.set_ylabel('Proportion of Non-adversarial samples')


for i, raw in enumerate(raws):
    # adv_count = np.zeros(NUM_ITERATIONS, )
    medians = []
    for iteration in range(NUM_ITERATIONS):
        distances = []
        for image in range(NUM_IMAGES):
            if 'iterations' not in raw[image]:
                continue
            distance = raw[image]['iterations'][iteration]['distance']
            # adversarial = raw[image]['iterations'][iteration]['perturbed']
            # probs = model.get_probs([adversarial])
            label = raw[image]['true_label']
            # adv_prob = np.max(probs[0][np.arange(10) != label])
            # if np.argmax(probs[0]) != label:
            #     adv_count[iteration] += 1
            distances.append(distance)
        medians.append(np.median(distances))
    ax1.plot(range(1, 31), medians, label='g = {}'.format(G[i]), linewidth=0.9)
    # ax2.plot(1 - adv_count / NUM_IMAGES, '--', label='g = {}'.format(G[i]))

ax1.grid()
plt.title('Radius Size Experiment with Deterministic Model (1000 images)'
          '\ntheta = g / sqrt(d)'
          '\ndelta = theta * sqrt(d) * L2_dist(t)')
ax1.legend()
plt.savefig('adv/radius_exp_1000.pdf')
pass
