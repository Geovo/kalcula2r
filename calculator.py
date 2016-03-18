# Author: Kristian Voshchepynets
# License: GPLv2 or later


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class CalculatorWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="k2 calculator")
        self.own_width = 0
        self.own_height = 0

        self.stack = []
        self.current = ""
        self.ops = ["+", "-", "/", "X", "%", "+/-", "="]
        self.nums = [str(x) for x in range(10)]

        self.grid_upper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.results = Gtk.Box(spacing=10)
        self.results_label = Gtk.Label("")
        self.results_label.set_markup("<span font='35'>0</span>")
        self.results_label.set_justify(Gtk.Justification.RIGHT)

        self.last_op = ""
        self.op_stack = []

        self.commands = Gtk.Grid()
        # first, set the proper window size
        self.set_proper_size()
        # now, create the first field
        self.first_layer()
        # here goes the output
        self.second_layer()

        # setup buttons
        self.setup_commands()


    def set_proper_size(self):
        screen = self.get_screen()
        #calculate the size of the window
        self.own_height = round(0.8 * screen.get_height())
        self.own_width = round(0.7 * screen.get_width())
        self.set_size_request(self.own_width, self.own_height)

    def first_layer(self):
        print("hello")
        self.grid_upper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        #print(dir(self.grid_upper))
        self.grid_upper.set_size_request(self.own_width, self.own_height * 0.15)
        self.add(self.grid_upper)
        demo_label = Gtk.Label("Placeholder for inputs")
        demo_label.set_justify(Gtk.Justification.RIGHT)
        # margin left
        self.grid_upper.add(Gtk.Label("   "))
        self.grid_upper.add(demo_label)

    def second_layer(self):
        print("second")
        self.results.set_size_request(self.own_width, round(self.own_height * 0.25))
        self.results_label.set_size_request(self.own_width - 20, round(self.own_height * 0.25))
        self.results_label.set_justify(Gtk.Justification.RIGHT)
        self.results_label.get_style().font_desc.set_size(30000)
        self.results.add(self.results_label)
        self.grid_upper.add(self.results)

        print(self.results_label.get_style().font_desc.get_size())

    def setup_commands(self):
        self.commands.set_size_request(self.own_width, round(self.own_height * 0.6))
        left_box = Gtk.Grid()
        left_box.set_size_request(round(self.own_width * 0.6), round(self.own_height * 0.6))


        nums = [str(x) for x in range(10)]
        nums.reverse()
        nums.append("+/-")
        nums.append("%")
        # temporary size vars
        h = round(self.own_height * 0.6 / 4)
        w = round(self.own_width / 5)

        #print(nums)
        self.grid_upper.add(self.commands)

        c = 0
        first_in_row = 0
        prev = False
        virgin = True

        for n in nums:
        #    print("c is %d" % c)
        #    print(first_in_row)
            button = Gtk.Button(label=n)
            button.connect("clicked", self.button_click)
            button.set_size_request(w, h)
            if c == 0 and virgin:
                first_in_row = button
                virgin = False

            if c == 3:
                left_box.attach_next_to(button, first_in_row, Gtk.PositionType.BOTTOM, 1, 1)
                first_in_row = button
                c = 0
            else:
                if not prev:
                    #self.commands.add(button)
                    left_box.add(button)
                else:
                    #self.commands.attach_next_to(button, prev, Gtk.PositionType.RIGHT, 1, 1)
                    left_box.attach_next_to(button, prev, Gtk.PositionType.RIGHT, 1, 1)

            c = c + 1
            prev = button

        self.commands.add(left_box)

        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        ops = ["/", "X", "+", "-"]

        for op in ops:
            button = Gtk.Button(label=op)
            button.connect("clicked", self.button_click)
            button.set_size_request(w, h)
            center_box.add(button)

        self.commands.add(center_box)

        # now add the right box
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        nu_ops = ["C", "AC", "Eco mode", "="]

        for op in nu_ops:
            button = Gtk.Button(label=op)
            button.connect("clicked", self.button_click)
            button.set_size_request(w, h)
            right_box.add(button)

        self.commands.add(right_box)

    def button_click(self, widget):
        print(widget.get_label())
        label = widget.get_label()

        if self.ops.__contains__(label):
            if len(self.stack) > 0:
                # check for precedence
                if self.precedence(label) >= self.precedence(self.stack[-1]):
                    self.stack.append(self.current)
                    self.stack.append(label)
                    self.current = ""
                else:
                    # the op has lower precedence
                    # push last found number to stack
                    print("sent solve_stack")
                    self.stack.append(self.current)
                    self.solve_stack()
                    # append label to stack afterwards
                    self.stack.append(label)
            else:
                self.stack.append(self.current)
                self.stack.append(label)
                self.current = ""
        elif self.nums.__contains__(label):
            self.current += label
        elif label == "C":
            self.current = ""
        elif label == "AC":
            self.current = ""
            self.stack = []
            self.op_stack = []
            self.last_op = ""

        print(self.stack)
        #print(self.op_stack)
        if self.current != "":
            self.results_label.set_markup("<span font='35'>%s</span>" % self.current)
        else:
            self.results_label.set_markup("<span font='35'>0</span>")

    def operate(self, a, b, op):
        print(a + " " + op + b)
        a = int(a)
        b = int(b)
        if op == "X":
            return a * b
        elif op == "/":
            return a / b
        elif op == "+":
            return a + b
        elif op == "-":
            return a - b
        elif op == "%":
            return a % b


    def precedence(self, op):
        if op == "+" or op == "-":
            return 2
        elif op == "X" or op == "/" or op == "%":
            return 3
        elif op == "=":
            return 1
        else:
            return 0

    def solve_stack(self):
        print("solving stack!!!")
        rpn = self.transform_rpn()
        return
        #rpn = ["5", "4", "+"]

        i = 0
        while len(rpn) > 1:
            if self.ops.__contains__(rpn[i]) and rpn[i] != "=" and rpn[i] != "+/-":
                # n is an op
                a = rpn.pop(i-1)
                i -= 1
                print("got a: " + a)
                b = rpn.pop(i-1)
                i -= 1
                print("got b: " + b)
                op = rpn.pop(i)
                print("got op: " + op)

                print("a: " + a + " " + op + " " + b)
                res = self.operate(a,b,op)
                rpn.insert(i,res)
            i += 1
            print(rpn)
            self.stack = [rpn[0]]


    def transform_rpn(self):
        out = []
        ops = []
        cp = self.stack

        for n in cp:
            if self.ops.__contains__(n):
                if len(ops) > 0:
                    if self.precedence(n) <= self.precedence(ops[-1]):
                        while self.precedence(ops[-1]) > self.precedence(n):
                            out.append(ops.pop(-1))
                            if len(ops) == 0:
                                break
                else:
                    ops.append(n)
            else:
                # must be a number
                out.append(n)

        # pop out the rest of the ops
        while len(ops) > 0:
            out.append(ops.pop(-1))
        print("rpn below:")
        print(out)
        return out

# basic setup
win = CalculatorWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
