from pepipoenv import PePiPoEnv

import argparse
from random import randint
import os
from copy import deepcopy
from typing import Optional, Tuple
from pprint import pprint

import gymnasium as gym
import numpy as np
import torch
from torch.utils.tensorboard import SummaryWriter

from tianshou.data import Collector, VectorReplayBuffer
from tianshou.env import DummyVectorEnv
from tianshou.env.pettingzoo_env import PettingZooEnv
from tianshou.policy import (
    BasePolicy,
    DQNPolicy,
    MultiAgentPolicyManager,
    RandomPolicy,
)
from tianshou.trainer import OffpolicyTrainer
from tianshou.utils import TensorboardLogger
from tianshou.utils.net.common import Net

def generate_random_experiment_name() -> str:
    return f"exp_{randint(0, 9999)}"


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=1626)
    parser.add_argument('--eps-test', type=float, default=0.05, help="Set the eps for epsilon-greedy exploration")
    parser.add_argument('--eps-train', type=float, default=0.1, help="Set the eps for epsilon-greedy exploration")
    parser.add_argument('--buffer-size', type=int, default=20000)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--gamma', type=float, default=0.9, help='THe discount factor. A smaller gamma favors earlier win')
    parser.add_argument('--n-step', type=int, default=3)
    parser.add_argument('--target-update-freq', type=int, default=320)
    parser.add_argument('--epoch', type=int, default=50)
    parser.add_argument('--step-per-epoch', type=int, default=1000)
    parser.add_argument('--step-per-collect', type=int, default=50)
    parser.add_argument('--update-per-step', type=float, default=0.1)
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--hidden-sizes', type=int, nargs='*', default=[128, 128, 128, 128])
    parser.add_argument('--training-num', type=int, default=10, help="Number of train envs. Default 10")
    parser.add_argument('--test-num', type=int, default=10, help="Number of test envs. Default 10")
    parser.add_argument('--logdir', type=str, default='log', help="Directory to store tensorboard logs. Default ./log")
    parser.add_argument('--render', type=float, default=0.1, help="Renders a frame every x seconds. default 0.1s")
    parser.add_argument('--win-rate', type=float, default=0.9, help='the expected winning rate: Optimal policy can get 0.7')
    parser.add_argument('--watch', default=False, action='store_true', help='no training watch the play of pre-trained models')
    parser.add_argument('--agent-id', type=int, default=2, help='the learned agent plays as the agent_id-th player. Choices are 1 (player_0) and 2 (player_1).')
    parser.add_argument('--resume-path', type=str, default='', help='the path of agent pth file for resuming from a pre-trained agent')
    parser.add_argument('--opponent-path', type=str, default='', help='the path of opponent agent pth file for resuming from a pre-trained agent')
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument("--n-watch-eps", type=int, default=10, help="Number of episodes to watch. Default 10")
    return parser

def get_args() -> argparse.Namespace:
    parser = get_parser()
    return parser.parse_known_args()[0]


def get_agents(
    args: argparse.Namespace = get_args(),
    agent_learn: Optional[BasePolicy] = None,
    agent_opponent: Optional[BasePolicy] = None,
    optim: Optional[torch.optim.Optimizer] = None,
) -> Tuple[BasePolicy, torch.optim.Optimizer, list]:
    env = get_env()
    observation_space = env.observation_space['observation'] if isinstance(
        env.observation_space, gym.spaces.Dict
    ) else env.observation_space
    args.state_shape = observation_space.shape or observation_space.n
    args.action_shape = env.action_space.shape or env.action_space.n
    if agent_learn is None:
        # model
        net = Net(
            args.state_shape,
            args.action_shape,
            hidden_sizes=args.hidden_sizes,
            device=args.device
        ).to(args.device)
        if optim is None:
            optim = torch.optim.Adam(net.parameters(), lr=args.lr)
        agent_learn = DQNPolicy(
            model=net,
            optim=optim,
            discount_factor=args.gamma,
            action_space=env.action_space,
            estimation_step=args.n_step,
            target_update_freq=args.target_update_freq
        )
        if args.resume_path:
            agent_learn.load_state_dict(torch.load(args.resume_path))

    if agent_opponent is None:
        if args.opponent_path:
            agent_opponent = deepcopy(agent_learn)
            agent_opponent.load_state_dict(torch.load(args.opponent_path))
        else:
            agent_opponent = RandomPolicy(action_space=env.action_space)

    if args.agent_id == 1:
        agents = [agent_learn, agent_opponent]
    else:
        agents = [agent_opponent, agent_learn]
    policy = MultiAgentPolicyManager(agents, env)
    return policy, optim, env.agents

def get_env(render_mode=None):
    return PettingZooEnv(PePiPoEnv(render_mode=render_mode))


def train_agent(
    args: argparse.Namespace = get_args(),
    agent_learn: Optional[BasePolicy] = None,
    agent_opponent: Optional[BasePolicy] = None,
    optim: Optional[torch.optim.Optimizer] = None,
) -> Tuple[dict, BasePolicy]:
    
    # set experiment ID
    args.exp_id = generate_random_experiment_name()

    # ======== environment setup =========
    train_envs = DummyVectorEnv([get_env for _ in range(args.training_num)])
    test_envs = DummyVectorEnv([get_env for _ in range(args.test_num)])
    # seed
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    train_envs.seed(args.seed)
    test_envs.seed(args.seed)

    # ======== agent setup =========
    policy, optim, agents = get_agents(args, agent_learn=agent_learn, agent_opponent=agent_opponent, optim=optim)

    # ======== collector setup =========
    train_collector = Collector(
        policy,
        train_envs,
        VectorReplayBuffer(args.buffer_size, len(train_envs)),
        exploration_noise=True
    )
    test_collector = Collector(policy, test_envs, exploration_noise=True)
    t_training_steps = args.batch_size * args.training_num
    print(f"Training {args.exp_id} for {t_training_steps} total steps")
    train_collector.collect(n_step=t_training_steps)

    # ======== tensorboard logging setup =========
    log_path = os.path.join(args.logdir, args.exp_id)
    writer = SummaryWriter(log_path)
    writer.add_text("args", str(args))
    logger = TensorboardLogger(writer)

    # ======== callback functions used during training =========
    def save_best_fn(policy):
        if hasattr(args, 'model_save_path'):
            model_save_path = args.model_save_path
        else:
            model_save_path = os.path.join("models", args.exp_id,  "policy.pth")

        torch.save(policy.policies[agents[args.agent_id - 1]].state_dict(), model_save_path)

    def stop_fn(mean_rewards):
        return mean_rewards >= args.win_rate

    def train_fn(epoch, env_step):
        policy.policies[agents[args.agent_id - 1]].set_eps(args.eps_train)

    def test_fn(epoch, env_step):
        policy.policies[agents[args.agent_id - 1]].set_eps(args.eps_test)

    def reward_metric(rews):
        return rews[:, args.agent_id - 1]

    # trainer
    result = OffpolicyTrainer(
        policy,
        train_collector,
        test_collector,
        args.epoch,
        args.step_per_epoch,
        args.step_per_collect,
        args.test_num,
        args.batch_size,
        train_fn=train_fn,
        test_fn=test_fn,
        stop_fn=stop_fn,
        save_best_fn=save_best_fn,
        update_per_step=args.update_per_step,
        logger=logger,
        test_in_train=False,
        reward_metric=reward_metric,
        verbose=True
    ).run()

    return result, policy.policies[agents[args.agent_id - 1]]

# ======== a test function that tests a pre-trained agent ======
def watch(args: argparse.Namespace = get_args(),
    agent_learn: Optional[BasePolicy] = None,
    agent_opponent: Optional[BasePolicy] = None,
) -> None:
    env = get_env(render_mode="human")
    env = DummyVectorEnv([lambda: env])

    policy, optim, agents = get_agents(args, agent_learn=agent_learn, agent_opponent=agent_opponent)
    policy.eval()
    policy.policies[agents[args.agent_id - 1]].set_eps(args.eps_test)
    
    collector = Collector(policy, env, exploration_noise=True)
    result = collector.collect(n_episode=args.n_watch_eps, render=args.render)
    
    rews, lens = result["rews"], result["lens"]
    pprint(result)
    print(f"Final reward: {rews[:, args.agent_id - 1].mean()}, length: {lens.mean()}")
    print(f"Total wins: {sum([1 if arr[1] > 0 else 0 for arr in result['rews']])} / {result['n/ep']}")

# train the agent and watch its performance in a match!
args = get_args()

if args.watch: 
    watch(args)
else:
    result, agent = train_agent(args)



"""
I want every experiment to have a name and I want to be able to resume via name

# Trains new agent
    ```
    python train.py 
    ```

# Watch trained agent
    ```
    python train.py --watch --agent-name agent_123 
    ```
"""