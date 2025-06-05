from agents.agent import Agent
import random

class RandomAgent(Agent):

    def __init__(self, player):
        super().__init__(player)

    def get_action(self, action_list, match, action_type=None):

        return random.choice(action_list)

    def get_chosen_card(self, cards, match, chosing_type=None):
        if not cards:
            return None
        return random.choice(cards)