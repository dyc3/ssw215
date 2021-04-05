def word_count():
	with open("alice.txt", "r") as f:
		count = sum([len(line.split()) for line in f.readlines()])
	print(f"The file alice.txt has about {count} words")
	return count

if __name__ == "__main__":
	word_count()
