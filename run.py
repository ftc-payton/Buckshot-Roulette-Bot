import tkinter as tk
from tkinter import Button, Frame, Canvas
from copy import deepcopy
from math import isclose
import threading
import ctypes

possibility_tree = []
result = ''
maximum_hp = 0
action_window = None

class NumericControl(tk.Frame):
    def __init__(self, master, initial_value=0, callback=None, upper_bound = 8, lower_bound = 0, **kwargs):
        super().__init__(master, **kwargs)
        self.value = initial_value
        self.callback = callback
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

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
        if self.value + 1 > self.upper_bound:
            return
        old_value = self.value
        self.value += 1
        self.value_label.config(text=str(self.value))
        if self.callback:
            self.callback(self, old_value)

    def decrement(self):
        if self.value - 1 < self.lower_bound:
            return
        old_value = self.value
        self.value -= 1
        self.value_label.config(text=str(self.value))
        if self.callback:
            self.callback(self, old_value)

class ActionWindow(tk.Toplevel):
    def __init__(self, master, initial_action, you_prob, dealer_prob, none_prob, shells=0):
        super().__init__(master)
        self.title("Path")
        self.geometry("700x250")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self.current_you_prob = you_prob
        self.current_dealer_prob = dealer_prob
        self.current_none_prob = none_prob
        self.result_var = tk.StringVar()
        self.is_guaranteed_list = False
        self.action = initial_action
        self.shells = shells

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
            "HR_dealer_adrenaline_saw": "Did the dealer use adrenaline to steal your hand saw?",
            "dealer_saw": "The dealer will use the hand saw.",
            "dealer_adrenaline_saw": "The dealer will use adrenaline to steal your hand saw.",
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
            "dealer_adrenaline_cuff": "The dealer will use adrenaline to steal your handcuffs.",
            "you_cig": "Use the cigarettes.",
            "you_adrenaline_cig": "Use the adrenaline to steal the cigarettes.",
            "dealer_cig": "The dealer will use cigarettes.",
            "dealer_adrenaline_cig": "The dealer will use adrenaline to steal your cigarettes.",
            "you_invert_uk": "Use the inverter.",
            "you_invert_live": "Use the inverter.",
            "you_invert_blank": "Use the inverter.",
            "you_adrenaline_invert_uk": "Use the adrenaline to steal the inverter.",
            "you_adrenaline_invert_live": "Use the adrenaline to steal the inverter.",
            "you_adrenaline_invert_blank": "Use the adrenaline to steal the inverter.",
            "MR_you_exp": "Use the expired medicine. Did it succeed?",
            "MR_you_adrenaline_exp": "Use the adrenaline to steal the expired medicine. Did it succeed?",
            "MR_dealer_exp": "The dealer will use expired medicine. Did it succeed?",
            "dealer_invert": "The dealer will use the inverter.",
            "SR_dealer_beer": "Which shell did the dealer eject?",
            "HR_dealer_invert": "Did the dealer use the inverter?",
            "HR_dealer_adrenaline_invert": "Did the dealer use adrenaline to steal your inverter?",
            "HR_dealer_beer": "Did the dealer use the beer?",
            "dealer_beer_blank": "The dealer will use the beer to eject the guaranteed blank round.",
            "dealer_glass": "The dealer will use the magnifying glass.",
            "dealer_adrenaline_glass": "The dealer will use adrenaline to steal your magnifying glass.",
            "SR_dealer_adrenaline_beer": "Which shell did the dealer eject?",
            "HR_dealer_adrenaline_beer": "Did the dealer use adrenaline to steal your beer?",
            "SR_PR_you_phone": "Use the burner phone.",
            "dealer_phone": "The dealer will use the burner phone.",
            "dealer_shoot_self_live": "The dealer will shoot itself with a guaranteed live round.",
            "dealer_shoot_op_blank": "The dealer will shoot you with a guaranteed blank round."
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

        self.label = tk.Label(self, text=(self.action_text_map.get(initial_action, "") if self.current_dealer_prob != 1.0 else "You are guaranteed to lose."))
        self.label.pack(padx=20, pady=20)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(padx=10, pady=10)
        self.create_buttons(initial_action)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_buttons(self, action):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        if self.current_dealer_prob == 1.0:
            tk.Button(self.button_frame, text="Next",
                      command=lambda: self.on_choice("Next")).pack(padx=10)
        elif isinstance(action, list):
            if not self.is_guaranteed_list:
                tk.Button(self.button_frame, text="Yes",
                        command=lambda: self.on_choice("Yes")).pack(side="left", padx=10)
                tk.Button(self.button_frame, text="No",
                        command=lambda: self.on_choice("No")).pack(side="left", padx=10)
            else:
                tk.Button(self.button_frame, text="Next",
                          command=lambda: self.on_choice("Next")).pack(padx=10)
        elif action.startswith("SR_"):
            if "PR" in action:
                numeric_frame = tk.Frame(self.button_frame)
                numeric_frame.pack(side="left", padx=10)
                tk.Label(numeric_frame, text="Shell number:").pack(side="left")
                self.numeric_control = NumericControl(numeric_frame, 2, lower_bound=2, upper_bound=self.shells)
                self.numeric_control.pack(side="left", padx=10)
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
        elif action.startswith("MR_"):
            tk.Button(self.button_frame, text="Yes",
                      command=lambda: self.on_choice("Yes")).pack(side="left", padx=10)
            tk.Button(self.button_frame, text="No",
                      command=lambda: self.on_choice("No")).pack(side="left", padx=10)
        else:
            tk.Button(self.button_frame, text="Next",
                      command=lambda: self.on_choice("Next")).pack(padx=10)

    def on_choice(self, choice):
        self.result_var.set(choice)

    def on_close(self):
        self.result_var.set([])
        self.destroy()

    def update_window(self, new_action, new_you_prob, new_dealer_prob, new_none_prob, guaranteed_action_list = False, destroy = False):
        if destroy:
            self.destroy()
            return
        self.action = new_action
        self.label.config(text=(self.action_text_map.get(new_action, "") if new_dealer_prob != 1.0 else "You are guaranteed to lose."))

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
        if self.current_dealer_prob != 1.0:
            if not "PR" in self.action:
                return self.result_var.get()
            else:
                return [self.numeric_control.value, self.result_var.get()]
        else:
            self.destroy()

class DraggableItem:
    def __init__(self, canvas, x, y, name, image_path):
        self.canvas = canvas
        self.name = name
        self.image_path = image_path

        self.width = 80
        self.height = 80
        self.locked = False

        self.rect = canvas.create_rectangle(x, y, x + self.width, y + self.height,
                                            fill="lightblue", outline="black", tags="draggable")
        self.text = canvas.create_text(x + self.width / 2, y + self.height / 2,
                                       text=name, tags="draggable")
        self.offset_x = 0
        self.offset_y = 0
        self.current_target = None

        for tag in (self.rect, self.text):
            canvas.tag_bind(tag, "<ButtonPress-1>", self.on_press)
            canvas.tag_bind(tag, "<B1-Motion>", self.on_motion)
            canvas.tag_bind(tag, "<ButtonRelease-1>", self.on_release)

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def on_press(self, event):
        if self.locked:
            return
        bbox = self.canvas.bbox(self.rect)
        self.offset_x = event.x - bbox[0]
        self.offset_y = event.y - bbox[1]
        if self.current_target is not None:
            self.current_target.remove_item(self)
            self.current_target = None

    def on_motion(self, event):
        if self.locked:
            return
        new_x = event.x - self.offset_x
        new_y = event.y - self.offset_y
        bbox = self.canvas.bbox(self.rect)
        dx = new_x - bbox[0]
        dy = new_y - bbox[1]
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)

    def on_release(self, event):
        if self.locked:
            return
        for target in self.canvas.app.drop_targets:
            if target.contains(event.x, event.y):
                if target.add_item(self):
                    self.snap_to_target(target)
                    self.current_target = target
                    break

    def snap_to_target(self, target):
        center_x = (target.x0 + target.x1) / 2
        center_y = (target.y0 + target.y1) / 2
        new_x = center_x - self.width / 2
        new_y = center_y - self.height / 2
        bbox = self.canvas.bbox(self.rect)
        current_x, current_y = bbox[0], bbox[1]
        dx = new_x - current_x
        dy = new_y - current_y
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
        if len(self.items) >= 1:
            return False
        self.items.append(item)
        return True

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)



class UIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Buckshot Roulette Bot")
        self.geometry("1350x767")
        self.resizable(False, False)

        self.eval_thread = None

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
        self.draggable_items = []

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
        self.item_buttons = []
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
            self.item_buttons.append(btn)

    def create_draggable(self, item_data):
        new_item = DraggableItem(self.canvas, 50, 50, item_data["name"], item_data["image"])
        self.draggable_items.append(new_item)

    def create_right_panel(self):
        right_inner = tk.Frame(self.right_frame, bg="lightgray")
        right_inner.place(relx=0.5, rely=0.5, anchor="center")

        top_frame = tk.Frame(right_inner, bg="lightgray")
        top_frame.pack(pady=5)
        tk.Label(top_frame, text="Live Rounds:", bg="lightgray", fg="black").grid(row=0, column=0, padx=2)
        self.live_count_control = NumericControl(top_frame, initial_value=0, upper_bound=8, lower_bound=0)
        self.live_count_control.grid(row=0, column=1, padx=2)

        tk.Label(top_frame, text="Blanks:", bg="lightgray", fg="black").grid(row=1, column=0, padx=2)
        self.blank_count_control = NumericControl(top_frame, initial_value=0, upper_bound=8, lower_bound=0)
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
        self.max_hp_control = NumericControl(middle_frame, initial_value=1, callback=health_callback, upper_bound=5, lower_bound=1)
        self.max_hp_control.grid(row=0, column=1, padx=2)

        tk.Label(middle_frame, text="Dealer HP:", bg="lightgray", fg="black").grid(row=1, column=0, padx=2)
        self.dealer_hp_control = NumericControl(middle_frame, initial_value=1, callback=health_callback, upper_bound=5, lower_bound=1)
        self.dealer_hp_control.grid(row=1, column=1, padx=2)

        tk.Label(middle_frame, text="Your HP:", bg="lightgray", fg="black").grid(row=2, column=0, padx=2)
        self.you_hp_control = NumericControl(middle_frame, initial_value=1, callback=health_callback, upper_bound=5, lower_bound=1)
        self.you_hp_control.grid(row=2, column=1, padx=2)

        self.go_btn = Button(right_inner, text="Go", command=self.run_go)
        self.go_btn.pack(pady=10)

        self.calc_label = tk.Label(right_inner, text="", fg="black", bg="lightgray")
        self.calc_label.pack()

        self.reset_btn = tk.Button(right_inner, text="Reset", command=self.reset_app)
        self.reset_btn.pack()

    def destroy_item_by_name(self, item_name, side):
        for target in self.drop_targets:
            if target.side == side:
                for item in target.items:
                    if item.name == item_name:
                        self.canvas.delete(item.rect)
                        self.canvas.delete(item.text)
                        target.items.remove(item)
                        if item in self.draggable_items:
                            self.draggable_items.remove(item)
                        return True
        return False

    def remove_you_item(self, item_name):
        return self.destroy_item_by_name(item_name, side="you")

    def remove_dealer_item(self, item_name):
        return self.destroy_item_by_name(item_name, side="dealer")

    def reset_app(self):
        self.live_count_control.set_value(0)
        self.blank_count_control.set_value(0)
        self.max_hp_control.set_value(1)
        self.dealer_hp_control.set_value(1)
        self.you_hp_control.set_value(1)

        for item in self.draggable_items:
            self.canvas.delete(item.rect)
            self.canvas.delete(item.text)
        self.draggable_items.clear()
        for dt in self.drop_targets:
            dt.items.clear()

    def disable_controls(self):
        for control in [self.live_count_control, self.blank_count_control,
                        self.max_hp_control, self.dealer_hp_control, self.you_hp_control]:
            control.minus_btn.config(state="disabled")
            control.plus_btn.config(state="disabled")
        for item in self.draggable_items:
            item.lock()
        for btn in self.item_buttons:
            btn.config(state="disabled")
        self.reset_btn.config(state="disabled")

    def enable_controls(self):
        for control in [self.live_count_control, self.blank_count_control,
                        self.max_hp_control, self.dealer_hp_control, self.you_hp_control]:
            control.minus_btn.config(state="normal")
            control.plus_btn.config(state="normal")
        for item in self.draggable_items:
            item.unlock()
        for btn in self.item_buttons:
            btn.config(state="normal")
        self.reset_btn.config(state="normal")

    def run_go(self):
        if self.eval_thread is None or not self.eval_thread.is_alive():
            self.disable_controls()
            self.go_btn.config(text="Stop")
            self.calc_label.config(text="Calculating...")
            self.eval_thread = threading.Thread(target=self.eval_thread_func)
            self.eval_thread.start()
        else:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.eval_thread.ident),
                ctypes.py_object(KeyboardInterrupt)
            )
            global action_window
            if action_window:
                action_window.on_choice(None)
                action_window.destroy()
                return

    def eval_thread_func(self):
        try:
            global action_window
            action_window = None
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
                raise KeyboardInterrupt()
            self.after(0, self.calc_label.config, {"text": ""})

            print(possibility_tree)

            for i in range(len(possibility_tree)):
                deleted = True
                while deleted:
                    try:
                        if possibility_tree[i][1] == 0.0:
                            possibility_tree.pop(i)
                            deleted = True
                        else:
                            deleted = False
                    except IndexError:
                        deleted = False

            game_not_resolved = True
            turn_index = 1
            action_window = None
            you_sawed = False
            dealer_sawed = False
            you_inverted = False
            dealer_inverted = False
            while game_not_resolved:
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
                action_common_you_invert = all("you_invert" in item for item in actions) if actions else False
                action_common_you_adrenaline_invert = all("you_adrenaline_invert" in item for item in actions) if actions else False
                action_common_you_exp = all("you_exp" in item for item in actions) if actions else False
                action_common_you_adrenaline_exp = all("you_adrenaline_exp" in item for item in actions) if actions else False
                action_common_dealer_exp = all("dealer_exp" in item for item in actions) if actions else False
                action_common_dealer_think = all("dealer_think" in item for item in actions) if actions else False
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
                    elif action_common_you_invert:
                        actual_action = "you_invert_uk"
                    elif action_common_you_adrenaline_invert:
                        actual_action = "you_adrenaline_invert_uk"
                    elif action_common_you_exp:
                        actual_action = "MR_you_exp"
                    elif action_common_you_adrenaline_exp:
                        actual_action = "MR_you_adrenaline_exp"
                    elif action_common_dealer_exp:
                        actual_action = "MR_dealer_exp"
                    elif action_common_dealer_think:
                        blank_think = None
                        live_think = None
                        for i in range(len(possibility_tree)):
                            if possibility_tree[i][0][turn_index] == 'dealer_think_blank':
                                blank_think = possibility_tree[i][0]
                            elif possibility_tree[i][0][turn_index] == 'dealer_think_live':
                                live_think = possibility_tree[i][0]
                            if blank_think and live_think:
                                break
                        blank_think_acts = []
                        live_think_acts = []
                        for i in range(len(blank_think)):
                            if not 'dealer_shoot' in blank_think[turn_index + i]:
                                blank_think_acts.append(blank_think[turn_index + i])
                            else:
                                blank_turn_index = turn_index + i
                                break
                        for i in range(len(live_think)):
                            if not 'dealer_shoot' in live_think[turn_index + i]:
                                live_think_acts.append(live_think[turn_index + i])
                            else:
                                live_turn_index = turn_index + i
                                break
                        print(blank_think_acts)
                        print(live_think_acts)
                        ti_increase = 1
                        if 'dealer_invert' in blank_think_acts:
                            result = ''
                            if not action_window:
                                action_window = ActionWindow(self, "HR_dealer_invert", you_prob, dealer_prob, none_prob)
                            else:
                                action_window.update_window("HR_dealer_invert", you_prob, dealer_prob, none_prob)
                            result = action_window.wait_for_result()
                            if not result or not action_window.winfo_exists():
                                raise KeyboardInterrupt()
                            if result == 'No':
                                ti_increase = 1
                            else:
                                ti_increase = 3
                                self.remove_dealer_item("Inverter")
                                dealer_inverted = True
                            print(result)
                        elif 'dealer_adrenaline_invert' in blank_think_acts:
                            result = ''
                            if not action_window:
                                action_window = ActionWindow(self, "HR_dealer_adrenaline_invert", you_prob, dealer_prob, none_prob)
                            else:
                                action_window.update_window("HR_dealer_adrenaline_invert", you_prob, dealer_prob, none_prob)
                            result = action_window.wait_for_result()
                            if not result or not action_window.winfo_exists():
                                raise KeyboardInterrupt()
                            if result == 'No':
                                ti_increase = 1
                            else:
                                ti_increase = 3
                                self.remove_dealer_item("Adrenaline")
                                self.remove_you_item("Inverter")
                                dealer_inverted = True
                            print(result)
                        elif 'dealer_beer_live' in blank_think_acts or 'dealer_beer_blank' in blank_think_acts:
                            result = ''
                            if not action_window:
                                action_window = ActionWindow(self, "HR_dealer_beer", you_prob, dealer_prob, none_prob)
                            else:
                                action_window.update_window("HR_dealer_beer", you_prob, dealer_prob, none_prob)
                            result = action_window.wait_for_result()
                            if not result or not action_window.winfo_exists():
                                raise KeyboardInterrupt()
                            if result == 'No':
                                ti_increase = 1
                            else:
                                ti_increase = 2
                                self.remove_dealer_item("Beer")
                            print(result)
                            if result == 'Yes':
                                for i in range(len(possibility_tree)):
                                    deleted = True
                                    while deleted:
                                        try:
                                            if 'dealer_think_live' in possibility_tree[i][0][turn_index]:
                                                possibility_tree.pop(i)
                                                deleted = True
                                            else:
                                                deleted = False
                                        except IndexError:
                                            deleted = False
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

                                action_window.update_window("SR_dealer_beer", you_prob, dealer_prob, none_prob)
                                result = action_window.wait_for_result()
                                if not result or not action_window.winfo_exists():
                                    raise KeyboardInterrupt()
                                if result == 'Live':
                                    self.live_count_control.value -= 1
                                else:
                                    self.blank_count_control.value -= 1
                        elif 'dealer_adrenaline_beer_live' in blank_think_acts or 'dealer_adrenaline_beer_blank' in blank_think_acts:
                            result = ''
                            if not action_window:
                                action_window = ActionWindow(self, "HR_dealer_adrenaline_beer", you_prob, dealer_prob, none_prob)
                            else:
                                action_window.update_window("HR_dealer_adrenaline_beer", you_prob, dealer_prob, none_prob)
                            result = action_window.wait_for_result()
                            if not result or not action_window.winfo_exists():
                                raise KeyboardInterrupt()
                            if result == 'No':
                                ti_increase = 1
                            else:
                                ti_increase = 2
                                self.remove_dealer_item("Adrenaline")
                                self.remove_you_item("Beer")

                            print(result)
                            if result == 'Yes':
                                for i in range(len(possibility_tree)):
                                    deleted = True
                                    while deleted:
                                        try:
                                            if 'dealer_think_live' in possibility_tree[i][0][turn_index]:
                                                possibility_tree.pop(i)
                                                deleted = True
                                            else:
                                                deleted = False
                                        except IndexError:
                                            deleted = False
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

                                action_window.update_window("SR_dealer_adrenaline_beer", you_prob, dealer_prob, none_prob)
                                result = action_window.wait_for_result()
                                if not result or not action_window.winfo_exists():
                                    raise KeyboardInterrupt()
                                if result == 'Live':
                                    self.live_count_control.value -= 1
                                else:
                                    self.blank_count_control.value -= 1
                        elif 'dealer_saw' in live_think_acts or 'dealer_adrenaline_saw' in live_think_acts:
                            result = ''
                            if not action_window:
                                action_window = ActionWindow(self, "HR_dealer_saw" if not 'dealer_adrenaline_saw' in live_think_acts else "HR_dealer_adrenaline_saw", you_prob, dealer_prob, none_prob)
                            else:
                                action_window.update_window("HR_dealer_saw" if not 'dealer_adrenaline_saw' in live_think_acts else "HR_dealer_adrenaline_saw", you_prob, dealer_prob, none_prob)
                            result = action_window.wait_for_result()
                            if not result or not action_window.winfo_exists():
                                raise KeyboardInterrupt()
                            result = 'Yes' if result == 'No' else 'No'
                            print(result)
                            if result == 'No':
                                ti_increase = 2
                                dealer_sawed = True
                                self.remove_dealer_item("Hand Saw" if "dealer_saw" in live_think_acts else "Adrenaline")
                                if "dealer_adrenaline_saw" in live_think_acts:
                                    self.remove_you_item("Hand Saw")
                            else:
                                ti_increase = 1
                        else:
                            turn_index += 1
                            continue
                        if result == 'Yes':
                            for i in range(len(possibility_tree)):
                                deleted = True
                                while deleted:
                                    try:
                                        if 'dealer_think_live' in possibility_tree[i][0][turn_index]:
                                            possibility_tree.pop(i)
                                            deleted = True
                                        else:
                                            deleted = False
                                    except IndexError:
                                        deleted = False
                        elif result == 'No':
                            for i in range(len(possibility_tree)):
                                deleted = True
                                while deleted:
                                    try:
                                        if 'dealer_think_blank' in possibility_tree[i][0][turn_index]:
                                            possibility_tree.pop(i)
                                            deleted = True
                                        else:
                                            deleted = False
                                    except IndexError:
                                        deleted = False
                        elif result == 'Live':
                            for i in range(len(possibility_tree)):
                                deleted = True
                                while deleted:
                                    try:
                                        if '_blank' in possibility_tree[i][0][turn_index + 1]:
                                            possibility_tree.pop(i)
                                            deleted = True
                                        else:
                                            deleted = False
                                    except IndexError:
                                        deleted = False
                        elif result == 'Blank':
                            for i in range(len(possibility_tree)):
                                deleted = True
                                while deleted:
                                    try:
                                        if '_live' in possibility_tree[i][0][turn_index + 1]:
                                            possibility_tree.pop(i)
                                            deleted = True
                                        else:
                                            deleted = False
                                    except IndexError:
                                        deleted = False
                        print(possibility_tree)
                        turn_index += ti_increase
                        continue
                else:
                    actual_action = actions[0]

                if 'dealer_think' in actual_action:
                    turn_index += 1
                    continue

                result = ''
                if not action_window:
                    action_window = ActionWindow(self, actual_action, you_prob, dealer_prob, none_prob)
                else:
                    action_window.update_window(actual_action, you_prob, dealer_prob, none_prob)
                result = action_window.wait_for_result()
                if not result or not action_window.winfo_exists():
                    raise KeyboardInterrupt()
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
                elif result == "Yes" and 'HR' in actual_action:
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
                elif result == "No" and 'HR' in actual_action:
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
                elif result == "Yes" and 'MR' in actual_action:
                    for i in range(len(possibility_tree)):
                        deleted = True
                        while deleted:
                            try:
                                if not "exp_hit" in possibility_tree[i][0][turn_index]:
                                    possibility_tree.pop(i)
                                    deleted = True
                                else:
                                    deleted = False
                            except IndexError:
                                deleted = False
                elif result == "No" and 'MR' in actual_action:
                    for i in range(len(possibility_tree)):
                        deleted = True
                        while deleted:
                            try:
                                if "exp_hit" in possibility_tree[i][0][turn_index]:
                                    possibility_tree.pop(i)
                                    deleted = True
                                else:
                                    deleted = False
                            except IndexError:
                                deleted = False

                final_action = possibility_tree[0][0][turn_index]
                if 'you_saw' in final_action:
                    self.remove_you_item("Hand Saw")
                    you_sawed = True
                elif 'you_adrenaline_saw' in final_action:
                    self.remove_dealer_item("Hand Saw")
                    self.remove_you_item("Adrenaline")
                    you_sawed = True
                elif 'you_invert' in final_action:
                    self.remove_you_item("Inverter")
                    you_inverted = True
                elif 'you_adrenaline_invert' in final_action:
                    self.remove_you_item("Adrenaline")
                    self.remove_dealer_item("Inverter")
                    you_inverted = True
                elif 'you_beer' in final_action:
                    self.remove_you_item("Beer")
                elif 'you_adrenaline_beer' in final_action:
                    self.remove_you_item("Adrenaline")
                    self.remove_dealer_item("Beer")
                elif 'you_glass' in final_action:
                    self.remove_you_item("Magnifying Glass")
                elif 'you_adrenaline_glass' in final_action:
                    self.remove_you_item("Adrenaline")
                    self.remove_dealer_item("Magnifying Glass")
                elif 'you_cig' in final_action:
                    self.remove_you_item("Cigarettes")
                    self.you_hp_control.value += 1
                elif 'you_adrenaline_cig' in final_action:
                    self.remove_you_item("Adrenaline")
                    self.remove_dealer_item("Cigarettes")
                    self.you_hp_control.value += 1
                elif 'you_exp' in final_action:
                    if 'hit' in final_action:
                        self.you_hp_control.value += 1
                    elif 'miss' in final_action:
                        self.you_hp_control.decrement()
                        self.you_hp_control.decrement()
                    self.remove_you_item("Expired Medicine")
                elif 'you_adrenaline_exp' in final_action:
                    if 'hit' in final_action:
                        self.you_hp_control.value += 1
                    elif 'miss' in final_action:
                        self.you_hp_control.decrement()
                        self.you_hp_control.decrement()
                    self.remove_you_item("Adrenaline")
                    self.remove_dealer_item("Expired Medicine")
                elif 'you_cuff' in final_action:
                    self.remove_you_item("Handcuffs")
                elif 'you_adrenaline_cuff' in final_action:
                    self.remove_you_item("Adrenaline")
                    self.remove_dealer_item("Handcuffs")
                elif 'you_shoot_self_live' in final_action:
                    self.you_hp_control.decrement()
                elif 'you_shoot_op_live' in final_action:
                    self.dealer_hp_control.decrement()
                    if you_sawed:
                        self.dealer_hp_control.decrement()
                        you_sawed = False
                elif 'you_shoot_op_blank' in final_action:
                    you_sawed = False
                elif 'dealer_shoot_self_live' in final_action:
                    self.dealer_hp_control.decrement()
                elif 'dealer_shoot_op_live' in final_action:
                    self.you_hp_control.decrement()
                    if dealer_sawed:
                        self.you_hp_control.decrement()
                        dealer_sawed = False
                elif 'dealer_shoot_op_blank' in final_action:
                    dealer_sawed = False

                if 'live' in final_action and not 'invert' in final_action:
                    if you_inverted or dealer_inverted:
                        self.blank_count_control.decrement()
                        you_inverted = False
                        dealer_inverted = False
                    else:
                        self.live_count_control.decrement()
                elif 'blank' in final_action and not 'invert' in final_action:
                    if you_inverted or dealer_inverted:
                        self.live_count_control.decrement()
                        you_inverted = False
                        dealer_inverted = False
                    else:
                        self.blank_count_control.decrement()

                print(possibility_tree)
                if not 'CR' in actual_action and not (dealer_potential_saw and result == "No" and not action_common_dealer_saw):
                    turn_index += 1
                game_not_resolved = not len(possibility_tree) == 1

            print(possibility_tree[0][0][-1])
            if possibility_tree[0][0][-1] == "full_end_player_win":
                for i in range(len(possibility_tree[0][0]) - turn_index - 1):
                    result = ''
                    if 'dealer_think' in possibility_tree[0][0][turn_index]:
                        turn_index += 1
                        continue
                    action_window.update_window(possibility_tree[0][0][turn_index], 1.0, 0.0, 0.0)
                    result = action_window.wait_for_result()
                    if not result or not action_window.winfo_exists():
                        raise KeyboardInterrupt()
                    turn_index += 1
                action_window.update_window(possibility_tree[0][0][-1], 1.0, 0.0, 0.0)
                action_window.wait_for_result()
                action_window.destroy()
                raise KeyboardInterrupt()
            elif possibility_tree[0][0][-1] == "full_end_dealer_win":
                action_window.update_window(possibility_tree[0][0][-1], 0.0, 1.0, 0.0)
                action_window.wait_for_result()
                action_window.destroy()
                raise KeyboardInterrupt()
            elif possibility_tree[0][0][-1] == "full_end_no_win":
                for i in range(len(possibility_tree[0][0]) - turn_index - 1):
                    result = ''
                    if 'dealer_think' in possibility_tree[0][0][turn_index]:
                        turn_index += 1
                        continue
                    action_window.update_window(possibility_tree[0][0][turn_index], 0.0, 0.0, 1.0)
                    result = action_window.wait_for_result()
                    if not result or not action_window.winfo_exists():
                        raise KeyboardInterrupt()
                    turn_index += 1
                action_window.update_window(possibility_tree[0][0][-1], 0.0, 0.0, 1.0)
                action_window.wait_for_result()
                action_window.destroy()
                raise KeyboardInterrupt()
        except KeyboardInterrupt:
            pass
        finally:
            possibility_tree = []
            self.after(0, self.enable_controls)
            self.after(0, self.go_btn.config, {"text": "Go"})
            self.after(0, self.calc_label.config, {"text": ""})





    def go(self, you_items, dealer_items, live, blank, dealer_hp, you_hp, max_hp):
        if ((live <= 0) and (blank <= 0)) or (dealer_hp <= 0) or (you_hp <= 0) or (max_hp < you_hp or max_hp < dealer_hp):
            global action_window
            action_window = ActionWindow(self, "IC", 0.0, 0.0, 0.0)
            action_window.wait_for_result()
            action_window.destroy()
            raise KeyboardInterrupt()

        print("\r\n")
        print("Your items:", you_items)
        print("Dealer items:", dealer_items)
        print("Live:Blank", f"{live}:{blank}")
        print("Your Health:Dealer Health", f"{you_hp}:{dealer_hp}")


        global maximum_hp
        maximum_hp = max_hp

        phoned = None
        if "Burner Phone" in you_items and live != 0 and blank != 0:
            action_window = ActionWindow(self,"SR_PR_you_phone", 0.0, 0.0, 0.0, shells=live+blank)
            phoned = action_window.wait_for_result()
            print(phoned)
            if phoned[1] == '':
                raise KeyboardInterrupt()
            action_window.update_window('',0.0,0.0,0.0,destroy=True)
        if not phoned:
            phoned = [0, '']

        result = eval(you_items,dealer_items,live,blank,dealer_hp,you_hp,["full_start"],1.0, None, 'you', phoned=phoned)
        return 'completed'

def eval(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, turn, force_dismiss_search = False, cuffed = None, prev_cuffed = None, phoned = [0,'']):
    if any("full_end_dealer_win" in item for item in path) or any("full_end_player_win" in item for item in path):
        if dealer_hp <= 0 or you_hp <= 0:
            return
        else:
            return None
    if any("full_end_no_win" in item for item in path):
        return

    if dealer_hp <= 0:
        path.append("full_end_player_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return
    if you_hp <= 0:
        path.append("full_end_dealer_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return

    if (live + blank) == 0:
        path.append("full_end_no_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return

    if turn == 'dealer':
        result = sim_dealer_action(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, None, cuffed, prev_cuffed, False, guarantee,phoned)
        return result

    if not phoned[1] or phoned[0] <= 0:
        live_chance = live / (live + blank)
        blank_chance =  blank / (live + blank)
    elif phoned[0] == 1:
        live_chance = 1.0 if phoned[1] == 'Live' else 0.0
        blank_chance = 1.0 if phoned[1] == 'Blank' else 0.0
    elif phoned[1] == 'Live':
        live_chance = (live - 1) / (live - 1 + blank)
        blank_chance = (blank) / (live - 1 + blank)
    elif phoned[1] == 'Blank':
        live_chance = (live) / (live + blank - 1)
        blank_chance = (blank - 1) / (live + blank - 1)

    is_live_likely = live_chance > blank_chance
    is_live_guaranteed = (live_chance == 1.0 or guarantee == 'live' or (phoned[1] == 'Live' and phoned[0] == 1)) and not 'likely_live' in path[-1]
    is_blank_guaranteed = (blank_chance == 1.0 or guarantee == 'blank' or (phoned[1] == 'Blank' and phoned[0] == 1)) and not 'likely_blank' in path[-1]
    is_blank_likely = blank_chance < live_chance
    equally_likely = live_chance == blank_chance

    if (you_items or dealer_items) and not force_dismiss_search:
        if is_live_guaranteed or is_blank_guaranteed:
            passing = ["glass"]
        else:
            passing = []
        search(you_items,dealer_items,live,blank,dealer_hp,you_hp,path,randomness,'live' if is_live_guaranteed else 'blank' if is_blank_guaranteed else None, passing, prev_cuffed, cuffed, phoned)
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
            return
        else:
            path.append("you_shoot_op_live")
            result = eval(you_items, dealer_items, live - 1, blank, dealer_hp - potential_damage, you_hp, path, randomness, None, 'dealer' if cuffed != 'dealer' else 'you', False, None, cuffed, [phoned[0] - 1, phoned[1]])
            return result

    if "Hand Saw" in you_items and live_chance >= blank_chance:
        potential_damage = 2
        you_items.remove("Hand Saw")
        path.append("you_saw")
    else:
        potential_damage = 1

    if is_blank_guaranteed:
        path.append("you_shoot_self_blank")
        result = eval(you_items, dealer_items, live, blank - 1, dealer_hp, you_hp, path, randomness, None, 'you', False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
        return result

    if (live_chance >= blank_chance or 'likely_blank' in path[-1]) and not 'likely_live' in path[-1]:
        result = split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, 'opponent', 'you', live_chance, potential_damage, 'turn', cuffed, prev_cuffed, False, phoned)
        return result
    else:
        result = split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, 'self', 'you', live_chance, potential_damage, 'turn', cuffed, prev_cuffed, False, phoned)
        return result



def split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, action, turn, live_odds, potential_damage = 1, whose = 'turn', cuffed = None, prev_cuffed = None, inverted = False, phoned = [0,'']):
    global possibility_tree
    live_randomness = randomness * live_odds
    blank_randomness = randomness * (1 - live_odds)

    if not phoned[1] or phoned[0] <= 0:
        live_chance = live / (live + blank)
        blank_chance =  blank / (live + blank)
    elif phoned[0] == 1:
        live_chance = 1.0 if phoned[1] == 'Live' else 0.0
        blank_chance = 1.0 if phoned[1] == 'Blank' else 0.0
    elif phoned[1] == 'Live':
        live_chance = (live - 1) / (live - 1 + blank)
        blank_chance = (blank) / (live - 1 + blank)
    elif phoned[1] == 'Blank':
        live_chance = (live) / (live + blank - 1)
        blank_chance = (blank - 1) / (live + blank - 1)


    if action == 'dealer_shoot_choice':
        stored_path = path.copy()
        stored_you_items = you_items.copy()
        stored_dealer_items = dealer_items.copy()
        op_eval = sim_dealer_action(stored_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp, stored_path.copy(), randomness * 0.5,'opponent', cuffed, prev_cuffed, inverted, phoned=phoned)
        op_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        self_eval = sim_dealer_action(stored_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp, stored_path.copy(), randomness * 0.5, 'self', cuffed, prev_cuffed, inverted, phoned=phoned)
        self_ptree = deepcopy(possibility_tree)
        possibility_tree = op_ptree + self_ptree
        return
    elif action == 'dealer_shoot_choice_with_certainty':
        stored_path = path.copy()
        stored_you_items = you_items.copy()
        stored_dealer_items = dealer_items.copy()
        op_eval = sim_dealer_action(stored_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp, stored_path.copy(), randomness * 0.5,'opponent', cuffed, prev_cuffed, False, 'live', phoned)
        op_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        self_eval = sim_dealer_action(stored_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp, stored_path.copy(), randomness * 0.5, 'self', cuffed, prev_cuffed, False, 'blank', phoned)
        self_ptree = deepcopy(possibility_tree)
        possibility_tree = op_ptree + self_ptree
        return

    if action == 'beer':
        if turn == 'you':
            if whose == 'turn':
                stored_path = path.copy()
                stored_dealer_items = dealer_items.copy()
                new_you_items = you_items.copy()
                new_you_items.remove("Beer")
                live_path = stored_path.copy()
                live_path.append("you_beer_live")
                live_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("you_beer_blank")
                blank_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
            elif whose == 'other':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Beer")
                new_you_items = you_items.copy()
                new_you_items.remove("Adrenaline")
                live_path = stored_path.copy()
                live_path.append("you_adrenaline_beer_live")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("you_adrenaline_beer_blank")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
        elif turn == 'dealer':
            if whose == 'turn':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Beer")
                stored_you_items = you_items.copy()
                live_path = stored_path.copy()
                live_path.append("dealer_beer_live")
                live_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_beer_blank")
                blank_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
            elif whose == 'other':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Adrenaline")
                new_you_items = you_items.copy()
                new_you_items.remove("Beer")
                live_path = stored_path.copy()
                live_path.append("dealer_adrenaline_beer_live")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_adrenaline_beer_blank")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return

    if action == 'exp':
        if turn == 'you':
            if whose == 'turn':
                stored_path = path.copy()
                stored_dealer_items = dealer_items.copy()
                new_you_items = you_items.copy()
                new_you_items.remove("Expired Medicine")
                live_path = stored_path.copy()
                live_path.append("you_exp_hit")
                live_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, (you_hp + 2) if (you_hp + 2) <= maximum_hp else (you_hp + 1) , live_path.copy(), randomness * 0.5, None, turn, False, cuffed, prev_cuffed, phoned)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("you_exp_miss")
                blank_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp - 1, blank_path.copy(), randomness * 0.5, None, turn, False, cuffed, prev_cuffed, phoned)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
            elif whose == 'other':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Expired Medicine")
                new_you_items = you_items.copy()
                new_you_items.remove("Adrenaline")
                live_path = stored_path.copy()
                live_path.append("you_adrenaline_exp_hit")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank, dealer_hp, (you_hp + 2) if (you_hp + 2) <= maximum_hp else (you_hp + 1), live_path.copy(), randomness * 0.5, None, turn, False, cuffed, prev_cuffed, phoned)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("you_adrenaline_exp_miss")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank, dealer_hp, you_hp - 1, blank_path.copy(), randomness * 0.5, None, turn, False, cuffed, prev_cuffed, phoned)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
        elif turn == 'dealer':
            if whose == 'turn':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Expired Medicine")
                stored_you_items = you_items.copy()
                live_path = stored_path.copy()
                live_path.append("dealer_exp_hit")
                live_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live, blank, (dealer_hp + 2) if (dealer_hp + 2) <= maximum_hp else (dealer_hp + 1), you_hp, live_path.copy(), randomness * 0.5, None, turn, False, cuffed, prev_cuffed, phoned)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_exp_miss")
                blank_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live, blank, dealer_hp - 1, you_hp, blank_path.copy(), randomness * 0.5, None, turn, False, cuffed, prev_cuffed, phoned)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
            elif whose == 'other':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Adrenaline")
                new_you_items = you_items.copy()
                new_you_items.remove("Expired Medicine")
                live_path = stored_path.copy()
                live_path.append("dealer_adrenaline_exp_hit")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank, (dealer_hp + 2) if (dealer_hp + 2) <= maximum_hp else (dealer_hp + 1), you_hp, live_path.copy(), randomness * 0.5, None, turn, False, cuffed, prev_cuffed, phoned)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_adrenaline_exp_miss")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank, dealer_hp - 1, you_hp, blank_path.copy(), randomness * 0.5, None, turn, False, cuffed, prev_cuffed, phoned)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return

    if action == 'invert':
        if turn == 'you':
            if whose == 'turn':
                stored_path = path.copy()
                stored_dealer_items = dealer_items.copy()
                new_you_items = you_items.copy()
                new_you_items.remove("Inverter")
                live_path = stored_path.copy()
                if live / (live + blank) >= blank / (live + blank):
                    live_path.append("you_invert_live_likely_live")
                else:
                    live_path.append("you_invert_live_likely_blank")
                live_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live - 1, blank + 1, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                if live / (live + blank) >= blank / (live + blank):
                    blank_path.append("you_invert_blank_likely_live")
                else:
                    blank_path.append("you_invert_blank_likely_blank")
                blank_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live + 1, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
            elif whose == 'other':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Inverter")
                new_you_items = you_items.copy()
                new_you_items.remove("Adrenaline")
                live_path = stored_path.copy()
                if live_chance >= blank_chance:
                    live_path.append("you_adrenaline_invert_live_likely_live")
                else:
                    live_path.append("you_adrenaline_invert_live_likely_blank")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live - 1, blank + 1, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                if live_chance >= blank_chance:
                    blank_path.append("you_adrenaline_invert_blank_likely_live")
                else:
                    blank_path.append("you_adrenaline_invert_blank_likely_blank")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live + 1, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
        elif turn == 'dealer':
            if whose == 'turn':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Inverter")
                stored_you_items = you_items.copy()
                live_path = stored_path.copy()
                live_path.append("dealer_invert_live")
                live_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live - 1, blank + 1, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_invert_blank")
                blank_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live + 1, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
            elif whose == 'other':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Adrenaline")
                new_you_items = you_items.copy()
                new_you_items.remove("Inverter")
                live_path = stored_path.copy()
                live_path.append("dealer_adrenaline_invert_live")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live - 1, blank + 1, dealer_hp, you_hp, live_path.copy(), live_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_adrenaline_invert_blank")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live + 1, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None, turn, False, cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return

    if action == 'glass':
        if turn == 'you':
            if whose == 'turn':
                stored_path = path.copy()
                new_you_items = you_items.copy()
                new_you_items.remove("Magnifying Glass")
                stored_dealer_items = dealer_items.copy()
                live_path = stored_path.copy()
                live_path.append("you_glass_live")
                live_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, "live", turn, False, cuffed, prev_cuffed, phoned)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("you_glass_blank")
                blank_eval = eval(new_you_items.copy(), stored_dealer_items.copy(), live, blank, dealer_hp, you_hp, blank_path.copy(), blank_randomness, "blank", turn, False, cuffed, prev_cuffed, phoned)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
            elif whose == 'other':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Magnifying Glass")
                new_you_items = you_items.copy()
                new_you_items.remove("Adrenaline")
                live_path = stored_path.copy()
                live_path.append("you_adrenaline_glass_live")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, "live", turn, False, cuffed, prev_cuffed, phoned)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("you_adrenaline_glass_blank")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank, dealer_hp, you_hp, blank_path.copy(), blank_randomness, "blank", turn, False, cuffed, prev_cuffed, phoned)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
        elif turn == 'dealer':
            if whose == 'turn':
                stored_path = path.copy()
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Magnifying Glass")
                stored_you_items = you_items.copy()
                live_path = stored_path.copy()
                live_path.append("dealer_glass_live")
                live_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, "live", turn, False, cuffed, prev_cuffed, phoned)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_glass_blank")
                blank_eval = eval(stored_you_items.copy(), new_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, "blank", turn, False, cuffed, prev_cuffed, phoned)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return
            elif whose == 'other':
                stored_path = path.copy()
                new_you_items = you_items.copy()
                new_you_items.remove("Magnifying Glass")
                new_dealer_items = dealer_items.copy()
                new_dealer_items.remove("Adrenaline")
                live_path = stored_path.copy()
                live_path.append("dealer_adrenaline_glass_live")
                live_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp, live_path.copy(),live_randomness, "live", turn, False, cuffed, prev_cuffed, phoned)
                live_ptree = deepcopy(possibility_tree)
                possibility_tree = []
                blank_path = stored_path.copy()
                blank_path.append("dealer_adrenaline_glass_blank")
                blank_eval = eval(new_you_items.copy(), new_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(),blank_randomness, "blank", turn, False, cuffed, prev_cuffed, phoned)
                blank_ptree = deepcopy(possibility_tree)
                possibility_tree = live_ptree + blank_ptree
                return

    if action == 'self':
        if turn == 'dealer':
            stored_path = path.copy()
            stored_you_items = you_items.copy()
            stored_dealer_items = dealer_items.copy()
            live_path = stored_path.copy()
            live_path.append("dealer_shoot_self_live")
            live_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live - 1, blank, dealer_hp - 1, you_hp, live_path.copy(), live_randomness, None, 'you' if cuffed != 'you' else 'dealer', False, None, cuffed, [phoned[0] - 1, phoned[1]])
            live_ptree = deepcopy(possibility_tree)
            possibility_tree = []
            blank_path = stored_path.copy()
            blank_path.append("dealer_shoot_self_blank")
            blank_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'dealer', False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
            blank_ptree = deepcopy(possibility_tree)
            possibility_tree = live_ptree + blank_ptree
            return
        elif turn == 'you':
            stored_path = path.copy()
            stored_you_items = you_items.copy()
            stored_dealer_items = dealer_items.copy()
            live_path = stored_path.copy()
            live_path.append("you_shoot_self_live")
            live_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live - 1, blank, dealer_hp, you_hp - 1, live_path.copy(), live_randomness, None, 'dealer' if cuffed != 'dealer' else 'you', False, None, cuffed, [phoned[0] - 1, phoned[1]])
            live_ptree = deepcopy(possibility_tree)
            possibility_tree = []
            blank_path = stored_path.copy()
            blank_path.append("you_shoot_self_blank")
            blank_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'you', False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
            blank_ptree = deepcopy(possibility_tree)
            possibility_tree = live_ptree + blank_ptree
            return
    elif action == 'opponent':
        if turn == 'dealer':
            stored_path = path.copy()
            stored_you_items = you_items.copy()
            stored_dealer_items = dealer_items.copy()
            live_path = stored_path.copy()
            live_path.append("dealer_shoot_op_live")
            live_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), (live - 1) if not inverted else live, blank if not inverted else (blank - 1), dealer_hp, you_hp - potential_damage, live_path.copy(), live_randomness, None, 'you' if cuffed != 'you' else 'dealer', False, None, cuffed, [phoned[0] - 1, phoned[1]])
            live_ptree = deepcopy(possibility_tree)
            possibility_tree = []
            blank_path = stored_path.copy()
            blank_path.append("dealer_shoot_op_blank")
            blank_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live if not inverted else (live - 1), (blank - 1) if not inverted else blank, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'you' if cuffed != 'you' else 'dealer', False, None, cuffed, [phoned[0] - 1, phoned[1]])
            blank_ptree = deepcopy(possibility_tree)
            possibility_tree = live_ptree + blank_ptree
            return
        elif turn == 'you':
            stored_path = path.copy()
            stored_you_items = you_items.copy()
            stored_dealer_items = dealer_items.copy()
            live_path = stored_path.copy()
            live_path.append("you_shoot_op_live")
            live_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live - 1, blank, dealer_hp - potential_damage, you_hp, live_path.copy(), live_randomness, None,'dealer' if cuffed != 'dealer' else 'you', False, None, cuffed, [phoned[0] - 1, phoned[1]])
            live_ptree = deepcopy(possibility_tree)
            possibility_tree = []
            blank_path = stored_path.copy()
            blank_path.append("you_shoot_op_blank")
            blank_eval = eval(stored_you_items.copy(), stored_dealer_items.copy(), live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'dealer' if cuffed != 'dealer' else 'you', False, None, cuffed, [phoned[0] - 1, phoned[1]])
            blank_ptree = deepcopy(possibility_tree)
            possibility_tree = live_ptree + blank_ptree
            return


def sim_dealer_action(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, choice = None, cuffed = None, prev_cuffed = None, inverted = False, guarantee = None, phoned = [0,'']):
    if any("full_end_dealer_win" in item for item in path) or any("full_end_player_win" in item for item in path):
        if dealer_hp <= 0 or you_hp <= 0:
            return
        else:
            return None
    if any("full_end_no_win" in item for item in path):
        return

    if dealer_hp <= 0:
        path.append("full_end_player_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return
    elif you_hp <= 0:
        path.append("full_end_dealer_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return

    if (live + blank) == 0:
        path.append("full_end_no_win")
        possibility_tree.append([path, randomness, you_hp, dealer_hp])
        return

    live_chance = live / (live + blank)
    blank_chance = blank / (live + blank)
    is_live_guaranteed = (live_chance == 1.0) or guarantee == 'live'
    is_blank_guaranteed = (blank_chance == 1.0) or guarantee == 'blank'
    if not phoned[1] or phoned[0] <= 0:
        live_chance = live / (live + blank)
        blank_chance =  blank / (live + blank)
    elif phoned[0] == 1:
        live_chance = 1.0 if phoned[1] == 'Live' else 0.0
        blank_chance = 1.0 if phoned[1] == 'Blank' else 0.0
    elif phoned[1] == 'Live':
        live_chance = (live - 1) / (live - 1 + blank)
        blank_chance = (blank) / (live - 1 + blank)
    elif phoned[1] == 'Blank':
        live_chance = (live) / (live + blank - 1)
        blank_chance = (blank - 1) / (live + blank - 1)


    if "Burner Phone" in dealer_items:
        new_dealer_items = dealer_items.copy()
        new_dealer_items.remove("Burner Phone")
        new_path = path.copy()
        new_path.append("dealer_phone")
        sim_dealer_action(you_items, new_dealer_items.copy(), live, blank, dealer_hp, you_hp, new_path.copy(), randomness, choice, cuffed, prev_cuffed, inverted, guarantee, phoned)
        return
    elif "Cigarette Pack" in dealer_items and dealer_hp < maximum_hp:
        new_dealer_items = dealer_items.copy()
        new_dealer_items.remove("Cigarette Pack")
        new_path = path.copy()
        new_path.append("dealer_cig")
        sim_dealer_action(you_items, new_dealer_items.copy(), live, blank, dealer_hp+1, you_hp, new_path.copy(),randomness, choice, cuffed, prev_cuffed, inverted, guarantee, phoned)
        return
    elif "Cigarette Pack" in you_items and "Adrenaline" in dealer_items and dealer_hp < maximum_hp:
        new_dealer_items = dealer_items.copy()
        new_dealer_items.remove("Adrenaline")
        new_you_items = you_items.copy()
        new_you_items.remove("Cigarette Pack")
        new_path = path.copy()
        new_path.append("dealer_adrenaline_cig")
        sim_dealer_action(new_you_items.copy(), new_dealer_items.copy(), live, blank, dealer_hp+1, you_hp, new_path.copy(),randomness, choice, cuffed, prev_cuffed, inverted, guarantee, phoned)
        return


    if "Expired Medicine" in dealer_items and dealer_hp + 1 < maximum_hp and dealer_hp != 1:
        split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "exp", "dealer", live_chance, 1, 'turn', cuffed, prev_cuffed, inverted, phoned)
        return
    elif "Expired Medicine" in you_items and "Adrenaline" in dealer_items and dealer_hp + 1 < maximum_hp and dealer_hp != 1:
        split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "exp", "dealer", live_chance, 1, 'other', cuffed, prev_cuffed, inverted, phoned)
        return

    if "Magnifying Glass" in dealer_items and not is_blank_guaranteed and not is_live_guaranteed and not choice:
        new_dealer_items = dealer_items.copy()
        new_dealer_items.remove("Magnifying Glass")
        new_path = path.copy()
        new_path.append("dealer_glass")
        split(you_items, new_dealer_items.copy(), live, blank, dealer_hp, you_hp, new_path.copy(), randomness, 'dealer_shoot_choice_with_certainty','dealer', live_chance, 1, 'turn', cuffed, prev_cuffed, inverted, phoned)
        return
    elif "Magnifying Glass" in you_items and "Adrenaline" in dealer_items and not is_blank_guaranteed and not is_live_guaranteed and not choice:
        new_dealer_items = dealer_items.copy()
        new_dealer_items.remove("Adrenaline")
        new_you_items = you_items.copy()
        new_you_items.remove("Magnifying Glass")
        new_path = path.copy()
        new_path.append("dealer_adrenaline_glass")
        split(you_items, new_dealer_items.copy(), live, blank, dealer_hp, you_hp, new_path.copy(), randomness, 'dealer_shoot_choice_with_certainty','dealer', live_chance, 1, 'turn', cuffed, prev_cuffed, inverted, phoned)
        return

    if "Handcuffs" in dealer_items and not prev_cuffed == 'you' and not cuffed == 'you':
        new_dealer_items = dealer_items.copy()
        new_dealer_items.remove("Handcuffs")
        new_path = path.copy()
        new_path.append("dealer_cuff")
        sim_dealer_action(you_items, new_dealer_items.copy(), live, blank, dealer_hp, you_hp, new_path.copy(), randomness, choice, 'you', None, inverted, guarantee, phoned)
        return
    elif "Handcuffs" in you_items and "Adrenaline" in dealer_items and not prev_cuffed == 'you' and not cuffed == 'you':
        new_dealer_items = dealer_items.copy()
        new_dealer_items.remove("Adrenaline")
        new_you_items = you_items.copy()
        new_you_items.remove("Handcuffs")
        new_path = path.copy()
        new_path.append("dealer_adrenaline_cuff")
        sim_dealer_action(you_items, new_dealer_items.copy(), live, blank, dealer_hp, you_hp, new_path.copy(), randomness, choice, 'you', None, inverted, guarantee, phoned)
        return

    if not is_blank_guaranteed and not is_live_guaranteed and not choice:
        split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness,'dealer_shoot_choice', 'dealer', live_chance, 1, 'turn', cuffed, prev_cuffed, inverted, phoned)
        return

    if choice == "opponent" or is_live_guaranteed:
        path.append("dealer_think_live")
        if "Hand Saw" in dealer_items:
            dealer_items.remove("Hand Saw")
            path.append("dealer_saw")
            potential_damage = 2
            if guarantee == 'live':
                is_live_guaranteed = True
        elif "Adrenaline" in dealer_items and "Hand Saw" in you_items:
            dealer_items.remove("Adrenaline")
            you_items.remove("Hand Saw")
            path.append("dealer_adrenaline_saw")
            potential_damage = 2
            if guarantee == 'live':
                is_live_guaranteed = True
        else:
            potential_damage = 1
        if not is_live_guaranteed:
            split(you_items,dealer_items,live,blank,dealer_hp,you_hp,path,randomness,'opponent','dealer',live_chance, potential_damage, 'turn', cuffed, prev_cuffed, inverted, phoned)
            return
        else:
            path.append("dealer_shoot_op_live")
            eval(you_items,dealer_items,live - 1,blank,dealer_hp,you_hp - potential_damage,path,randomness,None,'you' if cuffed != 'you' else 'dealer',False,None,cuffed,[phoned[0] - 1, phoned[1]])
            return
    elif choice == "self" or is_blank_guaranteed:
        path.append("dealer_think_blank")
        if "Inverter" in dealer_items:
            new_dealer_items = dealer_items.copy()
            new_dealer_items.remove("Inverter")
            new_path = path.copy()
            new_path.append("dealer_invert")
            sim_dealer_action(you_items, new_dealer_items.copy(), live if not is_blank_guaranteed else (live + 1), blank if not is_blank_guaranteed else (blank - 1), dealer_hp, you_hp,new_path.copy(), randomness, 'opponent', cuffed, prev_cuffed, True, 'live' if guarantee == 'blank' else None, phoned)
            return
        elif "Inverter" in you_items and "Adrenaline" in dealer_items:
            new_dealer_items = dealer_items.copy()
            new_dealer_items.remove("Adrenaline")
            new_you_items = you_items.copy()
            new_you_items.remove("Inverter")
            new_path = path.copy()
            new_path.append("dealer_adrenaline_invert")
            sim_dealer_action(new_you_items.copy(), new_dealer_items.copy(), live if not is_blank_guaranteed else (live + 1), blank if not is_blank_guaranteed else (blank - 1), dealer_hp, you_hp,new_path.copy(), randomness, 'opponent', cuffed, prev_cuffed, True, 'live' if guarantee == 'blank' else None, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
            return
        elif "Beer" in dealer_items:
            split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "beer", "dealer", live_chance, 1, 'turn', cuffed, prev_cuffed, inverted, phoned)
            return
        elif "Beer" in you_items and "Adrenaline" in dealer_items:
            split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "beer", "dealer", live_chance, 1, 'other', cuffed, prev_cuffed, inverted, phoned)
            return
        if not is_blank_guaranteed:
            split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, 'self', 'dealer',live_chance, 1, 'turn', cuffed, prev_cuffed, inverted, phoned)
        else:
            path.append("dealer_shoot_self_blank")
            eval(you_items,dealer_items,live,blank-1,dealer_hp,you_hp,path,randomness,None,'dealer',False,cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
        return
    path.append("dealer_sim_here")
    return

def search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, passed, prev_cuffed = None, cuffed = None, phoned = [0,'']):
    global possibility_tree
    starting_ptree = deepcopy(possibility_tree)
    possibility_tree = []
    alpha_ptree = []
    beta_ptree = []
    global maximum_hp

    if not phoned[1] or phoned[0] <= 0:
        live_chance = live / (live + blank)
        blank_chance =  blank / (live + blank)
    elif phoned[0] == 1:
        live_chance = 1.0 if phoned[1] == 'Live' else 0.0
        blank_chance = 1.0 if phoned[1] == 'Blank' else 0.0
    elif phoned[1] == 'Live':
        live_chance = (live - 1) / (live - 1 + blank)
        blank_chance = (blank) / (live - 1 + blank)
    elif phoned[1] == 'Blank':
        live_chance = (live) / (live + blank - 1)
        blank_chance = (blank - 1) / (live + blank - 1)

    if not guarantee:
        if live_chance == 1.0:
            guarantee = 'live'
        elif blank_chance == 1.0:
            guarantee = 'blank'

    if "Handcuffs" in you_items and not "cuffs" in passed and not prev_cuffed == 'dealer' and not cuffed == 'dealer':
        new_you_items = you_items.copy()
        new_you_items.remove("Handcuffs")
        new_path = path.copy()
        new_path.append("you_cuff")
        eval(new_you_items.copy(),dealer_items,live,blank,dealer_hp,you_hp,new_path.copy(),randomness,guarantee,'you',False,'dealer',None, phoned)
        alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("cuffs")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        beta_ptree = deepcopy(possibility_tree)
        action_done = True
    elif "Magnifying Glass" in you_items and not "glass" in passed:
        split(you_items,dealer_items,live,blank,dealer_hp,you_hp,path,randomness,"glass", "you", live / (live + blank), 1, 'turn', cuffed, prev_cuffed, False, phoned)
        alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("glass")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        beta_ptree = deepcopy(possibility_tree)
        action_done = True
    elif "Inverter" in you_items and not "invert" in passed:
        if guarantee:
            new_you_items = you_items.copy()
            new_you_items.remove("Inverter")
            if guarantee == 'live':
                new_path = path.copy()
                new_path.append("you_invert_live")
                eval(new_you_items.copy(),dealer_items,live-1,blank+1,dealer_hp,you_hp,new_path.copy(),randomness,'blank','you',False,cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
            elif guarantee == 'blank':
                new_path = path.copy()
                new_path.append("you_invert_blank")
                eval(new_you_items.copy(),dealer_items,live+1,blank-1,dealer_hp,you_hp,new_path.copy(),randomness,'live','you',False,cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
        else:
            split(you_items,dealer_items,live,blank,dealer_hp,you_hp,path,randomness,"invert", "you", live_chance, 1, 'turn', cuffed, prev_cuffed,False, phoned)
        alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("invert")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        beta_ptree = deepcopy(possibility_tree)
        action_done = True
    elif "Beer" in you_items and not "beer" in passed:
        if guarantee:
            newpath = path.copy()
            newpath.append(f"you_beer_{guarantee}")
            new_you_items = you_items.copy()
            new_you_items.remove("Beer")
            if guarantee == 'live':
                eval(new_you_items,dealer_items,live - 1,blank,dealer_hp,you_hp,newpath,randomness,None,'you', False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
            elif guarantee == 'blank':
                eval(new_you_items,dealer_items,live,blank - 1,dealer_hp,you_hp,newpath,randomness,None,'you', False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
        else:
            split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "beer", "you", live_chance, 1, 'turn', cuffed, prev_cuffed, False, phoned)
        alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("beer")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        beta_ptree = deepcopy(possibility_tree)
        action_done = True
    elif "Cigarette Pack" in you_items and not "cig" in passed and you_hp < maximum_hp:
        new_you_items = you_items.copy()
        new_you_items.remove("Cigarette Pack")
        new_path = path.copy()
        new_path.append("you_cig")
        eval(new_you_items.copy(),dealer_items,live,blank,dealer_hp,you_hp+1,new_path.copy(),randomness,guarantee,'you', False, cuffed, prev_cuffed, phoned)
        alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("cig")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        beta_ptree = deepcopy(possibility_tree)
        action_done = True
    elif "Expired Medicine" in you_items and not "exp" in passed and you_hp < maximum_hp:
        split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "exp", "you", live_chance, 1, 'turn', cuffed, prev_cuffed, False, phoned)
        alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("exp")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        beta_ptree = deepcopy(possibility_tree)
        action_done = True
    elif "Adrenaline" in you_items and not "adrenaline" in passed:
        if dealer_items:
            adrenaline(you_items,dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, passed, prev_cuffed, cuffed, phoned)
            return
        else:
            newpassed = passed.copy()
            newpassed.append("adrenaline")
            search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, newpassed, prev_cuffed, cuffed, phoned)
            return
    else:
        eval(you_items,dealer_items,live,blank,dealer_hp,you_hp,path,randomness,guarantee,'you', True, cuffed, prev_cuffed, phoned)
        return

    a_full_prob = 0.0
    for i in range(len(alpha_ptree)):
        a_full_prob += alpha_ptree[i][1]

    if a_full_prob == 0.0:
        a_full_prob = 1.0

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

    if b_full_prob == 0.0:
        b_full_prob = 1.0

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
            if (alpha_ptree[i][1] * (1/ a_full_prob)) != 0.0:
                alpha_rating += (alpha_ptree[i][2] - alpha_ptree[i][3]) / (alpha_ptree[i][1] * (1/ a_full_prob))
        beta_rating = 0
        for i in range(len(beta_ptree)):
            if (beta_ptree[i][1] * (1/ b_full_prob)) != 0.0:
                beta_rating += (beta_ptree[i][2] - beta_ptree[i][3]) / (beta_ptree[i][1] * (1/ b_full_prob))
        if alpha_rating > beta_rating and not isclose(alpha_rating, beta_rating, rel_tol=1e-12, abs_tol=0.0):
            possibility_tree = starting_ptree + alpha_ptree
        else:
            possibility_tree = starting_ptree + beta_ptree

def adrenaline(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, passed, prev_cuffed = None, cuffed = None, phoned = [0,'']):
    global possibility_tree
    a_starting_ptree = deepcopy(possibility_tree)
    possibility_tree = []
    a_alpha_ptree = []
    a_beta_ptree = []

    if not phoned[1] or phoned[0] <= 0:
        live_chance = live / (live + blank)
        blank_chance =  blank / (live + blank)
    elif phoned[0] == 1:
        live_chance = 1.0 if phoned[1] == 'Live' else 0.0
        blank_chance = 1.0 if phoned[1] == 'Blank' else 0.0
    elif phoned[1] == 'Live':
        live_chance = (live - 1) / (live - 1 + blank)
        blank_chance = (blank) / (live - 1 + blank)
    elif phoned[1] == 'Blank':
        live_chance = (live) / (live + blank - 1)
        blank_chance = (blank - 1) / (live + blank - 1)

    if "Handcuffs" in dealer_items and not "cuffs" in passed and not prev_cuffed == 'dealer' and not cuffed == 'dealer':
        a_new_you_items = you_items.copy()
        a_new_you_items.remove("Adrenaline")
        a_new_dealer_items = dealer_items.copy()
        a_new_dealer_items.remove("Handcuffs")
        new_path = path.copy()
        new_path.append("you_adrenaline_cuff")
        eval(a_new_you_items.copy(),a_new_dealer_items.copy(),live,blank,dealer_hp,you_hp,new_path.copy(),randomness,guarantee,'you',False,'dealer',None,phoned)
        a_alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("cuffs")
        adrenaline(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        a_beta_ptree = deepcopy(possibility_tree)
        a_action_done = True
    elif "Magnifying Glass" in dealer_items and not "glass" in passed:
        split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "glass", "you", live_chance, 1, 'other', cuffed, prev_cuffed, False, phoned)
        a_alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("glass")
        adrenaline(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        a_beta_ptree = deepcopy(possibility_tree)
        a_action_done = True
    elif "Inverter" in dealer_items and not "invert" in passed:
        if guarantee:
            a_new_dealer_items = dealer_items.copy()
            a_new_dealer_items.remove("Inverter")
            a_new_you_items = you_items.copy()
            a_new_you_items.remove("Adrenaline")
            if guarantee == 'live':
                new_path = path.copy()
                new_path.append("you_adrenaline_invert_live")
                eval(a_new_you_items.copy(), a_new_dealer_items.copy(), live - 1, blank + 1, dealer_hp, you_hp, new_path.copy(),randomness, 'blank', 'you', False, cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
            elif guarantee == 'blank':
                new_path = path.copy()
                new_path.append("you_adrenaline_invert_blank")
                eval(a_new_you_items.copy(), a_new_dealer_items.copy(), live + 1, blank - 1, dealer_hp, you_hp, new_path.copy(),randomness, 'live', 'you', False, cuffed, prev_cuffed, [phoned[0], phoned[1]] if phoned[0] != 1 else [phoned[0], ('Live' if phoned[1] == 'Blank' else 'Blank')])
        else:
            split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "invert", "you",live_chance, 1, 'other', cuffed, prev_cuffed, False, phoned)
        a_alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("invert")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed,prev_cuffed, cuffed, phoned)
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
                eval(a_new_you_items, a_new_dealer_items, live - 1, blank, dealer_hp, you_hp, a_newpath, randomness, None, 'you', False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
            elif guarantee == 'blank':
                eval(a_new_you_items, a_new_dealer_items, live, blank - 1, dealer_hp, you_hp, a_newpath, randomness, None, 'you', False, cuffed, prev_cuffed, [phoned[0] - 1, phoned[1]])
        else:
            split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "beer", "you", live_chance, 1, 'other', cuffed, prev_cuffed, False, phoned)
        a_alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("beer")
        adrenaline(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        a_beta_ptree = deepcopy(possibility_tree)
        a_action_done = True
    elif "Cigarette Pack" in dealer_items and not "cig" in passed and you_hp < maximum_hp:
        a_new_you_items = you_items.copy()
        a_new_you_items.remove("Adrenaline")
        a_new_dealer_items = dealer_items.copy()
        a_new_dealer_items.remove("Cigarette Pack")
        new_path = path.copy()
        new_path.append("you_adrenaline_cig")
        eval(a_new_you_items.copy(),a_new_dealer_items.copy(),live,blank,dealer_hp,you_hp+1,new_path.copy(),randomness,guarantee,'you', False, cuffed, prev_cuffed, phoned)
        a_alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("cig")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        a_beta_ptree = deepcopy(possibility_tree)
        a_action_done = True
    elif "Expired Medicine" in dealer_items and not "exp" in passed and you_hp < maximum_hp:
        split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, "exp", "you", live_chance, 1, 'other', cuffed, prev_cuffed, False, phoned)
        a_alpha_ptree = deepcopy(possibility_tree)
        possibility_tree = []
        new_passed = passed.copy()
        new_passed.append("exp")
        search(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, new_passed, prev_cuffed, cuffed, phoned)
        a_beta_ptree = deepcopy(possibility_tree)
        a_action_done = True
    else:
        eval(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, 'you', True, cuffed, prev_cuffed, phoned)
        return

    a_a_full_prob = 0.0
    for i in range(len(a_alpha_ptree)):
        a_a_full_prob += a_alpha_ptree[i][1]

    if a_a_full_prob == 0.0:
        a_a_full_prob = 1.0

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

    if a_b_full_prob == 0.0:
        a_b_full_prob = 1.0

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
            if (a_alpha_ptree[i][1] * (1/ a_a_full_prob)) != 0.0:
                a_alpha_rating += (a_alpha_ptree[i][2] - a_alpha_ptree[i][3]) / (a_alpha_ptree[i][1] * (1/ a_a_full_prob))
        a_beta_rating = 0
        for i in range(len(a_beta_ptree)):
            if (a_beta_ptree[i][1] * (1/ a_b_full_prob)) != 0.0:
                a_beta_rating += (a_beta_ptree[i][2] - a_beta_ptree[i][3]) / (a_beta_ptree[i][1] * (1/ a_b_full_prob))
        if a_alpha_rating > a_beta_rating and not isclose(a_alpha_rating, a_beta_rating, rel_tol=1e-12, abs_tol=0.0):
            possibility_tree = a_starting_ptree + a_alpha_ptree
        else:
            possibility_tree = a_starting_ptree + a_beta_ptree


if __name__ == "__main__":
    app = UIApp()
    app.mainloop()
