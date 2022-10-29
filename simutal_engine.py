# Definition of elements
# Every element is a different object.
# inputs is a dict of <name-string>:<value-int>...,
# output_name is a string


# AND gate
class AND():
    def __init__(self, inputs, output_name):
        self.inputs = inputs
        self.output_name = output_name
        
    def compute(self):
        for input in self.inputs.values():
            if input == 0:
                self.output = 0
                break
            else:
                self.output = 1

        return self.output

# OR gate
class OR():
    def __init__(self, inputs, output_name):
        self.inputs = inputs
        self.output_name = output_name
        
    def compute(self):
        for input in self.inputs.values():
            if input == 1:
                self.output = 1
                break
            else:
                self.output = 0

        return self.output

def read_instructions(filename):
    with open(filename, "r") as f:
        instructions = f.read()
    declaration, process = instructions.split("set:")
    declaration = list(filter(None, declaration.split("\n")))
    process = list(filter(None, process.split("\n")))
    return declaration, process

def run_process(process):
    assigns = []
    outs = []

    for instruction in process:
        if "//" in instruction:
            pass
        if "=" in instruction:
            assigns.append(instruction)
        if "->" in instruction:
            outs.append(instruction)

    io ={
        "i":{},
        "o":{}
    }

    for out in outs:
        out_var = out.split("-> ")[1].split(", ")
        for var in out_var:
            io["o"][var] = None

    for assignment in assigns:
        key, value = assignment.split("=")
        io["i"][key.lstrip()] = value.lstrip()

    return io

def read_gate(definition):
    gate = definition.split("->")[0][-1]
    if gate == "&":
        return "AND"
    elif gate == "|":
        return "OR"

def run_outputs(declaration, io):
    for line in declaration:
        if "//" in line:
            pass
        elif "MUX" in line:
            inputs_desc = line.split(")")[0][5:].split(", ")
            sel = line.split("?")[1].split()[0]
            out = line.split()[-1]
            if out in io["o"]:
                if inputs_desc[int(io["i"][sel])] in io["i"]:
                    io["o"][out] = int(io["i"][inputs_desc[int(io["i"][sel])]])
                else:
                    io["o"][out] = int(io["o"][inputs_desc[int(io["i"][sel])]])
            else:
                io["i"][out] = inputs_desc[int(io["i"][out])]
        else:
            gate = read_gate(line)
            inputs_desc = line.split(")")[0][1:].split(", ")
            inputs = []
            for input_var in inputs_desc:
                if input_var[0] == "!":
                    io["i"][input_var[1]] = (1-int(io["i"][input_var[1]]))
                    input_var = input_var[1]
                if input_var in io["i"]:
                    inputs.append((int(io["i"][input_var]))==1)
                else:
                    inputs.append((int(io["o"][input_var]))==1)

            out = line.split("-> ")[-1]

            result = None
            if gate == "AND":
                for input_val in inputs:
                    if input_val == 0:
                        result = 0
                        break
                    else:
                        result = 1

            elif gate == "OR":
                result = None
                for input_val in inputs:
                    if input_val == 1:
                        result = 1
                        break
                    else:
                        result = 0

            if out in io["o"]:
                io["o"][out] = result
            else:
                io["i"][out] = result

    return io


if __name__ == "__main__":
    and1 = AND({"A":1, "B":1}, "R")
    and1.compute()
    or1 = OR({"C":0, "R":and1.output}, "D")
    print(and1.compute())
    print(or1.compute())
    # import sys
    # if len(sys.argv) != 2:
    #     filename = "test.utal"
    # else:
    #     filename = sys.argv[1]
    # declaration, process = read_instructions(filename)
    # io = run_process(process)
    # io = run_outputs(declaration, io)
    # print(io["i"])
    # print(io["o"])