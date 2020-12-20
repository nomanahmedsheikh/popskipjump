import numpy as np
import torch
import torchvision.datasets as datasets
from PIL import Image

CIFAR_PATHS = ['cifar10_00_3.png', 'cifar10_01_8.png']
MNIST_PATHS = ['mnist_01_3.jpg', 'mnist_02_6.jpg', 'mnist_03_0.jpg', 'mnist_04_7.jpg', 'mnist_05_9.jpg']


def read_image(path):
    return np.asarray(Image.open(path)) / 255


def get_sample(dataset, index=0):
    if dataset == 'cifar10':
        filename = CIFAR_PATHS[index]
    elif dataset == 'mnist':
        filename = MNIST_PATHS[index]
    else:
        raise
    img = read_image('data/{}'.format(filename))
    label = int(filename.split('.')[0].split('_')[-1])
    return img, label


def get_shape(dataset):
    if dataset == 'cifar10':
        return 32, 32, 3
    if dataset == 'mnist':
        return 28, 28
    raise RuntimeError("Unknown Dataset: {}".format(dataset))


def get_device():
    if torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')
    return device


def find_adversarial_images(dataset, labels):
    ii, ll = get_samples(dataset, n_samples=10)
    cand_img, cand_lbl = [], []
    for i, l in enumerate(ll):
        if l != ll[0]:
            cand_img = [ii[0], ii[i]]
            cand_lbl = [ll[0], ll[i]]
    starts = []
    for l in labels:
        if l != cand_lbl[0]:
            starts.append(cand_img[0])
        else:
            starts.append(cand_img[1])
    return starts


def get_samples(dataset, n_samples=16, conf=None, model=None, samples_from=0):
    np.random.seed(42)
    if dataset == 'mnist':
        test_data = datasets.MNIST(root="data", train=False, download=True, transform=None)
        samples = test_data.data
        targets = test_data.test_labels
    elif dataset == 'cifar10':
        test_data = datasets.CIFAR10(root="data", train=False, download=True, transform=None)
        samples = test_data.data
        targets = test_data.targets
    else:
        raise RuntimeError('Unknown Dataset: {}'.format(dataset))
    if conf is None:
        indices = np.random.choice(len(test_data), n_samples, replace=False)
    else:
        indices = []
        i = 0
        candidates = np.random.choice(len(test_data), len(test_data), replace=False)
        while len(indices) != n_samples+samples_from:
            probs = model.get_probs(samples[candidates[i]][None]/255.0)
            if probs[0][targets[candidates[i]]] > conf:
                indices.append(candidates[i])
            i += 1

    if type(samples) is not np.ndarray:
        samples = samples.numpy()
    targets = np.array(targets)
    images = samples[indices] / 255.0
    labels = targets[indices]
    images = images[samples_from:]
    labels = labels[samples_from:]
    print("Images indices: ", indices)
    return images, labels


def save_adv_image(image, path, dataset='cifar10'):
    data = image * 255
    if dataset == 'mnist':
        img = Image.fromarray(np.uint8(data), 'L')
    else:
        img = Image.fromarray(np.uint8(data), 'RGB')
    img.save(path)


def show_image(image, dataset='cifar10'):
    data = image * 255
    if dataset == 'mnist':
        img = Image.fromarray(np.uint8(data), 'L')
    else:
        img = Image.fromarray(np.uint8(data), 'RGB')
    img.show()


def get_concat_h(im1, im2):
    dst = Image.new('L', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_concat_v(im1, im2):
    dst = Image.new('L', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


def get_concat_v_all(imgs):
    assert len(imgs) >= 2
    res = get_concat_v(imgs[0], imgs[1])
    for img in imgs[2:]:
        res = get_concat_v(res, img)
    return res


def save_concat_h(imgs: list, path=None):
    assert len(imgs) >= 2
    a0 = Image.fromarray(imgs[0].numpy() * 255)
    a1 = Image.fromarray(imgs[1].numpy() * 255)
    res = get_concat_h(a0, a1)
    for img in imgs[2:]:
        a = Image.fromarray(img.numpy() * 255)
        res = get_concat_h(res, a)
    if path is not None:
        res.save(path)
    return res


def one_big_image(exp_name):
    rows = []
    for row in range(0, 8):
        h = Image.open('{}/{}.png'.format(exp_name, 8 * row + 1))
        for i in range(2, 9):
            img = Image.open('{}/{}.png'.format(exp_name, 8 * row + i))
            h = get_concat_h(h, img)
        rows.append(h)
    cur = rows[0]
    for row in rows[1:]:
        cur = get_concat_v(cur, row)
    cur.save('{}/combined.png'.format(exp_name))


def save_all_images(exp_name, images, dataset):
    for i, image in enumerate(images):
        save_adv_image(image, "%s/%d.png" % (exp_name, i + 1), dataset)
    one_big_image(exp_name)
