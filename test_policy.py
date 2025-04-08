from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
import matplotlib.pyplot as plt
from Game_Env import Game_Env
from TrainingLogger import TrainingLogger
from Policy_A2C import Policy_A2C


def env_fn(render_type=None):
    return Game_Env(render_type, ran_house=False)



if __name__ == "__main__":

    env = env_fn("human")
    vec_env = DummyVecEnv([lambda: env])
    # normalized_vec_env = VecNormalize.load("p_2_vec_normalize.pkl", vec_env) # rl alg
    normalized_vec_env = VecNormalize.load("p_4_vec_normalize.pkl", vec_env)
    normalized_vec_env.training = False  # Don't update normalization stats during testing
    normalized_vec_env.norm_reward = False  # Don't normalize rewards during testing

    policy = Policy_A2C(normalized_vec_env)
    policy.load_model("p_2")
    obs = normalized_vec_env.reset()
    terminated = False

    print(">>> stating test \n")
    while not terminated:
        action, _states = policy.model.predict(obs)
        obs, reward, terminated, info = normalized_vec_env.step(action)
    print(">>> finished test \n")

