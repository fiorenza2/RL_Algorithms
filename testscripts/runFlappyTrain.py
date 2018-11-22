from ple.games.flappybird import FlappyBird
from ple import PLE
from DQNAgent import *
import os

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.environ["SDL_VIDEODRIVER"] = "dummy"

# #===============================DEBUG BEGIN============================##
# import sys
# sys.path.append("pycharm-debug-py3k.egg")
# import pydevd
#
# pydevd.settrace('127.0.0.1', port=5678, stdoutToServer=True,
# stderrToServer=True)
# #================================DEBUG END=============================##


game = FlappyBird()
p = PLE(game, fps=30, display_screen=False, frame_skip=3)
z = p.game.rewards
z['tick'] = 0.1
p.game.adjustRewards(z)
p.init()

flappy_agent = DQNAgent(p.getActionSet(), frame_stack=4)

flappy_trainer = Trainer(p, flappy_agent, ReplayMemory, batch_size=32, memory_size=100000, final_exp_frame=500000,
                         save_freq=10000, reset_target=10000)

flappy_trainer.run_experiment(100000000)


