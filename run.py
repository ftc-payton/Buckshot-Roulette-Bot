import tkinter as tk
from tkinter import Button, Frame, Canvas

# TODO: add item functionality

possibility_tree = []
result = ''

class ActionWindow:
    def __init__(self, master, initial_action, you_prob, dealer_prob, none_prob):
        self.master = master
        self.actual_action = initial_action
        self.result = None
        self.you_prob = you_prob
        self.dealer_prob = dealer_prob
        self.none_prob = none_prob

        self.action_text_map = {
            "SR_you_shoot_self": "More likely for a blank. Shoot yourself. Click which shell occurred.",
            "SR_you_shoot_op": "More or equally likely for a live round. Shoot the dealer. Click which shell occurred.",
            "SR_dealer_shoot_op": "Which shell did the dealer shoot at you?",
            "SR_dealer_shoot_self": "Which shell did the dealer shoot at itself?",
            "CR_dealer_shoot": "Who did the dealer shoot?",
            "full_end_player_win": "You win!",
            "full_end_dealer_win": "You lose...",
            "full_end_no_win": "Shotgun will be loaded again. You must set the board again, then press go.",
            "you_shoot_op_live": "Shell is guaranteed live. Shoot the dealer.",
            "you_shoot_self_blank": "Shell is guaranteed blank. Shoot yourself.",
            "dealer_shoot_op_live": "Dealer will shoot you with a live round."
        }

        self.win = tk.Toplevel(master)
        self.win.title("Path")
        self.prob_canvas = tk.Canvas(self.win, height=50)
        self.prob_canvas.pack(fill="x", padx=20, pady=(20, 5))
        self.prob_canvas.bind("<Configure>", self.draw_prob_bar)

        self.prob_text_label = tk.Label(
            self.win,
            text="You: {:.1%}   Dealer: {:.1%}   None: {:.1%}".format(
                self.you_prob, self.dealer_prob, self.none_prob
            )
        )
        self.prob_text_label.pack(padx=20, pady=(0, 20))

        self.label = tk.Label(self.win, text="")
        self.label.pack(padx=20, pady=20)

        self.button_frame = tk.Frame(self.win)
        self.button_frame.pack(padx=10, pady=10)

        self.update_display(initial_action)

    def draw_prob_bar(self, event=None):
        width = self.prob_canvas.winfo_width()
        height = self.prob_canvas.winfo_height()

        self.prob_canvas.delete("all")

        you_width = width * self.you_prob
        dealer_width = width * self.dealer_prob
        none_width = width - (you_width + dealer_width)


        self.prob_canvas.create_rectangle(0, 0, you_width, height, fill="green", width=0)

        self.prob_canvas.create_rectangle(you_width, 0, you_width + dealer_width, height, fill="red", width=0)

        self.prob_canvas.create_rectangle(you_width + dealer_width, 0, width, height, fill="yellow", width=0)

    def update_display(self, action):
        self.actual_action = action

        text_to_display = self.action_text_map.get(
            self.actual_action, self.action_text_map[action]
        )
        self.label.config(text=text_to_display)

        for widget in self.button_frame.winfo_children():
            widget.destroy()

        if self.actual_action.startswith("SR_"):
            tk.Button(
                self.button_frame, text="Live",
                command=lambda: self.set_result("Live")
            ).pack(side="left", padx=10)
            tk.Button(
                self.button_frame, text="Blank",
                command=lambda: self.set_result("Blank")
            ).pack(side="left", padx=10)
        elif self.actual_action.startswith("CR_"):
            tk.Button(
                self.button_frame, text="Self",
                command=lambda: self.set_result("Self")
            ).pack(side="left", padx=10)
            tk.Button(
                self.button_frame, text="You",
                command=lambda: self.set_result("You")
            ).pack(side="left", padx=10)
        else:
            tk.Button(
                self.button_frame, text="Next",
                command=lambda: self.set_result("Next")
            ).pack(padx=10)

    def set_result(self, choice):
        global result
        result = choice

        self.win.destroy()


class NumericControl(tk.Frame):
    def __init__(self, master, initial_value=0, callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.value = initial_value
        self.callback = callback  # Called whenever the value changes.

        self.minus_btn = tk.Button(self, text="–", width=2, command=self.decrement)
        self.minus_btn.grid(row=0, column=0)

        self.value_label = tk.Label(self, text=str(self.value), width=5, relief="sunken")
        self.value_label.grid(row=0, column=1, padx=2)

        self.plus_btn = tk.Button(self, text="+", width=2, command=self.increment)
        self.plus_btn.grid(row=0, column=2)

    def increment(self):
        self.value += 1
        self.value_label.config(text=str(self.value))
        if self.callback:
            self.callback()

    def decrement(self):
        self.value -= 1
        self.value_label.config(text=str(self.value))
        if self.callback:
            self.callback()


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
        tk.Label(middle_frame, text="Dealer HP:", bg="lightgray", fg="black").grid(row=0, column=0, padx=2)
        self.dealer_hp_control = NumericControl(middle_frame, initial_value=0)
        self.dealer_hp_control.grid(row=0, column=1, padx=2)

        tk.Label(middle_frame, text="Your HP:", bg="lightgray", fg="black").grid(row=1, column=0, padx=2)
        self.you_hp_control = NumericControl(middle_frame, initial_value=0)
        self.you_hp_control.grid(row=1, column=1, padx=2)

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


        global possibility_tree
        possibility_tree = []

        # items will not be passed to go until full functionality is implemented
        evaluated = self.go([], [], live_rounds, blanks, dealer_hp, player_hp)
        if not evaluated:
            return

        print(possibility_tree)


        game_not_resolved = True
        turn_index = 1
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
            action_window = ActionWindow(self, actual_action, you_prob, dealer_prob, none_prob)
            self.wait_window(action_window.win)
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
            print(possibility_tree)
            if not 'CR' in actual_action:
                turn_index += 1
            game_not_resolved = not len(possibility_tree) == 1

        print(possibility_tree[0][0][-1])
        if possibility_tree[0][0][-1] == "full_end_player_win":
            for i in range(len(possibility_tree[0][0]) - turn_index - 1):
                action_window = ActionWindow(self, possibility_tree[0][0][turn_index], 1.0, 0.0, 0.0)
                self.wait_window(action_window.win)
                turn_index += 1
            action_window = ActionWindow(self, possibility_tree[0][0][-1], 1.0, 0.0, 0.0)
            self.wait_window(action_window.win)
        elif possibility_tree[0][0][-1] == "full_end_dealer_win":
            action_window = ActionWindow(self, possibility_tree[0][0][-1], 0.0, 1.0, 0.0)
            self.wait_window(action_window.win)
        elif possibility_tree[0][0][-1] == "full_end_none_win":
            action_window = ActionWindow(self, possibility_tree[0][0][-1], 0.0, 0.0, 1.0)
            self.wait_window(action_window.win)





    def go(self, you_items, dealer_items, live, blank, dealer_hp, you_hp):
        if ((live <= 0) and (blank <= 0)) or (dealer_hp <= 0) or (you_hp <= 0):
            print("Invalid configuration!")
            return None

        print("\r\n")
        print("Your items:", you_items)
        print("Dealer items:", dealer_items)
        print("Live:Blank", f"{live}:{blank}")
        print("Your Health:Dealer Health", f"{you_hp}:{dealer_hp}")


        result = eval(you_items,dealer_items,live,blank,dealer_hp,you_hp,["full_start"],1.0, None, 'you')
        return result





def eval(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, guarantee, turn):
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
        result = sim_dealer_action(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness)
        return result

    live_chance = live / (live + blank)
    blank_chance = blank / (live + blank)


    is_live_likely = live_chance > blank_chance
    is_live_guaranteed = live_chance == 1.0 or guarantee == 'live'
    is_blank_guaranteed = blank_chance == 1.0 or guarantee == 'blank'
    is_blank_likely = blank_chance < live_chance
    equally_likely = live_chance == blank_chance

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
            result = eval(you_items, dealer_items, live - 1, blank, dealer_hp - potential_damage, you_hp, path, randomness, None, 'dealer')
            return result

    if not you_items and not dealer_items:
        if is_blank_guaranteed:
            path.append("you_shoot_self_blank")
            result = eval(you_items, dealer_items, live, blank - 1, dealer_hp, you_hp, path, randomness, None, 'you')
            return result

        if live_chance >= blank_chance:
            result = split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, 'opponent', 'you', live_chance)
            return result
        else:
            result = split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, 'self', 'you', live_chance)
            return result

    if is_blank_guaranteed and "Inverter" in you_items:
        you_items.remove("Inverter")
        path.append("you_invert")
        result = eval(you_items,dealer_items,live + 1,blank - 1,dealer_hp,you_hp,path,randomness, 'live', 'you')
        return result



    # test if live
    live_randomness = randomness * live_chance
    blank_randomness = randomness * blank_chance

def split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, action, turn, live_odds):
    live_randomness = randomness * live_odds
    blank_randomness = randomness * (1 - live_odds)
    if action == 'dealer_shoot_choice':
        stored_path = path.copy()
        op_eval = sim_dealer_action(you_items, dealer_items, live, blank, dealer_hp, you_hp, stored_path.copy(), randomness * 0.5,'opponent')
        self_eval = sim_dealer_action(you_items, dealer_items, live, blank, dealer_hp, you_hp, stored_path.copy(), randomness * 0.5, 'self')
        return [self_eval, op_eval]
    if action == 'beer':
        stored_path = path.copy()
        you_items.remove("Beer")
        live_path = stored_path.copy()
        live_path.append("you_beer_live")
        live_eval = eval(you_items, dealer_items, live - 1, blank, dealer_hp, you_hp, live_path.copy(), live_randomness, None)
        blank_path = stored_path.copy()
        blank_path.append("you_beer_blank")
        blank_eval = eval(you_items, dealer_items, live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None)
        return [live_eval, blank_eval]
    if action == 'self':
        if turn == 'dealer':
            stored_path = path.copy()
            live_path = stored_path.copy()
            live_path.append("dealer_shoot_self_live")
            live_eval = eval(you_items, dealer_items, live - 1, blank, dealer_hp - 1, you_hp, live_path.copy(), live_randomness, None, 'you')
            blank_path = stored_path.copy()
            blank_path.append("dealer_shoot_self_blank")
            blank_eval = eval(you_items, dealer_items, live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'dealer')
            return [live_eval, blank_eval]
        elif turn == 'you':
            stored_path = path.copy()
            live_path = stored_path.copy()
            live_path.append("you_shoot_self_live")
            live_eval = eval(you_items, dealer_items, live - 1, blank, dealer_hp, you_hp - 1, live_path.copy(), live_randomness, None, 'dealer')
            blank_path = stored_path.copy()
            blank_path.append("you_shoot_self_blank")
            blank_eval = eval(you_items, dealer_items, live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'you')
            return [live_eval, blank_eval]
    elif action == 'opponent':
        if turn == 'dealer':
            stored_path = path.copy()
            live_path = stored_path.copy()
            live_path.append("dealer_shoot_op_live")
            live_eval = eval(you_items, dealer_items, live - 1, blank, dealer_hp, you_hp - 1, live_path.copy(), live_randomness, None,'you')
            blank_path = stored_path.copy()
            blank_path.append("dealer_shoot_op_blank")
            blank_eval = eval(you_items, dealer_items, live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'you')
            return [live_eval, blank_eval]
        elif turn == 'you':
            stored_path = path.copy()
            live_path = stored_path.copy()
            live_path.append("you_shoot_op_live")
            live_eval = eval(you_items, dealer_items, live - 1, blank, dealer_hp - 1, you_hp, live_path.copy(), live_randomness, None,'dealer')
            blank_path = stored_path.copy()
            blank_path.append("you_shoot_op_blank")
            blank_eval = eval(you_items, dealer_items, live, blank - 1, dealer_hp, you_hp, blank_path.copy(), blank_randomness, None,'dealer')
            return [live_eval, blank_eval]


def sim_dealer_action(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, choice = None):
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

    if not dealer_items:
        if is_live_guaranteed:
            path.append("dealer_shoot_op_live")
            result = eval(you_items, dealer_items, live - 1, blank, dealer_hp, you_hp - 1, path, randomness, None, 'you')
            return result
        elif not is_blank_guaranteed and not choice:
            result = split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, 'dealer_shoot_choice', 'dealer', live_chance)
            return result
        elif not is_blank_guaranteed:
            result = split(you_items, dealer_items, live, blank, dealer_hp, you_hp, path, randomness, choice, 'dealer', live_chance)
            return result
        elif is_blank_guaranteed:
            path.append("dealer_shoot_self_blank")
            result = eval(you_items, dealer_items, live, blank - 1, dealer_hp, you_hp, path, randomness, None, 'dealer')
            return result

    path.append("dealer_sim_here")
    return [path, randomness, you_hp, dealer_hp]

if __name__ == "__main__":
    app = UIApp()
    app.mainloop()
