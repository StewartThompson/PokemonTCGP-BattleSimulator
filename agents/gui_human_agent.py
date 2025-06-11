import threading
import time
from typing import Optional, List, Any
from agents.human_agent import HumanAgent


class GUIHumanAgent(HumanAgent):
    """GUI-enabled human agent that uses the Tkinter interface for user input"""
    
    def __init__(self, player, gui=None):
        super().__init__(player)
        self.gui = gui
        self.waiting_for_input = False
        self.user_choice = None
        self.input_lock = threading.Lock()
        
    def set_gui(self, gui):
        """Set the GUI interface"""
        self.gui = gui
        
    def get_action(self, actions, match, context=None):
        """Get action from GUI instead of terminal"""
        if not self.gui:
            # Fallback to terminal if no GUI
            return super().get_action(actions, match, context)
            
        # Update GUI display
        self.gui.update_display()
        
        # Log the action request
        self.gui.log_message(f"Choose action (context: {context})")
        
        # Show options and wait for user selection
        return self._get_user_choice_gui(actions, context or "action")
        
    def get_chosen_card(self, options, match, context=None):
        """Get card choice from GUI instead of terminal"""
        if not self.gui:
            # Fallback to terminal if no GUI
            return super().get_chosen_card(options, match, context)
            
        if not options:
            return None
            
        # Update GUI display
        self.gui.update_display()
        
        # Log the choice request
        self.gui.log_message(f"Choose from {len(options)} options (context: {context})")
        
        # Show options and wait for user selection
        return self._get_user_choice_gui(options, context or "option")
        
    def _get_user_choice_gui(self, options, context):
        """Get user choice through GUI interface"""
        with self.input_lock:
            self.waiting_for_input = True
            self.user_choice = None
            
            # Create callback function
            def on_choice_made(choice):
                self.user_choice = choice
                self.waiting_for_input = False
                
            # Show options in GUI
            self.gui.show_options(options, context, on_choice_made)
            
            # Wait for user to make a choice
            while self.waiting_for_input:
                time.sleep(0.1)
                # Allow GUI to update
                if hasattr(self.gui, 'root'):
                    self.gui.root.update()
                    
            return self.user_choice
            
    def _display_game_state(self, match):
        """Override to use GUI display instead of terminal"""
        if self.gui:
            self.gui.update_display()
        else:
            # Fallback to terminal display
            super()._display_game_state(match) 