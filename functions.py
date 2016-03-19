# here go the functions and their values
class Function:
    def __init__(self, name, func, params):
        self.name = name
        self.run = func
        self.params = params[1:-1].split(", ") # skip the whitespace
        print(self.params)

    def run_with_array(self, ary):
        out = "("
        for i, a in enumerate(ary):
            out += self.params[i] + "=" + str(a) + ","
        out = out[:-1] + ")"
        #print(out)
        res = eval("self.run" + out)
        #print(res)
        return str(res)


#f = Function("Percent", lambda s, perc, years: return s * perc ** years, 3)

# Function syntax:
# Percent | s, perc, years | s + perc ** years

class FunctionParser:
    def __init__(self):
        print("Parser ready!")

    def parse(self, input):
        a = input.split("|")
        print(a)
        name = a[0][:-1] # remove the trailing space
        count = len(",".split(a[1]))
        lambd = eval("lambda " + a[1][:-1] + ":" + a[2])
        return Function(name, lambd, a[1])

#fp = FunctionParser()
#f1 = fp.parse("Percent | s, perc, years | s + perc ** years")
#print(f1.run(100,5,1.15))
#print(f1.run_with_array([100,5,1.15]))
