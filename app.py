from hopskip import HopSkipJumpAttack
from model_interface import ModelInterface
import torchvision.datasets as datasets
from model_factory import get_model
from img_utils import get_sample, save_all_images, read_image
from conf import *
import logging
from datetime import datetime
import os
import numpy as np
import pickle

logging.root.setLevel(logging.WARNING)


def get_samples(n_samples=16):
    np.random.seed(42)
    test_data = datasets.MNIST(root="data", train=False, download=True, transform=None)
    indices = np.random.choice(len(test_data), n_samples, replace=False)
    images = test_data.data[indices].numpy() / 255.0
    labels = test_data.test_labels[indices].numpy()
    return images, labels


def validate_args(args):
    try:
        assert args.dataset is not None
    except:
        print("Invalid Arguments. try 'python app.py -h'")
        exit()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dataset",
                        help="(Mandatory) supported: mnist, cifar10")
    parser.add_argument("-o", "--output", default=None,
                        help="(Optional) path to the output directory")
    args = parser.parse_args()
    validate_args(args)
    exp_name = args.output
    if args.output is None:
        exp_name = 'adv/%s' % datetime.now().strftime("%b%d_%H%M%S")

    if os.path.exists(exp_name):
        logging.info("Path: '{}' already exists. Overwriting it!!!".format(exp_name))
    else:
        os.makedirs(exp_name)

    starts = None
    if EXPERIMENT:
        imgs, labels = get_samples(n_samples=4)
    else:
        if ATTACK_INPUT_IMAGE is None or ATTACK_INPUT_LABEL is None:
            img, label = get_sample(dataset=args.dataset, index=0)
        else:
            img, label = read_image(ATTACK_INPUT_IMAGE), ATTACK_INPUT_LABEL
        imgs, labels = [img], [label]

        if ATTACK_INITIALISE_IMAGE is not None:
            img_start = read_image(ATTACK_INITIALISE_IMAGE)
            starts = [img_start]

    # For now choice of model is fixed for a particular dataset
    if ASK_HUMAN:
        models = [get_model(key='human', dataset=args.dataset, bayesian=BAYESIAN)]
    else:
        models = [get_model(key='mnist', dataset=args.dataset, bayesian=BAYESIAN)]

    model_interface = ModelInterface(models, bounds=(0, 1))
    attack = HopSkipJumpAttack(model_interface, imgs[0].shape, experiment=exp_name, dataset=args.dataset)
    median_distance, additional = attack.attack(imgs, labels, starts, iterations=NUM_ITERATIONS)
    # save_all_images(exp_name, results['iterations'], args.dataset)
    pickle.dump(additional, open('{}/raw_data.pkl'.format(exp_name), 'wb'))
    logging.warning('Saved output at "{}"'.format(exp_name))
    logging.warning('Median_distance: {}'.format(median_distance))


if __name__ == '__main__':
    main()
    pass
