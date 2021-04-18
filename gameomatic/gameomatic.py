class Inventory(object):
	def __init__(self):
		self.items: dict[str, int] = {}

	def __getitem__(self, key) -> int:
		if key not in self.items:
			self.items[key] = 0 # avoid raising KeyError
		return self.items[key]

	def __setitem__(self, key, value) -> None:
		if value < 0:
			value = 0
		self.items[key] = value

	def __delitem__(self, key) -> None:
		del self.items[key]

	def __contains__(self, key) -> bool:
		return key in self.items

	def __iter__(self) -> "tuple[str, int]":
		for i in self.items.items():
			yield i


class Character(object):
	def __init__(self, name: str, items: "dict[str, int]"=None) -> None:
		self.name = name
		self.inventory: Inventory = Inventory()
		if items:
			for item, amount in items.items():
				self.inventory[item] = amount

	def give_item(self, name, amount):
		self.inventory[name] += amount
		if self.inventory[name] == 0:
			print(f"{self.name} is all out of {name}")

	def take_item(self, name, amount):
		self.inventory[name] -= amount
		if self.inventory[name] == 0:
			print(f"{self.name} is all out of {name}")

class Manager(object):
	def __init__(self) -> None:
		self.characters: dict[str, Character] = {}

	def add_character(self, char: Character):
		assert len(char.name) > 0
		self.characters[char.name] = char

	def __iadd__(self, other) -> "Manager":
		if isinstance(other, list):
			for char in other:
				assert isinstance(char, Character)
				self.add_character(char)
		else:
			assert isinstance(other, Character)
			self.add_character(other)
		return self

	def __iter__(self):
		for i in self.characters.values():
			yield i

	def __getitem__(self, key):
		return self.characters[key]

def dump(man: Manager):
	for c in man:
		print(c.name)
		for item, amount in c.inventory:
			print(f"\t{item}: {amount}")

manager = Manager()
manager += [
	Character("Gandolf", items={"food": 5, "grapefruit": 10, "green potions": 7, "red potions": 8, "spells of enchantment": 10}),
	Character("Frodo", items={"food": 0, "kiwi": 5, "wands of confusion": 7, "green potions": 8}),
	Character("Sauron", items={"bat wings": 5, "evil spells": 10, "fire wands": 5}),
]

def add_bilbo():
	global manager
	manager += Character("Bilbo", items={"food": 0, "kiwi": 5, "wands of confusion": 7, "green potions": 8})

if __name__ == "__main__":
	# part a: demonstrating that inventories can be modified.
	manager["Gandolf"].give_item("food", 1)
	manager["Gandolf"].take_item("grapefruit", 1)
	# part b: demonstrating that adding items and deleting them is possible.
	manager["Sauron"].give_item("grapefruit", 5)
	del manager["Sauron"].inventory["evil spells"]
	# part c: demonstrating that adding new characters with inventories is possible.
	add_bilbo()

	dump(manager)

	for char in manager:
		for item, amount in char.inventory:
			if amount == 0:
				print(f"{char.name} is all out of {item}.")
