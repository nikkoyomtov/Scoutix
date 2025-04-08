
from stable_baselines3 import A2C


class Policy_A2C:
    def __init__(self, env, ENT_COEF=0.01):
        self.model = A2C("MlpPolicy", env, verbose=2, ent_coef=ENT_COEF, policy_kwargs=dict(net_arch=[64, 128, 64]))

    def load_model(self, model_path):
        self.model = A2C.load(model_path)

    def save_model(self, model_path):
        self.model.save(model_path)