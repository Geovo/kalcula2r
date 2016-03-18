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

        self.edit_current = True

        self.commands = Gtk.Grid()
        # first, set the proper window size
        self.set_proper_size()
        # now, create the first field
        self.first_layer()
        # here goes the output
        self.second_layer()

        # setup buttons
        self.setup_commands()
        # enable keyboard events
        self.connect("key-press-event", self.key_pressed)


    def set_proper_size(self):
        screen = self.get_screen()
        #calculate the size of the window
        self.own_height = round(0.8 * screen.get_height())
        self.own_width = round(0.7 * screen.get_width())
        self.set_size_request(self.own_width, self.own_height)

    def first_layer(self):
        self.grid_upper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.grid_upper.set_size_request(self.own_width, self.own_height * 0.15)
        self.add(self.grid_upper)
        demo_label = Gtk.Label("Placeholder for inputs")
        demo_label.set_justify(Gtk.Justification.RIGHT)
        # margin left
        self.grid_upper.add(Gtk.Label("   "))
        self.grid_upper.add(demo_label)

    def second_layer(self):
        self.results.set_size_request(self.own_width, round(self.own_height * 0.25))
        self.results_label.set_size_request(self.own_width - 20, round(self.own_height * 0.25))
        self.results_label.set_justify(Gtk.Justification.RIGHT)
        self.results_label.get_style().font_desc.set_size(30000)
        self.results.add(self.results_label)
        self.grid_upper.add(self.results)

        #print(self.results_label.get_style().font_desc.get_size())

    def setup_commands(self):
        self.commands.set_size_request(self.own_width, round(self.own_height * 0.6))
        left_box = Gtk.Grid()
        left_box.set_size_request(round(self.own_width * 0.6), round(self.own_height * 0.6))


        #nums = [str(x) for x in range(10)]
        nums = ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0"]
        #nums.reverse()
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
        nu_ops = [".", "AC", "Eco mode", "="]

        for op in nu_ops:
            button = Gtk.Button(label=op)
            button.connect("clicked", self.button_click)
            button.set_size_request(w, h)
            right_box.add(button)

        self.commands.add(right_box)

    def button_click(self, widget):
        label = widget.get_label()

        if label == "=":
            self.equalize()
        elif label == "+/-":
            # simply swap the sign of current
            if self.current[0] == "-":
                self.current = self.current[1:]
            else:
                self.current = "-" + self.current
        elif self.ops.__contains__(label):
            self.add_operator(label)
        elif self.nums.__contains__(label):
            self.edit_number(label)
        elif label == ".":
            self.edit_number(".")
        elif label == "AC":
            self.current = ""
            self.stack = []
            self.op_stack = []
            self.last_op = ""

        self.update_label()

    def operate(self, a, b, op):
        #print(a + " " + op + b)
        a = float(a)
        b = float(b)
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
        rpn = self.transform_rpn()

        i = 0
        while len(rpn) > 1:
            print(self.stack)
            if self.ops.__contains__(rpn[i]) and rpn[i] != "=" and rpn[i] != "+/-":
                # n is an op
                a = rpn.pop(i-1)
                i -= 1
                b = rpn.pop(i-1)
                i -= 1
                op = rpn.pop(i)

                res = self.operate(b,a,op)
                # make sure you add ints if they don't need the .0
                if res == round(res):
                    res = int(res)
                rpn.insert(i,str(res))
            i += 1
            self.stack = [rpn[0]]
            self.current = rpn[0]


    def transform_rpn(self):
        out = []
        ops = []
        cp = self.stack

        while len(cp) > 0:
            n = cp.pop(0)
            if self.ops.__contains__(n):
                # is an operator
                if len(ops) == 0:
                    ops.append(n)
                elif self.precedence(n) < self.precedence(ops[-1]):
                    # pop out all elements from ops
                    while len(ops) > 0:
                        # this works only if ops has at least one op
                        out.append(ops.pop(-1))
                    # in the end append n to ops
                    ops.append(n)
                else:
                    out.append(n)
            else:
                # is a number
                out.append(n)

        # pop out the rest of the ops
        while len(ops) > 0:
            out.append(ops.pop(-1))
        return out

    def key_pressed(self, widget, event):
        # get the code
        key = event.keyval
        res = ""
        enter = False
        if key >= 48 and key <= 57:
            # qwerty digits
            self.edit_number(str(key - 48))
        elif key >= 65456 and key <= 65465:
            # numpad digits
            self.edit_number(str(key - 65456))
        elif key == 65233 or key == 65421 or key == 65469:
            # next goes enter or '='
            self.current = self.current[:-1]
            self.equalize()
            enter = True
        elif key == 46 or key == 65454:
            # dot operator
            self.edit_number(".")
        elif key == 47 or key == 65455:
            # division
            res = "/"
        elif key == 43 or key == 65451:
            # addition
            res = "+"
        elif key == 45 or key == 65453:
            # subtraction
            res = "-"
        elif key == 42 or key == 65450:
            # multiplication
            res = "X"
        elif key == 37:
            # modulo
            res = "%"
        elif key == 65288:
            # do some backspacing
            self.current = self.current[:-1]

        # if not a number, but an op:
        if res != "":
            self.add_operator(res)
        self.update_label()

        if enter:
            return True

    def update_label(self):
        if self.current == "":
            self.results_label.set_markup("<span font='35'>0</span>")
        else:
            self.results_label.set_markup("<span font='35'>" + self.current + "</span>")

    # here go the capsules for our main methods
    def equalize(self):
        if len(self.stack) > 0 and self.current != "":
            # if current is not empty, parse the equation with it appended
            # else simply do nothing
            self.stack.append(self.current)
            self.current = ""
            self.solve_stack()
            self.edit_current = False
        #elif len(self.stack) == 1:
        #    print("only one element in stack")

    def add_op(self, op):
        if len(self.stack) > 1:
            if self.ops.__contains__(self.stack[-1]):
                # swap the op
                self.stack[-1] = op
            else:
                self.stack.append(op)

    def add_operator(self, label):
        self.edit_current = False
        if len(self.stack) > 0:
            # first, make sure that you don't add the same elem twice
            if len(self.stack) == 1 and self.stack[-1] == self.current:
                self.stack.append(label)
                self.current = ""
            # check for precedence
            elif self.precedence(label) >= self.precedence(self.stack[-1]):
                self.stack.append(self.current)
                self.stack.append(label)
                self.current = ""
            else:
                # the op has lower precedence
                # push last found number to stack
                self.stack.append(self.current)
                self.solve_stack()
                # append label to stack afterwards
                self.stack.append(label)
        else:
            self.stack.append(self.current)
            self.stack.append(label)
            self.current = ""

    def edit_number(self, label):
        if len(self.stack) == 1:
            # make room for new equation
            self.stack = []

        if not self.edit_current:
            self.edit_current = True
            self.current = ""

        if self.current == "" and label == ".":
            self.current = "0."

        self.current += label


# basic setup
win = CalculatorWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
