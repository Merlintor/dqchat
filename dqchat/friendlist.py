import os
import json


class FriendList:
    def __init__(self):
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/friendlist.json")
        self.friends = self._load_friends_from_file()

    def _load_friends_from_file(self):
        try:
            with open(self.path, "r") as fl_file:
                if (os.stat(self.path).st_size == 0):
                    return []
                
                friend_data = json.load(fl_file)

                friends = []
                for item in friend_data.values():
                    friends.append(item)
                
                return friends
        except FileNotFoundError:
            with(open(self.path, "w")):
                return []

    def _update_file(self):
        with open(self.path, "w") as fl_file:
            json_data = {}
            for i in range(len(self.friends)):
                    json_data[str(i)] = {"name": self.friends[i]["name"], "onion": self.friends[i]["onion"]}
            json.dump(json_data, fl_file)


    def get_onion_by_name(self, name):
        for friend in self.friends:
            if (friend["name"] == name):
                return friend["onion"]
        return None     
            
    def get_name_by_onion(self, onion):
        for friend in self.friends:
            if (friend["onion"] == onion):
                return friend["name"]
        return None

    def add_friend(self, name, onion):
        for friend in self.friends:
            if (friend["name"] == name or friend["onion"] == onion):
                print("Friend with similar name or onion already exists")
                return False

        json_object = {"name": name, "onion": onion}
        self.friends.append(json_object)
        self._update_file()
        print("Added %s to the friend list. (%s)" % (name, onion))
        return True
    
    def remove_friend(self, name):
        for friend in self.friends:
            if (friend["name"] == name):
                self.friends.remove(friend)
                self._update_file()
                return True
        print("Removed %s from the friend list. (%s)" % (name))