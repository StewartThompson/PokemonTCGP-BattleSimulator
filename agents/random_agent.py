from agents.agent import Agent
import random

class RandomAgent(Agent):
    def get_action(self, action_list, match, action_type=None):

        return random.choice(action_list)

    def get_chosen_card(self, cards, match):
        if not cards:
            return None
        return random.choice(cards)