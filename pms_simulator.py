# pms_simulator.py

class PMSSimulator:
    def __init__(self):
        self.rooms = {
            "101": {"orders": []},  # Store orders for each room
            "102": {"orders": []},
            "103": {"orders": []},
        }
        self.menu = ["cheeseburger", "pizza", "salad"]

    def room_exists(self, room_number):
        return room_number in self.rooms

    def place_order(self, room_number, item):
        if room_number in self.rooms and item in self.menu:
            self.rooms[room_number]["orders"].append(item) #Add orders
            print(f"Order placed for room {room_number}: {item}")
            return True
        return False

pms = PMSSimulator()