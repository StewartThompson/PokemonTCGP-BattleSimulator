class Tool:
    def __init__(self, tool_id, name, effect, special_values=None):
        self.card_type = "tool"
        self.tool_id = tool_id
        self.name = name
        self.effect = effect
        self.special_values = special_values

    def __str__(self):
        return f"{self.name} ({self.effect})"

    def __repr__(self):
        return str(self)
