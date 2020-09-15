class DefaultParams:
    """
    Do not change the default values. if you want different values, create a new instance and override
    """
    def __init__(self):
        self.num_iterations = 32
        self.gamma = 1.0
        self.input_image_path = None  # String
        self.input_image_label = None  # integer
        self.init_image_path = None
        self.search = 'infomax'  # binary or infomax
        self.hopskipjumpattack = False
        self.remember_all = False  # This should be true for HSJA

        # Hand-picking images
        self.orig_image_conf = 0.90

        # Specific to Noisy Models
        self.noise = 'bayesian'
        self.new_adversarial_def = True  # New Def: if p(true_label)<0.5 then its adversarial
        self.sampling_freq_binsearch = 1
        self.sampling_freq_approxgrad = None
        self.ask_human = False
        self.average = False
        self.slack = 0.0
        self.flip_prob = 0.2  # Specific to Stochastic Noise
        self.beta = 1.0  # Gibbs Distribution Parameter (p ~ exp(beta*x))
        # Specific to Info max procedure
        self.grid_size = 100

        # Specific to Experiment mode
        self.experiment_mode = True
        self.num_samples = 3
        self.experiment_name = None  # If not none it will override the command line argument

        # For book-keeping
        self.flags = dict(stats_cosines=False, stats_manifold=False)
