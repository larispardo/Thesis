import gym
import gym_gvgai
import matplotlib.pyplot as plt
import time


def show_state(env, step=0, score=""):
    plt.figure()
    plt.clf()
    plt.imshow(env.render(mode="rgb_array"))

    plt.title(f"step: {step}, score: {score}")
    plt.axis("off")
    plt.show()
    time.sleep(.1)
    plt.close()

env = gym.make("gvgai-thesis01-lvl1-v1") # Acá puedes cambiar el nivel que quieres jugar (lvl0, lvl1, ...).

'''
env.reset()
sum_score = 0
for i in range(2000):
    show_state(env, step=i, score=sum_score)
    action_id = env.action_space.sample()
    state, reward, is_over, debug = env.step(action_id)
    sum_score += reward
    # print(f"action: {action_id}, reward: {reward}, score: {sum_score}")
    if is_over:
        print(f"Game over at tick {i}")
        break
'''
if not hasattr(env.action_space, 'n'):
    raise Exception('Keyboard agent only supports discrete action spaces')
ACTIONS = env.action_space.n
SKIP_CONTROL = 0    # Use previous control decision SKIP_CONTROL times, that's how you
                    # can test what skip is still usable.

human_agent_action = 0
human_wants_restart = False
human_sets_pause = False

def key_press(key, mod):
    global human_agent_action, human_wants_restart, human_sets_pause
    if key==0xff0d: human_wants_restart = True
    if key==32: human_sets_pause = not human_sets_pause
    a = int( key - ord('0') )
    if a <= 0 or a >= ACTIONS: return
    human_agent_action = a

def key_release(key, mod):
    global human_agent_action
    a = int( key - ord('0') )
    if a <= 0 or a >= ACTIONS: return
    if human_agent_action == a:
        human_agent_action = 0

env.render()
env.unwrapped.viewer.window.on_key_press = key_press
env.unwrapped.viewer.window.on_key_release = key_release

def rollout(env):
    global human_agent_action, human_wants_restart, human_sets_pause, val
    human_wants_restart = False
    obser = env.reset()
    skip = 0
    total_reward = 0
    total_timesteps = 0
    while 1:
        if not skip:
            #print("taking action {}".format(human_agent_action))
            a = human_agent_action
            total_timesteps += 1
            skip = SKIP_CONTROL
        else:
            skip -= 1

        obser, r, done, info = env.step(a)
        if r != 0:
            print("reward %0.3f" % r)
        total_reward += r
        window_still_open = env.render()
        if window_still_open==False: return False
        if done:
            return True
            break
        if human_wants_restart: break
        while human_sets_pause:
            time.sleep(0.1)
        time.sleep(0.1)
    print("timesteps %i reward %0.2f" % (total_timesteps, total_reward))

print("ACTIONS={}".format(ACTIONS))
print("Press keys 1 2 3 ... to take actions 1 2 3 ...")
print("No keys pressed is taking action 0")
val = 0
while 1:
    window_still_open = rollout(env)
    if window_still_open:
        env.close()
        val += 1
        env = gym.make("gvgai-thesis1-lvl"+ str(val%5)+"-v0")
        ACTIONS = env.action_space.n
        SKIP_CONTROL = 0  # Use previous control decision SKIP_CONTROL times, that's how you
        # can test what skip is still usable.

        human_agent_action = 0
        human_wants_restart = False
        human_sets_pause = False
        env.render()
        env.unwrapped.viewer.window.on_key_press = key_press
        env.unwrapped.viewer.window.on_key_release = key_release
    if window_still_open==False: break