import threading
import time
from typing import Optional, List, Any
from agents.human_agent import HumanAgent


class WebHumanAgent(HumanAgent):
    """Web-enabled human agent that uses the Flask interface for user input"""
    
    def __init__(self, player, web_gui=None):
        super().__init__(player)
        self.web_gui = web_gui
        
    def set_web_gui(self, web_gui):
        """Set the web GUI interface"""
        self.web_gui = web_gui
        
    def get_action(self, actions, match, context=None):
        """Get action from web GUI instead of terminal"""
        if not self.web_gui:
            # Fallback to terminal if no GUI
            return super().get_action(actions, match, context)
            
        # Log the action request
        self.web_gui.log_message(f"Choose action (context: {context})")
        
        # Show options and wait for user selection
        return self._get_user_choice_web(actions, context or "action")
        
    def get_chosen_card(self, options, match, context=None):
        """Get card choice from web GUI instead of terminal"""
        if not self.web_gui:
            # Fallback to terminal if no GUI
            return super().get_chosen_card(options, match, context)
            
        if not options:
            return None
            
        # Log the choice request
        self.web_gui.log_message(f"Choose from {len(options)} options (context: {context})")
        
        # Show options and wait for user selection
        return self._get_user_choice_web(options, context or "option")
        
    def _get_user_choice_web(self, options, context):
        """Get user choice through web GUI interface"""
        # Create callback function that will be called when user makes choice
        def on_choice_made(choice):
            return choice
            
        # Show options in web GUI and wait for response
        return self.web_gui.show_options(options, context, on_choice_made)
        
    def _display_game_state(self, match):
        """Override to skip terminal display since web GUI handles this"""
        pass  # Web GUI updates automatically 