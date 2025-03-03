import tkinter as tk
from tkinter import Button, Frame, Canvas
from copy import deepcopy
from math import isclose

possibility_tree = []
result = ''
maximum_hp = 0

class ActionWindow(tk.Toplevel):
    def __init__(self, master, initial_action, you_prob, dealer_prob, none_prob):
        super().__init__(master)
        self.title("Path")
        self.geometry("700x250")
        self.resizable(False, False)

        self.current_you_prob = you_prob
        self.current_dealer_prob = dealer_prob
        self.current_none_prob = none_prob
        self.result_var = tk.StringVar()

        self.action_text_map = {
            "IC": "Invalid configuration!",
            "SR_you_shoot_self": "There is a higher chance that the shell is blank. Shoot yourself. Click which shell occurred.",
            "SR_you_shoot_op": "There is a higher or equal chance that the shell is live. Shoot the dealer. Click which shell occurred.",
            "SR_dealer_shoot_op": "Which shell did the dealer shoot at you?",
            "SR_dealer_shoot_self": "Which shell did the dealer shoot at itself?",
            "CR_dealer_shoot": "Who did the dealer shoot?",
            "full_end_player_win": "You win!",
            "full_end_dealer_win": "You are guaranteed to lose.",
            "full_end_no_win": "The shotgun will be loaded again. You must set the board again, then press go.",
            "you_shoot_op_live": "The shell is guaranteed to be live. Shoot the dealer.",
            "you_shoot_self_blank": "The shell is guaranteed to be blank. Shoot yourself.",
            "dealer_shoot_op_live": "The Dealer will shoot you with a guaranteed live round.",
            "dealer_shoot_self_blank": "The Dealer will shoot itself with a guaranteed blank round.",
            "you_saw": "There is a higher or equal chance that the shell is live. Use the hand saw.",
            "HR_dealer_saw": "Did the dealer use the hand saw?",
            "dealer_saw": "The dealer will use the hand saw.",
            "SR_you_glass": "Use the magnifying glass. Click which shell is in the chamber.",
            "SR_you_beer": "Use the beer. Click which shell was ejected.",
            "you_beer_live": "Use the beer. You are guaranteed to eject a live round.",
            "you_beer_blank": "Use the beer. You are guaranteed to eject a blank round.",
            "SR_you_adrenaline_glass": "Use the adrenaline to steal the magnifying glass. Click which shell is in the chamber.",
            "SR_you_adrenaline_beer": "Use the adrenaline to steal the beer. Click which shell was ejected.",
            "you_adrenaline_beer_live": "Use the adrenaline to steal the beer. You are guaranteed to eject a live round.",
            "you_adrenaline_beer_blank": "Use the adrenaline to steal the beer. You are guaranteed to eject a blank round.",
            "you_cuff": "Use the handcuffs.",
            "you_adrenaline_cuff": "Use the adrenaline to steal the handcuffs.",
            "dealer_cuff": "The dealer will use handcuffs.",
            "you_cig": "Use the cigarettes.",
            "you_adrenaline_cig": "Use the adrenaline to steal the cigarettes."
        }

        prob_text_frame = tk.Frame(self)
        prob_text_frame.pack(fill="x", padx=20, pady=(20, 5))

        self.you_label = tk.Label(prob_text_frame, text="You: {:.1%}".format(you_prob), anchor="w")
        self.you_label.grid(row=0, column=0, sticky="w", padx=5)

        self.none_label = tk.Label(prob_text_frame, text="None: {:.1%}".format(none_prob), anchor="center")
        self.none_label.grid(row=0, column=1, sticky="ew", padx=5)

        self.dealer_label = tk.Label(prob_text_frame, text="Dealer: {:.1%}".format(dealer_prob), anchor="e")
        self.dealer_label.grid(row=0, column=2, sticky="e", padx=5)

        prob_text_frame.grid_columnconfigure(0, weight=1)
        prob_text_frame.grid_columnconfigure(1, weight=1)
        prob_text_frame.grid_columnconfigure(2, weight=1)

        self.prob_canvas = tk.Canvas(self, height=50)
        self.prob_canvas.pack(fill="x", padx=20, pady=(20, 5))
        self.bind("<Configure>", lambda event: self.draw_prob_bar())

        self.label = tk.Label(self, text=self.action_text_map.get(initial_action, ""))
        self.label.pack(padx=20, pady=20)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(padx=10, pady=10)
        self.create_buttons(initial_action)

    def create_buttons(self, action):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        if action.startswith("SR_"):
            tk.Button(self.button_frame, text="Live",
                      command=lambda: self.on_choice("Live")).pack(side="left", padx=10)
            tk.Button(self.button_frame, text="Blank",
                      command=lambda: self.on_choice("Blank")).pack(side="left", padx=10)
        elif action.startswith("CR_"):
            tk.Button(self.button_frame, text="Self",
                      command=lambda: self.on_choice("Self")).pack(side="left", padx=10)
            tk.Button(self.button_frame, text="You",
                      command=lambda: self.on_choice("You")).pack(side="left", padx=10)
        elif action.startswith("HR_"):
            tk.Button(self.button_frame, text="Yes",
                      command=lambda: self.on_choice("Yes")).pack(side="left", padx=10)
            tk.Button(self.button_frame, text="No",
                      command=lambda: self.on_choice("No")).pack(side="left", padx=10)
        else:
            tk.Button(self.button_frame, text="Next",
                      command=lambda: self.on_choice("Next")).pack(padx=10)

    def on_choice(self, choice):
        self.result_var.set(choice)

    def update_window(self, new_action, new_you_prob, new_dealer_prob, new_none_prob):
        self.label.config(text=self.action_text_map.get(new_action, ""))

        self.create_buttons(new_action)

        self.you_label.config(text="You: {:.1%}".format(new_you_prob))
        self.none_label.config(text="None: {:.1%}".format(new_none_prob))
        self.dealer_label.config(text="Dealer: {:.1%}".format(new_dealer_prob))

        self.animate_prob_bar(new_you_prob, new_dealer_prob, new_none_prob)

    def animate_prob_bar(self, target_you, target_dealer, target_none, steps=250, delay=1):
        diff_you = (target_you - self.current_you_prob) / steps
        diff_dealer = (target_dealer - self.current_dealer_prob) / steps
        diff_none = (target_none - self.current_none_prob) / steps

        def step(i):
            if i < steps:
                self.current_you_prob += diff_you
                self.current_dealer_prob += diff_dealer
                self.current_none_prob += diff_none
                self.draw_prob_bar()
                self.after(delay, lambda: step(i + 1))
            else:
                # Ensure the final values match the target exactly.
                self.current_you_prob = target_you
                self.current_dealer_prob = target_dealer
                self.current_none_prob = target_none
                self.draw_prob_bar()

        step(0)

    def draw_prob_bar(self):
        width = self.prob_canvas.winfo_width()
        height = self.prob_canvas.winfo_height()
        self.prob_canvas.delete("all")

        you_width = width * self.current_you_prob
        dealer_width = width * self.current_dealer_prob
        none_width = width - (you_width + dealer_width)

        self.prob_canvas.create_rectangle(0, 0, you_width, height, fill="green", width=0)
        self.prob_canvas.create_rectangle(you_width, 0, you_width + none_width, height, fill="yellow", width=0)
        self.prob_canvas.create_rectangle(you_width + none_width, 0, width, height, fill="red", width=0)

    def wait_for_result(self):
        self.wait_variable(self.result_var)
        return self.result_var.get()


class NumericControl(tk.Frame):
    def __init__(self, master, initial_value=0, callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.value = initial_value
        self.callback = callback

        self.minus_btn = tk.Button(self, text="–", width=2, command=self.decrement)
        self.minus_btn.grid(row=0, column=0)

        self.value_label = tk.Label(self, text=str(self.value), width=5, relief="sunken")
        self.value_label.grid(row=0, column=1, padx=2)

        self.plus_btn = tk.Button(self, text="+", width=2, command=self.increment)
        self.plus_btn.grid(row=0, column=2)

    def set_value(self, new_value):
        self.value = new_value
        self.value_label.config(text=str(self.value))

    def increment(self):
        old_value = self.value
        self.value += 1
        self.value_label.config(text=str(self.value))
        if self.callback:
            self.callback(self, old_value)

    def decrement(self):
        old_value = self.value
        self.value -= 1
        self.value_label.config(text=str(self.value))
        if self.callback:
            self.callback(self, old_value)


# --- Draggable item class ---
class DraggableItem:
    def __init__(self, canvas, x, y, name, image_path):
        # TODO: add images for items
        self.canvas = canvas
        self.name = name
        self.image_path = image_path

        self.rect = canvas.create_rectangle(x, y, x + 50, y + 50,
                                            fill="lightblue", outline="black", tags="draggable")
        self.text = canvas.create_text(x + 25, y + 25, text=name, tags="draggable")
        self.offset_x = 0
        self.offset_y = 0
        self.current_target = None

        for tag in (self.rect, self.text):
            canvas.tag_bind(tag, "<ButtonPress-1>", self.on_press)
            canvas.tag_bind(tag, "<B1-Motion>", self.on_motion)
            canvas.tag_bind(tag, "<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        bbox = self.canvas.bbox(self.rect)
        self.offset_x = event.x - bbox[0]
        self.offset_y = event.y - bbox[1]
        if self.current_target is not None:
            self.current_target.remove_item(self)
            self.current_target = None

    def on_motion(self, event):
        new_x = event.x - self.offset_x
        new_y = event.y - self.offset_y
        bbox = self.canvas.bbox(self.rect)
        dx = new_x - bbox[0]
        dy = new_y - bbox[1]
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)

    def on_release(self, event):
        for target in self.canvas.app.drop_targets:
            if target.contains(event.x, event.y):
                target.add_item(self)
                self.snap_to_target(target)
                self.current_target = target
                break

    def snap_to_target(self, target):
        count = len(target.items) - 1
        offset_x = (count % 2) * 55
        offset_y = (count // 2) * 55
        new_x = target.x0 + offset_x
        new_y = target.y0 + offset_y
        bbox = self.canvas.bbox(self.rect)
        dx = new_x - bbox[0]
        dy = new_y - bbox[1]
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)


class DropTarget:
    def __init__(self, canvas, x0, y0, x1, y1, side):
        self.canvas = canvas
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.side = side
        self.items = []
        self.rect = canvas.create_rectangle(x0, y0, x1, y1, dash=(2, 2), outline="gray")

    def contains(self, x, y):
        return self.x0 <= x <= self.x1 and self.y0 <= y <= self.y1

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)


# --- Main UI application ---
class UIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Buckshot Roulette Bot")
        self.geometry("1350x767")
        self.resizable(False, False)

        self.left_frame = Frame(self, width=200, bg="lightgray")
        self.left_frame.pack(side="left", fill="y")
        self.right_frame = Frame(self, width=300, bg="lightgray")
        self.right_frame.pack(side="right", fill="y")
        self.center_frame = Frame(self, bg="white")
        self.center_frame.pack(side="left", fill="both", expand=True)

        self.canvas = Canvas(self.center_frame, bg="green")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.app = self
        self.drop_targets = []

        self.create_table()
        self.create_left_panel()
        self.create_right_panel()


    def create_table(self):
        table_x0, table_y0, table_x1, table_y1 = 150, 150, 550, 550
        self.canvas.create_rectangle(table_x0, table_y0, table_x1, table_y1,
                                     fill="darkgreen", outline="white", width=2)
        mid_x = (table_x0 + table_x1) / 2
        mid_y = (table_y0 + table_y1) / 2

        self.canvas.create_line(mid_x, table_y0, mid_x, table_y1, fill="white", width=2)
        self.canvas.create_line(table_x0, mid_y, table_x1, mid_y, fill="white", width=2)

        self.canvas.create_text((table_x0 + table_x1) / 2, table_y0 - 20, text="Dealer",
                                fill="white", font=("Arial", 16))
        self.canvas.create_text((table_x0 + table_x1) / 2, table_y1 + 20, text="You",
                                fill="white", font=("Arial", 16))

        quadrants = {
            "top_left": (table_x0, table_y0, mid_x, mid_y),
            "top_right": (mid_x, table_y0, table_x1, mid_y),
            "bottom_left": (table_x0, mid_y, mid_x, table_y1),
            "bottom_right": (mid_x, mid_y, table_x1, table_y1)
        }
        for quadrant, (qx0, qy0, qx1, qy1) in quadrants.items():
            side = "dealer" if quadrant in ["top_left", "top_right"] else "you"
            w = (qx1 - qx0) / 2
            h = (qy1 - qy0) / 2
            for i in range(2):
                for j in range(2):
                    dt = DropTarget(self.canvas,
                                    qx0 + j * w, qy0 + i * h,
                                    qx0 + (j + 1) * w, qy0 + (i + 1) * h,
                                    side)
                    self.drop_targets.append(dt)

        self.canvas.create_rectangle(mid_x - 25, mid_y - 25, mid_x + 25, mid_y + 25,
                                     fill="yellow", outline="black")
        self.canvas.create_text(mid_x, mid_y, text="Shotgun", font=("Arial", 12), fill="black")

    def create_left_panel(self):
        # TODO: add images for items
        self.item_data = [
            {"name": "Burner Phone", "image": "images/image1.png"},
            {"name": "Inverter", "image": "images/image2.png"},
            {"name": "Expired Medicine", "image": "images/image3.png"},
            {"name": "Beer", "image": "images/image4.png"},
            {"name": "Adrenaline", "image": "images/image5.png"},
            {"name": "Cigarette Pack", "image": "images/image6.png"},
            {"name": "Hand Saw", "image": "images/image7.png"},
            {"name": "Handcuffs", "image": "images/image8.png"},
            {"name": "Magnifying Glass", "image": "images/image9.png"}
        ]
        for i, data in enumerate(self.item_data):
            btn = Button(self.left_frame, text=data["name"],
                         command=lambda d=data: self.create_draggable(d))
            btn.grid(row=i, column=0, padx=5, pady=5, sticky="ew")

    def create_draggable(self, item_data):
        DraggableItem(self.canvas, 50, 50, item_data["name"], item_data["image"])

    def create_right_panel(self):
        right_inner = tk.Frame(self.right_frame, bg="lightgray")
        right_inner.place(relx=0.5, rely=0.5, anchor="center")

        top_frame = tk.Frame(right_inner, bg="lightgray")
        top_frame.pack(pady=5)
        tk.Label(top_frame, text="Live Rounds:", bg="lightgray", fg="black").grid(row=0, column=0, padx=2)
        self.live_count_control = NumericControl(top_frame, initial_value=0)
        self.live_count_control.grid(row=0, column=1, padx=2)

        tk.Label(top_frame, text="Blanks:", bg="lightgray", fg="black").grid(row=1, column=0, padx=2)
        self.blank_count_control = NumericControl(top_frame, initial_value=0)
        self.blank_count_control.grid(row=1, column=1, padx=2)

        middle_frame = tk.Frame(right_inner, bg="lightgray")
        middle_frame.pack(pady=20)

        def health_callback(control, old_value):
            if control == self.max_hp_control:
                new_max = control.value
                if self.dealer_hp_control.value == old_value:
                    self.dealer_hp_control.set_value(new_max)
                if self.you_hp_control.value == old_value:
                    self.you_hp_control.set_value(new_max)
            else:
                if control.value > self.max_hp_control.value:
                    self.max_hp_control.set_value(control.value)

        tk.Label(middle_frame, text="Max HP:", bg="lightgray", fg="black").grid(row=0, column=0, padx=2)
        self.max_hp_control = NumericControl(middle_frame, initial_value=0, callback=health_callback)
        self.max_hp_control.grid(row=0, column=1, padx=2)

        tk.Label(middle_frame, text="Dealer HP:", bg="lightgray", fg="black").grid(row=1, column=0, padx=2)
        self.dealer_hp_control = NumericControl(middle_frame, initial_value=0, callback=health_callback)
        self.dealer_hp_control.grid(row=1, column=1, padx=2)

        tk.Label(middle_frame, text="Your HP:", bg="lightgray", fg="black").grid(row=2, column=0, padx=2)
        self.you_hp_control = NumericControl(middle_frame, initial_value=0, callback=health_callback)
        self.you_hp_control.grid(row=2, column=1, padx=2)


        go_btn = Button(right_inner, text="Go", command=self.run_go)
        go_btn.pack(pady=10)

    def run_go(self):
        player_items = []
        dealer_items = []
        for dt in self.drop_targets:
            if dt.side == "you":
                player_items.extend([item.name for item in dt.items])
            else:
                dealer_items.extend([item.name for item in dt.items])

        live_rounds = self.live_count_control.value
        blanks = self.blank_count_control.value
        dealer_hp = self.dealer_hp_control.value
        player_hp = self.you_hp_control.value
        max_hp = self.max_hp_control.value


        global possibility_tree
        possibility_tree = []

        evaluated = self.go(player_items, dealer_items, live_rounds, blanks, dealer_hp, player_hp, max_hp)
        if not evaluated:
            return

        print(possibility_tree)


        game_not_resolved = True
        turn_index = 1
        action_window = None
        while game_not_resolved:
            actual_action = ""
            actions = []
            for i in range(len(possibility_tree)):
                actions.append(possibility_tree[i][0][turn_index])
            print(actions)
            action_common_you_shoot_op = all("you_shoot_op_" in item for item in actions) if actions else False
            action_common_you_shoot_self = all("you_shoot_self_" in item for item in actions) if actions else False
            action_common_dealer_shoot = all("dealer_shoot_" in item for item in actions) if actions else False
            action_common_dealer_shoot_op = all("dealer_shoot_op_" in item for item in actions) if actions else False
            action_common_dealer_shoot_self = all("dealer_shoot_self_" in item for item in actions) if actions else False
            dealer_potential_saw = any("dealer_saw" in item for item in actions) if actions else False
            action_common_dealer_saw = all("dealer_saw" in item for item in actions) if actions else False
            action_common_you_glass = all("you_glass" in item for item in actions) if actions else False
            action_common_you_beer = all("you_beer" in item for item in actions) if actions else False
            action_common_you_adrenaline_beer = all("you_adrenaline_beer" in item for item in actions) if actions else False
            action_common_you_adrenaline_glass = all("you_adrenaline_glass" in item for item in actions) if actions else False
            action_same = all(x == actions[0] for x in actions) if actions else False
            if not action_same:
                if action_common_you_shoot_op:
                    actual_action = "SR_you_shoot_op"
                elif action_common_you_shoot_self:
                    actual_action = "SR_you_shoot_self"
                elif action_common_dealer_shoot:
                    if action_common_dealer_shoot_op:
                        actual_action = "SR_dealer_shoot_op"
                    elif action_common_dealer_shoot_self:
                        actual_action = "SR_dealer_shoot_self"
                    else:
                        actual_action = "CR_dealer_shoot"
                elif action_common_dealer_saw:
                    actual_action = "dealer_saw"
                elif dealer_potential_saw:
                    actual_action = "HR_dealer_saw"
                elif action_common_you_glass:
                    actual_action = "SR_you_glass"
                elif action_common_you_beer:
                    actual_action = "SR_you_beer"
                elif action_common_you_adrenaline_glass:
                    actual_action = "SR_you_adrenaline_glass"
                elif action_common_you_adrenaline_beer:
                    actual_action = "SR_you_adrenaline_beer"
            else:
                actual_action = actions[0]

            you_prob = 0.0
            dealer_prob = 0.0
            none_prob = 0.0
            full_prob = 0.0
            for i in range(len(possibility_tree)):
                full_prob += possibility_tree[i][1]

            for i in range(len(possibility_tree)):
                if possibility_tree[i][0][-1] == "full_end_dealer_win":
                    dealer_prob += (possibility_tree[i][1] * (1 / full_prob))
                elif possibility_tree[i][0][-1] == "full_end_player_win":
                    you_prob += (possibility_tree[i][1] * (1 / full_prob))
                elif possibility_tree[i][0][-1] == "full_end_no_win":
                    none_prob += (possibility_tree[i][1] * (1 / full_prob))

            global result
            result = ''
            if not action_window:
                action_window = ActionWindow(self, actual_action, you_prob, dealer_prob, none_prob)
            else:
                action_window.update_window(actual_action, you_prob, dealer_prob, none_prob)
            result = action_window.wait_for_result()
            if not result:
                return
            print(result)

            if result == "Live":
                for i in range(len(possibility_tree)):
                    deleted = True
                    while deleted:
                        try:
                            if "_blank" in possibility_tree[i][0][turn_index]:
                                possibility_tree.pop(i)
                                deleted = True
                            else:
                                deleted = False
                        except IndexError:
                            deleted = False
            elif result == "Blank":
                for i in range(len(possibility_tree)):
                    deleted = True
                    while deleted:
                        try:
                            if "_live" in possibility_tree[i][0][turn_index]:
                                possibility_tree.pop(i)
                                deleted = True
                            else:
                                deleted = False
                        except IndexError:
                            deleted = False
            elif result == "Self":
                for i in range(len(possibility_tree)):
                    deleted = True
                    while deleted:
                        try:
                            if "_op_" in possibility_tree[i][0][turn_index]:
                                possibility_tree.pop(i)
                                deleted = True
                            else:
                                deleted = False
                        except IndexError:
                            deleted = False
            elif result == "You":
                for i in range(len(possibility_tree)):
                    deleted = True
                    while deleted:
                        try:
                            if "_self_" in possibility_tree[i][0][turn_index]:
                                possibility_tree.pop(i)
                                deleted = True
                            else:
                                deleted = False
                        except IndexError:
                            deleted = False
            elif result == "Yes":
                for i in range(len(possibility_tree)):
                    deleted = True
                    while deleted:
                        try:
                            if not "dealer_saw" in possibility_tree[i][0][turn_index]:
                                possibility_tree.pop(i)
                                deleted = True
                            else:
                                deleted = False
                        except IndexError:
                            deleted = False
            elif result == "No":
                for i in range(len(possibility_tree)):
                    deleted = True
                    while deleted:
                        try:
                            if "dealer_saw" in possibility_tree[i][0][turn_index]:
                                possibility_tree.pop(i)
                                deleted = True
                            else:
                                deleted = False
                        except IndexError:
                            deleted = False

            print(possibility_tree)
            if not 'CR' in actual_action and not (dealer_potential_saw and result == "No" and not action_common_dealer_saw):
                turn_index += 1
            game_not_resolved = not len(possibility_tree) == 1

        print(possibility_tree[0][0][-1])
        if possibility_tree[0][0][-1] == "full_end_player_win":
            for i in range(len(possibility_tree[0][0]) - turn_index - 1):
                result = ''
                action_window.update_window(possibility_tree[0][0][turn_index], 1.0, 0.0, 0.0)
                result = action_window.wait_for_result()
                if not result:
                    return
                turn_index += 1
            action_window.update_window(possibility_tree[0][0][-1], 1.0, 0.0, 0.0)
            action_window.wait_for_result()
            action_window.destroy()
        elif possibility_tree[0][0][-1] == "full_end_dealer_win":
            action_window.update_window(possibility_tree[0][0][-1], 0.0, 1.0, 0.0)
            action_window.wait_for_result()
            action_window.destroy()
        elif possibility_tree[0][0][-1] == "full_end_no_win":
            for i in range(len(possibility_tree[0][0]) - turn_index - 1):
                result = ''
                action_window.update_window(possibility_tree[0][0][turn_index], 0.0, 0.0, 1.0)
                result = action_window.wait_for_result()
                if not result:
                    return
                turn_index += 1
            action_window.update_window(possibility_tree[0][0][-1], 0.0, 0.0, 1.0)
            action_window.wait_for_result()
            action_window.destroy()





    def go(self, you_items, dealer_items, live, blank, dealer_hp, you_hp, max_hp):
        if ((live <= 0) and (blank <= 0)) or (dealer_hp <= 0) or (you_hp <= 0) or (max_hp < you_hp or max_hp < dealer_hp):
            action_window = ActionWindow(self, "IC", 0.0, 0.0, 0.0)
            action_window.wait_for_result()
            action_window.destroy()
            return None

        print("\r\n")
        print("Your items:", you_items)
        print("Dealer items:", dealer_items)
        print("Live:Blank", f"{live}:{blank}")
        print("Your Health:Dealer Health", f"{you_hp}:{dealer_hp}")


        global maximum_hp
        maximum_hp = max_hp

        result = eval(you_items,dealer_items,live,blank,dealer_hp,you_hp,["full_start"],1.0, None, 'you')
        return result





def eval(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, turn, force_dismiss_search = False, cuffed = None, prev_cuffed = None):
    if any("full_end_dealer_win" in item for item in path) or any("full_end_player_win" in item for item in path):
        if dealer_hp == 0 or you_hp == 0:
            return [path, randomness, you_hp, dealer_hp]
        else:
            return None
    if any("full_end_no_win" in item for item in path):
        return [path, randomness, you_hp, dealer_hp]

    if dealer_hp == 0:
        path.append("full_end_player_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return [path, randomness, you_hp, dealer_hp]
    if you_hp == 0:
        path.append("full_end_dealer_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return [path, randomness, you_hp, dealer_hp]

    if (live + blank) == 0:
        path.append("full_end_no_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return [path, randomness, you_hp, dealer_hp]

    if turn == 'dealer':
        result = sim_dealer_action(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, None, cuffed, prev_cuffed)
        return result

    live_chance = live / (live + blank)
    blank_chance = blank / (live + blank)


    is_live_likely = live_chance > blank_chance
    is_live_guaranteed = live_chance == 1.0 or guarantee == 'live'
    is_blank_guaranteed = blank_chance == 1.0 or guarantee == 'blank'
    is_blank_likely = blank_chance < live_chance
    equally_likely = live_chance == blank_chance

    if (you_items or dealer_items) and not force_dismiss_search:
        if is_live_guaranteed or is_blank_guaranteed:
            passing = ["glass"]
        else:
            passing = []
        search(you_items,dealer_items,live,blank,dealer_hp,you_hp,path,randomness,'live' if is_live_guaranteed else 'blank' if is_blank_guaranteed else None, passing, prev_cuffed, cuffed)
        return path

    # finalizers
    if is_live_guaranteed:
        if "Hand Saw" in you_items:
            potential_damage = 2
            you_items.remove("Hand Saw")
            path.append("you_saw")
        else:
            potential_damage = 1
        if dealer_hp <= potential_damage:
            path.append("you_shoot_op_live")
            path.append("full_end_player_win")
            possibility_tree.append([path, randomness, you_hp, dealer_hp - potential_damage])
            return [path, randomness, you_hp, dealer_hp - potential_damage]
        else:
            path.append("you_shoot_op_live")
            result = eval(you_items, dealer_items, live - 1, blank, dealer_hp - potential_damage, you_hp, path, randomness, None, 'dealer' if cuffed != 'dealer' else 'you', False, None, cuffed)
            return result

    if "Hand Saw" in you_items and live_chance >= blank_chance:
        potential_damage = 2
        you_items.remove("Hand Saw")
        path.append("you_saw")
    else:
        potential_damage = 1

    if is_blank_guaranteed:
        path.append("you_shoot_self_blank")
        result = eval(you_items, dealer_items, live, blank - 1, dealer_hp, you_hp, path, randomness, None, 'you', cuffed)
        return result

    if live_chance >= blank_chance:
        result = split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, 'opponent', 'you', live_chance, potential_damage, 'turn', cuffed)
        return result
    else:
        result = split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, 'self', 'you', live_chance, potential_damage, 'turn', cuffed)
        return result



def split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, action, turn, live_odds, potential_damage = 1, whose = 'turn', cuffed = None, prev_cuffed = None):
    global possibility_tree
    live_randomness = randomness * live_odds
    blank_randomness = randomness * (1 - live_odds)
    if action == 'dealer_shoot_choice':
        stored_path = path.copy()
        stored_you_items = you_items.copy()
        stored_dealer_items = dealer_items.copy()
        op_eval = sim_dealer_action(stored_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp, stored_path.copy(), randomness * 0.5,'opponent', cuffed, prev_cuffed)
        op_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        self_eval = sim_dealer_action(stored_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp, stored_path.copy(), randomness * 0.5, 'self', cuffed, prev_cuffed)
        self_ptree = deepcopy(possibility_tree)
        possibility_tree = op_ptree + self_ptree
        return [self_eval, op_eval]

    if action == 'beer':
        if turn == 'you':
            if whose == 'turn':
                stored_path = path.copy()
                stored_dealer_items = dealer_items.copy()
                new_you_items = you_items.copy()
                new_you_items.remove("Beer")
                live_path = stored_path.copy()
                live_path.append("you_beer_live")
                live_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("you_beer_blank")
                blank_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return [live_eval, blank_eval]
            elif whose == 'other':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Beer")
                new_you_items = you_items.copy()
                new_you_items.remove("Adrenaline")
                live_path = stored_path.copy()
                live_path.append("you_adrenaline_beer_live")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("you_adrenaline_beer_blank")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return [live_eval, blank_eval]
        elif turn == 'dealer':
            if whose == 'turn':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Beer")
                stored_you_items = you_items.copy()
                live_path = stored_path.copy()
                live_path.append("dealer_beer_live")
                live_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_beer_blank")
                blank_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return [live_eval, blank_eval]
            elif whose == 'other':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Adrenaline")
                new_you_items = you_items.copy()
                new_you_items.remove("Beer")
                live_path = stored_path.copy()
                live_path.append("dealer_adrenaline_beer_live")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_adrenaline_beer_blank")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return [live_eval, blank_eval]

    if action == 'glass':
        if turn == 'you':
            if whose == 'turn':
                stored_path = path.copy()
                new_you_items = you_items.copy()
                new_you_items.remove("Magnifying Glass")
                stored_dealer_items = dealer_items.copy()
                live_path = stored_path.copy()
                live_path.append("you_glass_live")
                live_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, "live", turn, False, cuffed, prev_cuffed)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("you_glass_blank")
                blank_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp, blank_path.copy(), blank_randomness, "blank", turn, False, cuffed, prev_cuffed)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return [live_eval, blank_eval]
            elif whose == 'other':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Magnifying Glass")
                new_you_items = you_items.copy()
                new_you_items.remove("Adrenaline")
                live_path = stored_path.copy()
                live_path.append("you_adrenaline_glass_live")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, "live", turn, False, cuffed, prev_cuffed)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("you_adrenaline_glass_blank")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank, dealer_hp, you_hp, blank_path.copy(), blank_randomness, "blank", turn, False, cuffed, prev_cuffed)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return [live_eval, blank_eval]
        elif turn == 'dealer':
            if whose == 'turn':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Magnifying Glass")
                stored_you_items = you_items.copy()
                live_path = stored_path.copy()
                live_path.append("dealer_glass_live")
                live_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, "live", turn, False, cuffed, prev_cuffed)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_glass_blank")
                blank_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, "blank", turn, False, cuffed, prev_cuffed)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return [live_eval, blank_eval]
            elif whose == 'other':
                stored_path = path.copy()
                new_you_items = you_items.copy()
                new_you_items.remove("Magnifying Glass")
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Adrenaline")
                live_path = stored_path.copy()
                live_path.append("dealer_adrenaline_glass_live")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(),live_randomness, "live", turn, False, cuffed, prev_cuffed)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_adrenaline_glass_blank")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(),blank_randomness, "blank", turn, False, cuffed, prev_cuffed)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return [live_eval, blank_eval]

    if action == 'self':
        if turn == 'dealer':
            stored_path = path.copy()
            stored_you_items = you_items.copy()
            stored_dealer_items = dealer_items.copy()
            live_path = stored_path.copy()
            live_path.append("dealer_shoot_self_live")
            live_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live - 1, blank, dealer_hp - 1, you_hp, live_path.copy(), live_randomness, None, 'you' if cuffed != 'you' else 'dealer', False, None, cuffed)
            live_ptree = deepcopy(possibility_tree)
            possibility_tree = []
            blank_path = stored_path.copy()
            blank_path.append("dealer_shoot_self_blank")
            blank_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'dealer', False, cuffed)
            blank_ptree = deepcopy(possibility_tree)
            possibility_tree = live_ptree + blank_ptree
            return [live_eval, blank_eval]
        elif turn == 'you':
            stored_path = path.copy()
            stored_you_items = you_items.copy()
            stored_dealer_items = dealer_items.copy()
            live_path = stored_path.copy()
            live_path.append("you_shoot_self_live")
            live_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp - 1, live_path.copy(), live_randomness, None, 'dealer' if cuffed != 'dealer' else 'you', False, None, cuffed)
            live_ptree = deepcopy(possibility_tree)
            possibility_tree = []
            blank_path = stored_path.copy()
            blank_path.append("you_shoot_self_blank")
            blank_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'you', False, cuffed)
            blank_ptree = deepcopy(possibility_tree)
            possibility_tree = live_ptree + blank_ptree
            return [live_eval, blank_eval]
    elif action == 'opponent':
        if turn == 'dealer':
            stored_path = path.copy()
            stored_you_items = you_items.copy()
            stored_dealer_items = dealer_items.copy()
            if "Hand Saw" in stored_dealer_items:
                stored_path.append("dealer_saw")
                stored_dealer_items.remove("Hand Saw")
                potential_damage = 2
            live_path = stored_path.copy()
            live_path.append("dealer_shoot_op_live")
            live_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp - potential_damage, live_path.copy(), live_randomness, None,'you' if cuffed != 'you' else 'dealer', False, None, cuffed)
            live_ptree = deepcopy(possibility_tree)
            possibility_tree = []
            blank_path = stored_path.copy()
            blank_path.append("dealer_shoot_op_blank")
            blank_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'you' if cuffed != 'you' else 'dealer', False, None, cuffed)
            blank_ptree = deepcopy(possibility_tree)
            possibility_tree = live_ptree + blank_ptree
            return [live_eval, blank_eval]
        elif turn == 'you':
            stored_path = path.copy()
            stored_you_items = you_items.copy()
            stored_dealer_items = dealer_items.copy()
            live_path = stored_path.copy()
            live_path.append("you_shoot_op_live")
            live_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live - 1, blank, dealer_hp - potential_damage, you_hp, live_path.copy(), live_randomness, None,'dealer' if cuffed != 'dealer' else 'you', False, None, cuffed)
            live_ptree = deepcopy(possibility_tree)
            possibility_tree = []
            blank_path = stored_path.copy()
            blank_path.append("you_shoot_op_blank")
            blank_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'dealer' if cuffed != 'dealer' else 'you', False, None, cuffed)
            blank_ptree = deepcopy(possibility_tree)
            possibility_tree = live_ptree + blank_ptree
            return [live_eval, blank_eval]


def sim_dealer_action(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, choice = None, cuffed = None, prev_cuffed = None):
    if any("full_end_dealer_win" in item for item in path) or any("full_end_player_win" in item for item in path):
        if dealer_hp == 0 or you_hp == 0:
            return [path, randomness, you_hp, dealer_hp]
        else:
            return None
    if any("full_end_no_win" in item for item in path):
        return [path, randomness, you_hp, dealer_hp]

    if dealer_hp == 0:
        path.append("full_end_player_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return [path, randomness, you_hp, dealer_hp]
    elif you_hp == 0:
        path.append("full_end_dealer_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return [path, randomness, you_hp, dealer_hp]

    if (live + blank) == 0:
        path.append("full_end_no_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return [path, randomness, you_hp, dealer_hp]

    live_chance = live / (live + blank)
    blank_chance = blank / (live + blank)
    is_live_guaranteed = live_chance == 1.0
    is_blank_guaranteed = blank_chance == 1.0

    if "Handcuffs" in dealer_items and not prev_cuffed == 'you' and not cuffed == 'you':
        new_dealer_items = dealer_items.copy()
        new_dealer_items.remove("Handcuffs")
        new_path = path.copy()
        new_path.append("dealer_cuff")
        sim_dealer_action(you_items, new_dealer_items.copy(), live, blank, dealer_hp, you_hp, new_path.copy(), randomness, choice, 'you', None)
        return

    if is_live_guaranteed:
        if "Hand Saw" in dealer_items:
            potential_damage = 2
            dealer_items.remove("Hand Saw")
            path.append("dealer_saw")
        else:
            potential_damage = 1
        path.append("dealer_shoot_op_live")
        result = eval(you_items, dealer_items, live - 1, blank, dealer_hp, you_hp - potential_damage, path, randomness, None, 'you' if cuffed != 'you' else 'dealer', None, None, cuffed)
        return result
    elif not is_blank_guaranteed and not choice:
        result = split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, 'dealer_shoot_choice', 'dealer', live_chance, 1, 'turn', cuffed, prev_cuffed)
        return result
    elif not is_blank_guaranteed:
        result = split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, choice, 'dealer', live_chance, 1, 'turn', cuffed, prev_cuffed)
        return result
    elif is_blank_guaranteed:
        path.append("dealer_shoot_self_blank")
        result = eval(you_items, dealer_items, live, blank - 1, dealer_hp, you_hp, path, randomness, None, 'dealer', False, cuffed, prev_cuffed)
        return result

    path.append("dealer_sim_here")
    return [path, randomness, you_hp, dealer_hp]

def search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, passed, prev_cuffed = None, cuffed = None):
    global possibility_tree
    starting_ptree = deepcopy(possibility_tree)
    possibility_tree = []
    alpha_ptree = []
    beta_ptree = []
    global maximum_hp

    if "Handcuffs" in you_items and not "cuffs" in passed and not prev_cuffed == 'dealer' and not cuffed == 'dealer':
        new_you_items = you_items.copy()
        new_you_items.remove("Handcuffs")
        new_path = path.copy()
        new_path.append("you_cuff")
        eval(new_you_items.copy(),dealer_items,live,blank,dealer_hp,you_hp,new_path.copy(),randomness,guarantee,'you',False,'dealer')
        alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("cuffs")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed)
        beta_ptree = deepcopy(possibility_tree)
        action_done = True
    elif "Magnifying Glass" in you_items and not "glass" in passed:
        split(you_items,dealer_items,live,blank,dealer_hp,you_hp,path,randomness,"glass", "you", live / (live + blank), 1, 'turn', cuffed, prev_cuffed)
        alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("glass")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed)
        beta_ptree = deepcopy(possibility_tree)
        action_done = True
    elif "Beer" in you_items and not "beer" in passed:
        if guarantee:
            newpath = path.copy()
            newpath.append(f"you_beer_{guarantee}")
            new_you_items = you_items.copy()
            new_you_items.remove("Beer")
            if guarantee == 'live':
                eval(new_you_items,dealer_items,live - 1,blank,dealer_hp,you_hp,newpath,randomness,None,'you', False, cuffed, prev_cuffed)
            elif guarantee == 'blank':
                eval(new_you_items,dealer_items,live,blank - 1,dealer_hp,you_hp,newpath,randomness,None,'you', False, cuffed, prev_cuffed)
        else:
            split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "beer", "you", live / (live + blank), 1, 'turn', cuffed, prev_cuffed)
        alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("beer")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed)
        beta_ptree = deepcopy(possibility_tree)
        action_done = True
    elif "Cigarette Pack" in you_items and not "cig" in passed and you_hp < maximum_hp:
        new_you_items = you_items.copy()
        new_you_items.remove("Cigarette Pack")
        new_path = path.copy()
        new_path.append("you_cig")
        eval(new_you_items.copy(),dealer_items,live,blank,dealer_hp,you_hp+1,new_path.copy(),randomness,guarantee,'you', False, cuffed, prev_cuffed)
        alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("cig")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed)
        beta_ptree = deepcopy(possibility_tree)
        action_done = True
    elif "Adrenaline" in you_items and not "adrenaline" in passed:
        if dealer_items:
            adrenaline(you_items,dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, passed, prev_cuffed, cuffed)
            return
        else:
            newpassed = passed.copy()
            newpassed.append("adrenaline")
            search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, newpassed, prev_cuffed, cuffed)
            return
    else:
        eval(you_items,dealer_items,live,blank,dealer_hp,you_hp,path,randomness,guarantee,'you', True, cuffed, prev_cuffed)
        return

    a_full_prob = 0.0
    for i in range(len(alpha_ptree)):
        a_full_prob += alpha_ptree[i][1]

    a_d_prob = 0.0
    a_y_prob = 0.0
    a_n_prob = 0.0
    for i in range(len(alpha_ptree)):
        if alpha_ptree[i][0][-1] == "full_end_dealer_win":
            a_d_prob += (alpha_ptree[i][1] * (1/ a_full_prob))
        elif alpha_ptree[i][0][-1] == "full_end_player_win":
            a_y_prob += (alpha_ptree[i][1] * (1/ a_full_prob))
        elif alpha_ptree[i][0][-1] == "full_end_no_win":
            a_n_prob += (alpha_ptree[i][1] * (1/ a_full_prob))

    b_full_prob = 0.0
    for i in range(len(beta_ptree)):
        b_full_prob += beta_ptree[i][1]

    b_d_prob = 0.0
    b_y_prob = 0.0
    b_n_prob = 0.0
    for i in range(len(beta_ptree)):
        if beta_ptree[i][0][-1] == "full_end_dealer_win":
            b_d_prob += (beta_ptree[i][1] * (1/ b_full_prob))
        elif beta_ptree[i][0][-1] == "full_end_player_win":
            b_y_prob += (beta_ptree[i][1] * (1/ b_full_prob))
        elif beta_ptree[i][0][-1] == "full_end_no_win":
            b_n_prob += (beta_ptree[i][1] * (1/ b_full_prob))

    if a_y_prob + a_n_prob > b_y_prob + b_n_prob and not isclose(a_y_prob + a_n_prob, b_y_prob + b_n_prob, rel_tol=1e-15, abs_tol=0.0):
        possibility_tree = starting_ptree + alpha_ptree
    elif b_y_prob + b_n_prob > a_y_prob + a_n_prob and not isclose(a_y_prob + a_n_prob, b_y_prob + b_n_prob, rel_tol=1e-15, abs_tol=0.0):
        possibility_tree = starting_ptree + beta_ptree
    else:
        alpha_rating = 0
        for i in range(len(alpha_ptree)):
            alpha_rating += (alpha_ptree[i][2] - alpha_ptree[i][3]) / (alpha_ptree[i][1] * (1/ a_full_prob))
        beta_rating = 0
        for i in range(len(beta_ptree)):
            beta_rating += (beta_ptree[i][2] - beta_ptree[i][3]) / (beta_ptree[i][1] * (1/ b_full_prob))
        if alpha_rating > beta_rating and not isclose(alpha_rating, beta_rating, rel_tol=1e-12, abs_tol=0.0):
            possibility_tree = starting_ptree + alpha_ptree
        else:
            possibility_tree = starting_ptree + beta_ptree

def adrenaline(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, passed, prev_cuffed = None, cuffed = None):
    global possibility_tree
    a_starting_ptree = deepcopy(possibility_tree)
    possibility_tree = []
    a_alpha_ptree = []
    a_beta_ptree = []

    if "Handcuffs" in dealer_items and not "cuffs" in passed and not prev_cuffed == 'dealer' and not cuffed == 'dealer':
        a_new_you_items = you_items.copy()
        a_new_you_items.remove("Adrenaline")
        a_new_dealer_items = dealer_items.copy()
        a_new_dealer_items.remove("Handcuffs")
        new_path = path.copy()
        new_path.append("you_adrenaline_cuff")
        eval(a_new_you_items.copy(),a_new_dealer_items.copy(),live,blank,dealer_hp,you_hp,new_path.copy(),randomness,guarantee,'you',False,'dealer')
        a_alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("cuffs")
        adrenaline(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed)
        a_beta_ptree = deepcopy(possibility_tree)
        a_action_done = True
    elif "Magnifying Glass" in dealer_items and not "glass" in passed:
        split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "glass", "you", live / (live + blank), 1, 'other')
        a_alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("glass")
        adrenaline(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed)
        a_beta_ptree = deepcopy(possibility_tree)
        a_action_done = True
    elif "Beer" in dealer_items and not "beer" in passed:
        if guarantee:
            a_newpath = path.copy()
            a_newpath.append(f"you_adrenaline_beer_{guarantee}")
            a_new_dealer_items = dealer_items.copy()
            a_new_dealer_items.remove("Beer")
            a_new_you_items = you_items.copy()
            a_new_you_items.remove("Adrenaline")
            if guarantee == 'live':
                eval(a_new_you_items, a_new_dealer_items, live - 1, blank, dealer_hp, you_hp, a_newpath, randomness, None, 'you')
            elif guarantee == 'blank':
                eval(a_new_you_items, a_new_dealer_items, live, blank - 1, dealer_hp, you_hp, a_newpath, randomness, None, 'you')
        else:
            split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "beer", "you", live / (live + blank), 1, 'other')
        a_alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("beer")
        adrenaline(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed)
        a_beta_ptree = deepcopy(possibility_tree)
        a_action_done = True
    elif "Cigarette Pack" in dealer_items and not "cig" in passed and you_hp < maximum_hp:
        a_new_you_items = you_items.copy()
        a_new_you_items.remove("Adrenaline")
        a_new_dealer_items = dealer_items.copy()
        a_new_dealer_items.remove("Cigarette Pack")
        new_path = path.copy()
        new_path.append("you_adrenaline_cig")
        eval(a_new_you_items.copy(),a_new_dealer_items.copy(),live,blank,dealer_hp,you_hp+1,new_path.copy(),randomness,guarantee,'you', False, cuffed, prev_cuffed)
        a_alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("cig")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed)
        a_beta_ptree = deepcopy(possibility_tree)
        a_action_done = True
    else:
        eval(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, 'you', True)
        return

    a_a_full_prob = 0.0
    for i in range(len(a_alpha_ptree)):
        a_a_full_prob += a_alpha_ptree[i][1]

    a_a_d_prob = 0.0
    a_a_y_prob = 0.0
    a_a_n_prob = 0.0
    for i in range(len(a_alpha_ptree)):
        if a_alpha_ptree[i][0][-1] == "full_end_dealer_win":
            a_a_d_prob += (a_alpha_ptree[i][1] * (1 / a_a_full_prob))
        elif a_alpha_ptree[i][0][-1] == "full_end_player_win":
            a_a_y_prob += (a_alpha_ptree[i][1] * (1 / a_a_full_prob))
        elif a_alpha_ptree[i][0][-1] == "full_end_no_win":
            a_a_n_prob += (a_alpha_ptree[i][1] * (1 / a_a_full_prob))

    a_b_full_prob = 0.0
    for i in range(len(a_beta_ptree)):
        a_b_full_prob += a_beta_ptree[i][1]

    a_b_d_prob = 0.0
    a_b_y_prob = 0.0
    a_b_n_prob = 0.0
    for i in range(len(a_beta_ptree)):
        if a_beta_ptree[i][0][-1] == "full_end_dealer_win":
            a_b_d_prob += (a_beta_ptree[i][1] * (1 / a_b_full_prob))
        elif a_beta_ptree[i][0][-1] == "full_end_player_win":
            a_b_y_prob += (a_beta_ptree[i][1] * (1 / a_b_full_prob))
        elif a_beta_ptree[i][0][-1] == "full_end_no_win":
            a_b_n_prob += (a_beta_ptree[i][1] * (1 / a_b_full_prob))

    if a_a_y_prob + a_a_n_prob > a_b_y_prob + a_b_n_prob and not isclose(a_a_y_prob + a_a_n_prob, a_b_y_prob + a_b_n_prob, rel_tol=1e-15, abs_tol=0.0):
        possibility_tree = a_starting_ptree + a_alpha_ptree
    elif a_b_y_prob + a_b_n_prob > a_a_y_prob + a_a_n_prob and not isclose(a_a_y_prob + a_a_n_prob, a_b_y_prob + a_b_n_prob, rel_tol=1e-15, abs_tol=0.0):
        possibility_tree = a_starting_ptree + a_beta_ptree
    else:
        a_alpha_rating = 0
        for i in range(len(a_alpha_ptree)):
            a_alpha_rating += (a_alpha_ptree[i][2] - a_alpha_ptree[i][3]) / (a_alpha_ptree[i][1] * (1/ a_a_full_prob))
        a_beta_rating = 0
        for i in range(len(a_beta_ptree)):
            a_beta_rating += (a_beta_ptree[i][2] - a_beta_ptree[i][3]) / (a_beta_ptree[i][1] * (1/ a_b_full_prob))
        if a_alpha_rating > a_beta_rating and not isclose(a_alpha_rating, a_beta_rating, rel_tol=1e-12, abs_tol=0.0):
            possibility_tree = a_starting_ptree + a_alpha_ptree
        else:
            possibility_tree = a_starting_ptree + a_beta_ptree


if __name__ == "__main__":
    app = UIApp()
    app.mainloop()
