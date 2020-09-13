import pickle
import numpy as np
import matplotlib.pylab as plt
from model_factory import get_model


NUM_ITERATIONS = 32
NUM_IMAGES = 1
# TARGET_IMAGE = 4
NOISE = 'bayesian'
exp_name = 'eval_exp_wo_step_50'
# lis = ['infomax_5_32_opp', 'infomax_5_32_evals','infomax_5_32_opp_evals']
lis = ['del_later']
image_path = 'adv/del_later.png'


model = get_model(key='mnist_noman', dataset='mnist')


def read_dump(path):
    filepath = 'adv/{}/raw_data.pkl'.format(path)
    raw = pickle.load(open(filepath, 'rb'))
    return raw


# raws = [read_dump(exp_name)]
raws = [read_dump(s) for s in lis]


fig = plt.figure(figsize=(10, 7))
for i, raw in enumerate(raws):
    t_approx_grad, t_step_search, t_bin_search, t_total = 0, 0, 0, 0
    for iteration in range(NUM_ITERATIONS):
        for image in range(NUM_IMAGES):
            # if image != TARGET_IMAGE:
            #     continue
            if 'iterations' not in raw[image]:
                continue
            epoch = raw[image]['timing']['initial']
            init_search = raw[image]['timing']['init_search'] - epoch
            details = raw[image]['timing']['iters']
            start = details[iteration]['start']
            approx_grad = details[iteration]['approx_grad']
            step_search = details[iteration]['step_search']
            bin_search = details[iteration]['bin_search']
            end = details[iteration]['end']

            t_approx_grad += approx_grad - start
            t_step_search += step_search - approx_grad
            t_bin_search += bin_search - step_search
            t_total += end - start
    labels = ['Approx Grad', 'Step Search', 'Binary Search']
    values = [t_approx_grad, t_step_search, t_bin_search]
    plt.pie(values, labels=labels)
    plt.text(-2, 1, "Approx Grad: {} secs".format(np.round(t_approx_grad, 1)))
    plt.text(-2, 0.9, "Step Search: {} secs".format(np.round(t_step_search, 1)))
    plt.text(-2, 0.8, "Binary Search: {} secs".format(np.round(t_bin_search, 1)))
    plt.text(-2, 0.7, "Total: {} secs".format(np.round(t_total, 1)))
    # plt.bar(['Approx Grad'], [t_approx_grad])
    # plt.bar(['Step Search'], [t_step_search])
    # plt.bar(['Binary Search'], [t_bin_search])
    # plt.bar(['Total'], [t_total])
    # ax1.plot(range(1, NUM_ITERATIONS+2), total_bin_calls, label='Total', color='grey')
# ax1.grid()
plt.title('Timing Analysis for one attack (32 iterations)')
# plt.ylabel('Time (in seconds)')
plt.savefig(image_path)
pass