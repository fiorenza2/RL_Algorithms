import argparse
import os
import gym
from gym.wrappers import Monitor
import gym_ple
from utils.helpers import *
from src.DQNAgent import *
import vizdoomgym


class RewardClipWrapper(gym.RewardWrapper):

    def __init__(self, env, living=False):
        super(RewardClipWrapper, self).__init__(env)
        self.living = living

    def reward(self, reward):
        if self.living:
            reward += 0.1
        reward = np.clip(reward, -1, 1)
        return reward


def setup_env_agent(env, monitor, reward_shaping, frame_stack, train):

    env = gym.make(env)
    if monitor:
        if not os.path.exists('./monitor_dir'):
            os.makedirs('./monitor_dir')
        env = Monitor(env, './monitor_dir/', force=True)
    if reward_shaping and train:    # only shape reward when training and when stipulated
        reward_shaping = True
    else:
        reward_shaping = False
    env = RewardClipWrapper(env, reward_shaping)
    if len(env.observation_space.shape) == 1:   # if we have rank of 1, it's a 1D space, so no need for convolutions
        conv = False
        input_dim = int(env.observation_space.shape[0])
    else:
        conv = True         # otherwise it's an image, so we'll have to add these
        input_dim = 84
    env.seed(0)
    agent = DQNAgent(env.action_space, frame_stack=frame_stack, conv=conv, input_dim=input_dim)
    return env, agent


def main(args):

    if args.mode == 'train':
        env, flappy_agent = setup_env_agent(env=args.env, monitor=args.monitor, reward_shaping=args.reward_shaping,
                                            frame_stack=args.frame_stack, train=True)
        flappy_runner = Trainer(env, flappy_agent, ReplayMemory, batch_size=args.batch_size,
                                memory_size=args.memory_size, final_exp_frame=args.final_exp_frame,
                                save_freq=args.save_freq, reset_target=args.reset_target,
                                max_ep_steps=args.max_ep_steps, gamma=args.gamma,
                                num_samples_pre=args.num_samples_pre, frame_skip=args.frame_skip)
    else:
        env, flappy_agent = setup_env_agent(env=args.env, monitor=args.monitor, reward_shaping=False,
                                            frame_stack=args.frame_stack, train=False)
        flappy_agent.eps = 0.0
        flappy_runner = Tester(env, flappy_agent, 84, max_ep_steps=args.max_ep_steps, frame_skip=args.frame_skip,
                               visualise=args.visualise)
        flappy_runner.load_model(args.testfile)

    flappy_runner.run_experiment(args.num_episodes)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run DQN on Flappy Bird, training/testing.')
    parser.add_argument('--env', type=check_env, default='FlappyBird-v0',
                        help='set to required environment')
    parser.add_argument('--mode', type=check_train_test, default='test',
                        help='set to train or test')
    parser.add_argument('--testfile', type=str, default='./params/trained_params_gym_fb.pth',
                        help='path of the trained model')
    parser.add_argument('--monitor', type=bool, default=False,
                        help='monitor the training/testing')
    parser.add_argument('--frame_skip', type=int, default=3,
                        help='how many frames to skip between actions (and apply the same action)')
    parser.add_argument('--reward_shaping', type=bool, default=True,
                        help='incorporate a reward for living')
    parser.add_argument('--frame_stack', type=int, default=4,
                        help='how many frames to stack together as input to DQN')
    parser.add_argument('--weight_decay', type=float, default = 0,
                        help='add weight-decay into the training')
    parser.add_argument('--lr_scheduler', type=list, default = None,
                        help='add a learning rate scheduler (important for cartpole)')
    parser.add_argument('--gamma', type=float, default=0.9,
                        help='future return discounting parameter')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='batch size from replay memory buffer')
    parser.add_argument('--memory_size', type=int, default=100000,
                        help='size of replay memory buffer')
    parser.add_argument('--max_ep_steps', type=int, default=1000000,
                        help='max number of steps per episode')
    parser.add_argument('--reset_target', type=int, default=10000,
                        help='steps before syncing the target network with the current DQN')
    parser.add_argument('--final_exp_frame', type=int, default=500000,
                        help='frame at which exploration hits the baseline (i.e., 0.01)')
    parser.add_argument('--save_freq', type=int, default=10000,
                        help='how often to save the models')
    parser.add_argument('--num_episodes', type=int, default=100000000,
                        help='how many episodes to run')
    parser.add_argument('--num_samples_pre', type=int, default=3000,
                        help='num of samples with a random policy to seed the replay memory buffer')
    parser.add_argument('--visualise', type=bool, default=False,
                        help='visualise trained agent')
    arguments = parser.parse_args()
    print(arguments.visualise)

    main(arguments)
