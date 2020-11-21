import torch


class DefaultParams:
    """
    Do not change the default values. if you want different values, create a new instance and override
    """

    def __init__(self):
        self.attack = 'popskip'
        self.dataset = 'mnist'
        self.model_keys: dict = {'mnist': ['mnist_noman'], 'cifar10': ['cifar10']}
        self.num_iterations = 32
        self.bounds = (0, 1)
        self.gamma = 1.0
        self.input_image_path = None  # String
        self.input_image_label = None  # integer
        self.init_image_path = None
        self.hsja_repeat_queries = 1  # parameter for HSJ-repeated

        self.initial_num_evals = 100  # B_0 (i.e. num of queries for first iteration of original HSJA)
        self.max_num_evals = 50000  # Maximum queries allowed in Approximate Gradient Step
        # self.stepsize_search = "geometric_progression"  # Deprecating this
        self.distance = "MSE"  # Distance metric
        self.batch_size = 256

        # Specific to encoder
        self.encoder_type = 'identity'
        self.encoder_target_dim = 784

        # Hand-picking images
        self.orig_image_conf = 0.75

        # Specific to Noisy Models
        self.noise = 'bayesian'
        self.new_adversarial_def = True  # New Def: if p(true_label)<0.5 then its adversarial
        self.sampling_freq_binsearch = 1
        self.ask_human = False
        self.slack = 0.0
        self.flip_prob = 0.2  # Specific to Stochastic Noise
        self.beta = 1.0  # Gibbs Distribution Parameter (p ~ exp(beta*x))

        # Specific to Info max procedure
        self.grid_size = {'mnist': 100, 'cifar10': 300}
        self.prior_frac = 1
        self.queries = 1
        self.infomax_stop_criteria = "estimate_fluctuation"

        # Specific to Approximate Gradient
        self.grad_queries = 1

        self.theta_fac = -1

        # Specific to Experiment mode
        self.experiment_mode = True
        self.num_samples = 3
        self.samples_from = 0  # Number of sample to skip. This is for merging
        self.experiment_name = None  # If not none it will override the command line argument
