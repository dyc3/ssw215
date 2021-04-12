def word_order(words: str):
	result = sorted(set(words.split(",")))
	print(",".join(result))
	return result

# assert word_order("apple,mango,carrot,apple,orange,mango,berry") == ["apple", "berry", "carrot", "mango", "orange"]

if __name__ == "__main__":
	word_order("apple,mango,carrot,apple,orange,mango,berry")
