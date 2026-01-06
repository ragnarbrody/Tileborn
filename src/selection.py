class SelectionManager:
    def __init__(self):
        self.selected_entity = None

    def select(self, entity):
        self.selected_entity = entity
        print(f"Selecionado: {entity}")

    def clear(self):
        self.selected_entity = None

    def has_selection(self):
        return self.selected_entity is not None
