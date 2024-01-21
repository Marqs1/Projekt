from flask import Flask, jsonify, request
from collections import deque

# Define the Person and Graph classes
class Person:
    def __init__(self, name):
        self.name = name
        self.friends = set()
        self.possessions = set()

    def add_friend(self, friend):
        self.friends.add(friend)

    def add_possession(self, item):
        self.possessions.add(item)

class Graph:
    def __init__(self):
        self.people = {}

    def add_person(self, name):
        if name not in self.people:
            self.people[name] = Person(name)

    def add_friendship(self, name1, name2):
        if name1 in self.people and name2 in self.people:
            self.people[name1].add_friend(name2)
            self.people[name2].add_friend(name1)
        else:
            raise Exception(f"One or both of the people {name1} or {name2} have not been added to the graph.")

    def add_possession(self, name, item):
        if name in self.people:
            self.people[name].add_possession(item)
        else:
            raise Exception(f"Person {name} has not been added to the graph before assigning possessions.")

# Initialize the graph
graph = Graph()

# Define the function to find the shortest path to a person with desired items
def find_path_to_borrow_multiple_items(graph, start_name, items):
    visited = set()
    queue = deque([[start_name]])

    while queue:
        path = queue.popleft()
        person_name = path[-1]

        if person_name not in visited:
            visited.add(person_name)
            person = graph.people.get(person_name)

            if person and all(item in person.possessions for item in items):
                return path  # Return the path to the person who has all the items

            if person:
                for friend in person.friends:
                    if friend not in visited:
                        new_path = list(path)
                        new_path.append(friend)
                        queue.append(new_path)

    return None  # If there is no path to someone with all the items

# Flask app definition
app = Flask(__name__)

# API endpoint to get a list of friends
@app.route('/friends', methods=['GET'])
def get_friends():
    name = request.args.get('name')
    person = graph.people.get(name)
    if person:
        return jsonify({"friends": list(person.friends)})
    else:
        return jsonify({"error": "Person not found"}), 404

# API endpoint to check if two people know each other
@app.route('/knows', methods=['GET'])
def get_knows():
    name1 = request.args.get('person1')
    name2 = request.args.get('person2')
    person1 = graph.people.get(name1)
    if person1 and name2 in person1.friends:
        return jsonify({"knows": True})
    else:
        return jsonify({"knows": False})

# API endpoint to find the shortest path to borrow items
@app.route('/borrow', methods=['GET'])
def get_borrow_path():
    name = request.args.get('name')
    items = request.args.getlist('item')  # Get a list of items
    path = find_path_to_borrow_multiple_items(graph, name, items)
    if path:
        return jsonify({"path": path})
    else:
        return jsonify({"error": "No path found to borrow the items"}), 404

# Main execution
if __name__ == '__main__':
    # Add people to the graph
    people = ['Kamil', 'Magda', 'Ewa', 'Piotr', 'Nikodem', 'Mikolaj', 'Liliana', 'Daniel']
    for person in people:
        graph.add_person(person)

    # Add friendships
    friendships = [
        ('Kamil', 'Magda'), ('Kamil', 'Piotr'), ('Kamil', 'Daniel'),
        ('Magda', 'Liliana'), ('Ewa', 'Magda'), ('Ewa', 'Liliana'),
        ('Ewa', 'Daniel'), ('Piotr', 'Liliana'), ('Nikodem', 'Mikolaj'),
        ('Nikodem', 'Daniel'), ('Mikolaj', 'Daniel')
    ]
    for friend1, friend2 in friendships:
        graph.add_friendship(friend1, friend2)

    # Add possessions
    possessions = {
        'Magda': ['kamera'],
        'Piotr': ['kamera', 'statyw'],
        'Mikolaj': ['kamera'],
        'Liliana': ['kamera']
    }
    for person, items in possessions.items():
        for item in items:
            graph.add_possession(person, item)

    # Start the Flask app
    app.run(debug=True)
