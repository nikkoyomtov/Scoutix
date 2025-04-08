
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

class TrainingLogger(BaseCallback):
    """
    Custom callback to log rewards, episode lengths, and loss during training.
    """

    def __init__(self, verbose=0):
        super(TrainingLogger, self).__init__(verbose)
        self.losses = []
        self.current_episode_reward = 0
        self.current_episode_length = 0

    def _on_step(self) -> bool:
        # Log rewards and steps
        reward = np.mean(self.locals["rewards"])
        self.current_episode_reward += reward
        self.current_episode_length += 1
        # print("current reward: ", self.current_episode_reward)

        # Capture loss (SB3 doesn't expose this directly, but we extract it)
        loss = self.logger.name_to_value.get("loss", None)
        if loss is not None:
            self.losses.append(loss)

        return True

    def get_rewards(self):
        return self.current_episode_reward

    def get_episode_lengths(self):
        return self.current_episode_length

    def get_losses(self):
        return self.losses
