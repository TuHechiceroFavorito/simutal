# Definition of elements
# Every element is a different object.
# inputs is a dict of <name-string>:<value-int>...,
# output_name is a string

# element class
class Element:
    def __init__(self, inputs, output_name, inv_mask):
        self.inputs = inputs
        self.output_name = output_name
        self.inv_mask = inv_mask
        self.type = None
        self.computable = False
        self.computed = False

    # Compute the output with current inputs
    def compute(self, io):
        for index, input in enumerate(self.inputs):
            if input in io["i"]:
                value = abs(self.inv_mask[index] - io["i"][input])
            elif input in io["internal"]:
                value = abs(self.inv_mask[index] - io["internal"][input])
            else:
                print(f"ERROR: input {input} is not being driven by any signal")
                exit()

            if self.statement(value):
                break

        if self.output_name in io["o"]:
            io["o"][self.output_name] = self.output
        elif self.output_name in io["internal"]:
            io["internal"][self.output_name] = self.output

        self.computed = False
        return io

# AND gate
class AND(Element):
    def statement(self, value):
        if value == 0:
            self.output = 0
            return True
        else:
            self.output = 1

# OR gate
class OR(Element):
    def statement(self, value):
        if value == 1:
            self.output = 1
            return True
        else:
            self.output = 0

#MULTIPLEXER
class MUX:
    def __init__(self, inputs, output_name, sel, inv_mask):
        self.inputs = inputs
        self.output_name = output_name
        self.sel = sel
        self.inv_mask = inv_mask
        self.type = "MUX"
        self.computable = False
        self.computed = False


# Class circuit. This holds the declarations and the processes
class Circuit:
    def __init__(self, filename):
        self.declaration, self.process = self.read_instructions(filename)
        self.elements = []
        self.read_instructions(filename)
        self.set_process()
        self.set_declarations()
        self.update_elements()

    def print_elements(self):
        for element in self.elements:
            print(element.type, element.inputs, element.output_name, element.computable, element.computed)

    def read_instructions(self, filename):
        with open(filename, "r") as f:
            instructions = f.read()
        declaration, process = instructions.split("set:")
        self.declaration = list(filter(None, declaration.split("\n")))
        self.process = list(filter(None, process.split("\n")))
        return declaration, process

    def set_declarations(self):
        # Read each instruction in the declaration
        for instr in self.declaration:
            # Ignore comments
            if "//" in instr:
                pass

            # Generate elements
            else:
                element_type = self.read_element(instr)
                inputs_var = instr.split(")")[0][1:].split(", ") # Get the input variables
                # inputs = {}
                inverting_mask = [] # Create mask to invert inputs
                # Save input values in temp list
                for var in range(len(inputs_var)):
                    # Check if the variable is inverted
                    if inputs_var[var][0] == "!":
                        inverting_mask.append(1)
                        inputs_var[var] = inputs_var[var][1:] # Get rid of the ! sign
                    else:
                        inverting_mask.append(0)

                    # The variable could be an input, an internal signal
                    # or an output that is being used as an input in another element

                    # # Look for the variable in input lists and save value in temp list
                    # if var in self.io["i"]:
                    #     inputs[var] = self.io["i"][var]

                    # # Look in output list and save value
                    # elif var in self.io["o"]:
                    #     inputs[var] = self.io["o"][var]

                    # # If not, it must be an internal signal
                    # else:
                    #     inputs[var] = self.io["internal"][var]


                output_var = instr.split("-> ")[-1] # Get the output variable from its declaration
                if output_var not in self.io["o"]:
                    self.io["internal"][output_var] = None

                if element_type == "AND":
                    new_element = AND(inputs_var, output_var, inv_mask=inverting_mask)

                elif element_type == "OR":
                    new_element = OR(inputs_var, output_var, inv_mask=inverting_mask)

                self.elements.append(new_element)

    # Reads the process instructions. Stores variables and sets values for inputs
    def set_process(self):
        # Variables to assign values to
        var_assign = []
        # Declared outputs
        output_decl = []

        # Read instructions from process
        for instruction in self.process:
            # Ignore comments
            if "//" in instruction:
                pass
            # Assignment statement
            elif "=" in instruction:
                var_assign.append(instruction)
            # Output declaration
            elif "->" in instruction:
                output_decl.append(instruction)

        # Inputs/output dictionary
        self.io ={
            "i":{},
            "internal":{},
            "o":{}
        }

        # Put output names in io output
        for out in output_decl:
            out_var = out.split("-> ")[1].split(", ")
            for var in out_var:
                self.io["o"][var] = None

        # Put input names and values in io input
        for assignment in var_assign:
            key, value = assignment.split("=")
            self.io["i"][key.lstrip()] = int(value.lstrip()) # Remove empty spaces

        return self.io

    def read_element(slef, definition):
        element = definition.split("->")[0][-1]
        if element == "&":
            return "AND"
        elif element == "|":
            return "OR"

    def update_elements(self):
        for element in self.elements:
            for input in element.inputs:
                if input in self.io["internal"] and self.io["internal"][input] != None or input in self.io["i"]:
                    element.computable = True

    def sim(self):
        computed = False
        while not computed:
            for element in self.elements:
                if element.computable and not element.computed:
                    computed = True
                    self.io = element.compute(self.io)
                else:
                    computed = False

            self.update_elements()

if __name__ == "__main__":
    circ = Circuit("test.utal")
    circ.print_elements()
    circ.sim()
    print(circ.io["internal"])
    print(circ.io["o"])