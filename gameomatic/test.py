import unittest
import random

class TestRNG(unittest.TestCase):
	def test_random_is_uniform(self):
		random.seed(93185723)
		nums = [random.randint(1, 12) for _ in range(10000)]
		percentages = {x: nums.count(x)/10000 for x in range(1, 13)}
		for i in percentages.values():
			for j in percentages.values():
				self.assertAlmostEqual(i, j, delta=0.00681)
		self.assertAlmostEqual(sum(percentages.values()), 1, places=10) # accounting for floating point rounding errors

if __name__ == "__main__":
	unittest.main()
