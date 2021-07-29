class AddIn:
    variables = {}
    addin_tip = ""
    add_in_name = ""

    def get_variables(self):
        return self.variables

    def get_description(self):
        return self.addin_tip

    def __init__(self):
        print("Initializing " + self.add_in_name)
