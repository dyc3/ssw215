inventories = {
	"Gandolf": {"food": 5, "grapefruit": 10, "green potions": 7, "red potions": 8, "spells of enchantment": 10},
	"Frodo": {"food": 0, "kiwi": 5, "wands of confusion": 7, "green potions": 8},
	"Sauron": {"bat wings": 5, "evil spells": 10, "fire wands": 5}
}

def add_bilbo():
	global inventories
	inventories["Bilbo"] = {"food": 0, "kiwi": 5, "wands of confusion": 7, "green potions": 8}

if __name__ == "__main__":
	# part a: demonstrating that inventories can be modified.
	inventories["Gandolf"]["food"] += 1
	inventories["Gandolf"]["grapefruit"] -= 1
	# part b: demonstrating that adding items and deleting them is possible.
	inventories["Sauron"]["grapefruit"] = 5
	del inventories["Sauron"]["evil spells"]
	# part c: demonstrating that adding new characters with inventories is possible.
	add_bilbo()

	print(inventories)
	for name, inventory in inventories.items():
		for item, amount in inventory.items():
			if amount == 0:
				print(f"{name} is all out of {item}.")
