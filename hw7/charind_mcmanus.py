def char_index():
	text = "Mango banana apple pear Banana grapes strawberry Apple pear mango banana Kiwi apple mango strawberry"
	idxs = [i for i, c in enumerate(text) if c == "r"]
	print("This index values of each occurrences of character ‘r’ in the string are", idxs)
	return idxs

if __name__ == "__main__":
	char_index()
