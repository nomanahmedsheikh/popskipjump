#!/usr/bin/env python3
"""
A simple example that demonstrates how to run a single attack against
a PyTorch ResNet-18 model for different epsilons and how to then report
the robust accuracy.
"""
import torch
import numpy as np
from tqdm import tqdm
from scipy import stats
import torchvision.models as models
import eagerpy as ep
from foolbox import PyTorchModel, accuracy, samples
from foolbox.attacks import BoundaryAttack, L2BrendelBethgeAttack, L2PGD
from img_utils import get_samples
from model_factory import get_model
from foolbox.criteria import Misclassification


class Noisy(Misclassification):
    """Considers those perturbed inputs adversarial whose predicted class
    differs from the label.

    Args:
        labels: Tensor with labels of the unperturbed inputs ``(batch,)``.
    """
    def __init__(self, labels, flip_prob, rep):
        super().__init__(labels)
        self.flip_prob = flip_prob
        self.calls = 0
        self.rep = rep

    def __call__(self, perturbed, outputs):
        outputs_, restore_type = ep.astensor_(outputs)
        del perturbed, outputs

        classes = outputs_.numpy().argmax(axis=-1)
        assert classes.shape == self.labels.shape
        prediction = np.tile(classes.reshape(-1, 1), (1, self.rep))
        n_samples = self.labels.shape[0]
        self.calls += n_samples * self.rep
        n_classes = outputs_.shape[-1]
        rand_pred = np.random.randint(n_classes-1, size=(n_samples, self.rep))
        rand_pred[rand_pred == self.labels.numpy()[:,None]] = n_classes - 1
        indices_to_flip = np.random.rand(n_samples, self.rep) < self.flip_prob
        prediction[indices_to_flip] = rand_pred[indices_to_flip]
        prediction = stats.mode(prediction, axis=1)[0].flatten()
        is_adv = ep.astensor(torch.tensor(prediction)) != self.labels
        return restore_type(is_adv)


def search_boundary(x_star, x_t, theta_det, true_label, model):
    high, low = 1, 0
    while high - low > theta_det:
        mid = (high + low) / 2.0
        x_mid = (1 - mid) * x_star + mid * x_t
        pred = torch.argmax(model.get_probs(x_mid[None])[0])
        if pred == true_label:
            low = mid
        else:
            high = mid
    out = (1 - high) * x_star + high * x_t
    return out


def project(x_star, x_t, label, theta_det, model):
    x_t = x_t[0]
    probs = model.get_probs(x_t[None])
    if torch.argmax(probs[0]) == label:
        c = 0.25
        x_prev = x_star
        while True:
            x_tt = x_t + c * (x_t - x_star) / np.linalg.norm(x_t - x_star)
            x_tt = np.clip(x_tt, 0, 1)
            if np.max(np.abs(x_tt - x_prev)) == 0:
                break
            x_prev = x_tt
            pred = torch.argmax(model.get_probs(x_tt[None])[0])
            if pred != label:
                x_tt = search_boundary(x_t, x_tt, theta_det, label, model)
                break
            c += c
    else:
        x_tt = search_boundary(x_star, x_t, theta_det, label, model)
    return x_tt


def main() -> None:
    # instantiate a model (could also be a TensorFlow or JAX model)
    det_model = get_model(key='mnist_cnn', dataset='mnist', noise='deterministic')
    fmodel = PyTorchModel(det_model.model, bounds=(0, 1))
    n_samples = 100
    imgs, lbls = get_samples('mnist', n_samples=n_samples, conf=0.75, model=det_model, samples_from=0)
    images, labels = ep.astensors(torch.tensor(imgs[:, None, :, :], dtype=torch.float32), torch.tensor(lbls))
    clean_acc = accuracy(fmodel, images, labels)
    print(f"clean accuracy:  {clean_acc * 100:.1f} %")

    # apply the attack
    d = 28*28
    theta = 1 / (d*np.sqrt(d))
    flips = [0]
    BD, MC = {}, {}
    for rep in [1]:
        BD[rep] = {}
        MC[rep] = {}
        for flip in flips:
            attack = BoundaryAttack()
            epsilons = [None]
            criterion = Noisy(labels, flip, rep)
            raw_advs, clipped_advs, success = attack(fmodel, images, criterion, epsilons=epsilons)
            border_distance = torch.zeros(n_samples)
            for i, x_t in tqdm(enumerate(raw_advs[0])):
                x_tt = project(imgs[i], x_t.numpy(), lbls[i], theta, det_model)
                border_distance[i] = np.linalg.norm(x_tt - imgs[i]) ** 2 / d
            print(f'Flip={flip}, Rep={rep}', end='\t')
            print("Border-Distance", np.median(border_distance), end='\t')
            print('Model-Calls', criterion.calls)
            BD[rep][flip] = border_distance
            MC[rep][flip] = criterion.calls
    torch.save({'BD': BD, 'MC': MC}, open('aistats/brendell2.pkl', 'wb'))

    D = torch.load(open('aistats/brendell2.pkl', 'rb'))
    BD, MC = D['BD'], D['MC']
    for rep in BD:
        for flip in BD[rep]:
            n_images = len(BD[rep][flip])
            perc_50 = np.median(BD[rep][flip])
            perc_40 = np.percentile(BD[rep][flip], 40)
            perc_60 = np.percentile(BD[rep][flip], 60)
            calls = MC[rep][flip]/n_images
            print(f'rep={rep} flip={flip}\t{perc_40}\t{perc_50}\t{perc_60}\t{calls}')

if __name__ == "__main__":
    main()