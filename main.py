
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
import matplotlib.pyplot as plt
from Game_Env import Game_Env
from TrainingLogger import TrainingLogger
from Policy_A2C import Policy_A2C

# Global:
NUM_OF_EPOCH = 600
NUM_OF_STEPS_PER_EPOCH = 3000
NUM_OF_ENV = 5
ENT_COEF = 0.015


def env_fn(render_type=None):
    return Game_Env(render_type, ran_house=False)

def plot_metrics(reward_history, iterations):
    plt.figure(figsize=(10, 6))

    # Plot Rewards
    plt.plot(range(1, iterations + 1), reward_history, marker="o", linestyle="-", color="blue", label="Episode Reward")
    plt.xlabel("Iteration")
    plt.ylabel("Total Reward")
    plt.title("Reward Over Iterations")
    plt.grid(True)
    plt.legend()

    plt.show()


def main():
    print(">>> creating env \n")
    vec_env = make_vec_env(env_fn, n_envs=NUM_OF_ENV)

    normalized_vec_env = VecNormalize(vec_env,
                                      norm_obs=True,  # normalize observations
                                      norm_reward=True,  # normalize rewards
                                      clip_obs=10.,
                                      clip_reward=10.)

    print(">>> creating policy \n")
    policy = Policy_A2C(normalized_vec_env, ENT_COEF)

    print(">>> setting up training loger \n")
    reward = []
    time = []

    print(">>> starting training: \n")
    for i in range(NUM_OF_EPOCH):

        print("     starting iteration: ", i+1)
        vec_env.reset()
        training_logger = TrainingLogger()
        policy.model.learn(total_timesteps=NUM_OF_STEPS_PER_EPOCH,
                           log_interval=50,
                           callback=training_logger)

        reward.append(training_logger.get_rewards())
        time.append(training_logger.get_episode_lengths())

    vec_env.close()

    name = "p_4"
    policy.save_model(name)
    normalized_vec_env.save(f"{name}_vec_normalize_try.pkl")  # Save normalization statistics

    # Plot rewards
    plot_metrics(reward, NUM_OF_EPOCH)
    plot_metrics(reward[1:], NUM_OF_EPOCH-1)

    # test policy:
    print(">>> setting up test \n")
    env = env_fn("human")
    vec_env = DummyVecEnv([lambda: env])
    normalized_vec_env = VecNormalize.load(f"{name}_vec_normalize.pkl", vec_env)
    normalized_vec_env.training = False  # Don't update normalization stats during testing
    normalized_vec_env.norm_reward = False  # Don't normalize rewards during testing

    policy.load_model(name)
    obs = normalized_vec_env.reset()
    terminated = False

    print(">>> stating test \n")
    while not terminated:
        action, _states = policy.model.predict(obs)
        obs, reward, terminated, info = normalized_vec_env.step(action)
    print(">>> finished test \n")



if __name__ == "__main__":
    main()


# TODO 1: fix bug that collides in corner
# TODO 2: check if need to normalize reward
# TODO 3: reward - add dist and dirct - dont think this is relevant
# TODO 4: start from different locations - maybe
# TODO 5: obs - mark target is found on the arrays them selve - dont think this is relevant
# TODO 6: compare A2C to other algorithms (DQN)

# TODO: make env easier (roooms) - did
# TODO: remove duplicate in find_target



# ----------------------
