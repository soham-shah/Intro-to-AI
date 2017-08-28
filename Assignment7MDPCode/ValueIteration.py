#Artificial Intelligence: A Modern Approach

# Search AIMA
#AIMA Python file: mdp.py
'''
Soham Shah

1. What action is assigned in the terminal states?
    In the terminal state, the action assigned is +50

2. Where are the transition probabilities defined in the program, and what are
those probabilities?
    The transition probabilities are defined under def T in gridMDP. 
    They are, 80 percent of the time the horse will complete it's intended move,
    10 percent of the time he will go left of his intended move, and
    10 percent of the time he will go right of his intended move

3. What function needs to be called to run value iteration?
    to call the value iteration function, 
    we need to call value_iteration with the inputs of the MDP and the epsilon.
    Therefore, MDP needs to have been initialized which is done using the constructor. 

4. When you run value_iteration on the MDP provided, the results are stored in
a variable called myMDP. What is the utility of (0,1), (3, 1), and (2, 2)?
    (0, 1): 62.97
    (3, 1): 92.72
    (2, 2): None as we cannot traverse this location

5. How are actions represented, and what are the possible actions for each state
in the program?
    Actions are represented as vectors. For example (0,1) means moving north.
    For each state there are many possible actions. There are four actions, (0,1), (0,-1), (1,0), (-1,0)
    This shows up as orientations under utils.py
    Using the policy iteration algorithm, we calculate the best movement for each possible state. 
'''


"""Markov Decision Processes (Chapter 17)

First we define an MDP, and the special case of a GridMDP, in which
states are laid out in a 2-dimensional grid.  We also represent a policy
as a dictionary of {state:action} pairs, and a Utility function as a
dictionary of {state:number} pairs.  We then define the value_iteration
and policy_iteration algorithms."""

from utils import *

JUMP_VALUE = 1

class MDP:
    """A Markov Decision Process, defined by an initial state, transition model,
    and reward function. We also keep track of a gamma value, for use by
    algorithms. The transition model is represented somewhat differently from
    the text.  Instead of T(s, a, s') being  probability number for each
    state/action/state triplet, we instead have T(s, a) return a list of (p, s')
    pairs.  We also keep track of the possible states, terminal states, and
    actions for each state. [page 615]"""

    def __init__(self, init, actlist, terminals, gamma):
        update(self, init=init, actlist=actlist, terminals=terminals,
               gamma=gamma, states=set(), reward={})

    def R(self, state):
        "Return a numeric reward for this state."
        return self.reward[state]

    def T(state, action):
        """Transition model.  From a state and an action, return a list
        of (result-state, probability) pairs."""
        abstract

    def actions(self, state):
        """Set of actions that can be performed in this state.  By default, a
        fixed list of actions, except for terminal states. Override this
        method if you need to specialize by state."""
        if state in self.terminals:
            return [None]
        else:
            return self.actlist

class GridMDP (MDP):
    """A two-dimensional grid MDP, as in [Figure 17.1].  All you have to do is
    specify the grid as a list of lists of rewards; use None for an obstacle
    (unreachable state).  Also, you should specify the terminal states.
    An action is an (x, y) unit vector; e.g. (1, 0) means move east."""
    def __init__(self, grid, terminals, gamma, actlist, init=(0, 0) ):
        grid.reverse() ## because we want row 0 on bottom, not on top
        MDP.__init__(self, init, actlist=actlist,
                     terminals=terminals, gamma=gamma)
        update(self, grid=grid, rows=len(grid), cols=len(grid[0]))
        for x in range(self.cols):
            for y in range(self.rows):
                self.reward[x, y] = grid[y][x]
                if grid[y][x] is not None:
                    self.states.add((x, y))

    def T(self, state, action):
        if action == None:
            return [(0.0, state)]

        elif (JUMP_VALUE != 1):
            return [(0.5, self.go(state, action)),
                    (0.5, self.go(state, (0,0)))]

        else:
            return [(0.8, self.go(state, action)),
                    (0.1, self.go(state, turn_right(action))),
                    (0.1, self.go(state, turn_left(action)))]

    def go(self, state, direction):
        "Return the state that results from going in this direction."
        state1 = vector_add(state, direction)
        return if_(state1 in self.states, state1, state)

    def to_grid(self, mapping):
        """Convert a mapping from (x, y) to v into a [[..., v, ...]] grid."""
        return list(reversed([[mapping.get((x,y), None)
                               for x in range(self.cols)]
                              for y in range(self.rows)]))

    def to_arrows(self, policy):
        chars = {(JUMP_VALUE, 0):'>', (0, JUMP_VALUE):'^', (-JUMP_VALUE, 0):'<', (0, -JUMP_VALUE):'v', None: '.'}
        return self.to_grid(dict([(s, chars[a]) for (s, a) in policy.items()]))


def value_iteration(mdp, epsilon=0.001):
    "Solving an MDP by value iteration. [Fig. 17.4]"
    U1 = dict([(s, 0) for s in mdp.states])
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    while True:
        U = U1.copy()
        delta = 0
        for s in mdp.states:
            U1[s] = R(s) + gamma * max([sum([p * U[s1] for (p, s1) in T(s, a)])
                                        for a in mdp.actions(s)])
            delta = max(delta, abs(U1[s] - U[s]))
        if delta < epsilon * (1 - gamma) / gamma:
             return U

def best_policy(mdp, U):
    """Given an MDP and a utility function U, determine the best policy,
    as a mapping from state to action. (Equation 17.4)"""
    pi = {}
    for s in mdp.states:
        pi[s] = argmax(mdp.actions(s), lambda a:expected_utility(a, s, U, mdp))
    return pi

def expected_utility(a, s, U, mdp):
    "The expected utility of doing a in state s, according to the MDP and U."
    return sum([p * U[s1] for (p, s1) in mdp.T(s, a)])


def policy_iteration(mdp):
    "Solve an MDP by policy iteration [Fig. 17.7]"
    U = dict([(s, 0) for s in mdp.states])
    pi = dict([(s, random.choice(mdp.actions(s))) for s in mdp.states])
    while True:
        U = policy_evaluation(pi, U, mdp)
        unchanged = True
        for s in mdp.states:
            a = argmax(mdp.actions(s), lambda a: expected_utility(a,s,U,mdp))
            if a != pi[s]:
                pi[s] = a
                unchanged = False
        if unchanged:
            return pi

def policy_evaluation(pi, U, mdp, k=20):
    """Return an updated utility mapping U from each state in the MDP to its
    utility, using an approximation (modified policy iteration)."""
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    for i in range(k):
        for s in mdp.states:
            U[s] = R(s) + gamma * sum([p * U[s1] for (p, s1) in T(s, pi[s])])
    return U

def compareMDP(a,b):
    for firstIndex,item1 in enumerate(a):
        for secondIndex,item2 in enumerate(item1):
            if (item2!=b[firstIndex][secondIndex]):
                return False
    return True

def createMDP(nothing = 0, barn = 2, mountain = -1, snake = -0.5, wall = None, apple = 50, gam = 0.9, actlist=orientations):

    return GridMDP([[nothing, nothing, nothing, nothing, mountain, nothing, mountain, mountain, nothing, apple],
                    [wall, wall, mountain, mountain, nothing, snake, wall, nothing, wall, nothing],
                    [nothing, nothing, nothing, nothing, nothing, snake, wall, nothing, nothing, nothing],
                    [wall, barn, wall, wall, wall, snake, nothing, barn, wall, nothing],
                    [wall, nothing, nothing, nothing, nothing, wall, mountain, snake, mountain, nothing],
                    [nothing, snake, wall, nothing, nothing, wall, nothing, nothing, wall, nothing],
                    [nothing, snake, wall, nothing, mountain, wall, nothing, mountain, wall, wall],
                    [nothing, nothing, nothing, nothing, nothing, nothing, nothing, nothing, nothing, nothing]],
                        terminals=[(9,9)], gamma = gam, actlist=actlist)


"""
myMDP = GridMDP([[-0.04, -0.04, -0.04, +1],
                     [-0.04, None,  -0.04, -1],
                     [-0.04, -0.04, -0.04, -0.04]],
                    terminals=[(3,1),(3,2)])

U = value_iteration(myMDP, .001)
print U
"""

originalMDP = createMDP()
U = value_iteration(originalMDP, .001)
# print U

originalDirections = originalMDP.to_arrows(policy_iteration(originalMDP))
# Print oritigan directions
# for i in originalDirections:
#     print i

#Experiment 1: living reward
#adjust the value of non terminal states and check if anything changes
# print "Experiment #1 Results:"
# for i in range(-10,11,1):
#   testMDP_Map = createMDP(nothing = i/10.0)
#   testDirections = testMDP_Map.to_arrows(policy_iteration(testMDP_Map))

#   if (not compareMDP(originalDirections,testDirections)):
#       print "Nothing = " + str(i/100.0)

# # Experiment #2 - Value of Gamma
# # adjust the value of gamma states and check if anything changes
# print "Experiment #2 Results:"
# for i in range(850,950,1):
#   testMDP_Map = createMDP(gam = i/1000.0)
#   testDirections = testMDP_Map.to_arrows(policy_iteration(testMDP_Map))

#   if (not compareMDP(originalDirections,testDirections)):
#       print "Gamma = " + str(i/1000.0)

# Experiment #3 - different movements
# Add the ability to jump for the horse
# print "Experiment #3 Results:"
# JUMP_VALUE = 2
# testMDP_Map = createMDP(actlist = [(2,0), (0, 2), (-2, 0), (0, -2)])
# testDirections =  testMDP_Map.to_arrows(policy_iteration(testMDP_Map))
# print (testDirections)



'''
#AI: A Modern Approach by Stuart Russell and Peter Norvig	Modified: Jul 18, 2005

The data matrix you will need for the assignment:

[0, 0, 0, 0, -1, -0.9, -1, -1, -0.9, 50],
[None, None, -1, -1, 0.9, -.5, None, 0.9, None, 0],
[0, 0, 0, 0, 0, -.5, None, 0, 0, 0],
[None, 2, None, None, 0, -.5, 0, 2, None, 0],
[0, 0, None, 0, 0, None, -1, -.5, -1, 0],
[0, -.5, None, 0, 0, None, 0, 0, None, 0],
[0, -.5, None, 0, -1, None, 0, -1, None, None],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

'''