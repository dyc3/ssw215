import unittest
from bank import Currency

class TestCurrency(unittest.TestCase):
	def test_operations(self):
		c = Currency(0)
		self.assertEqual(c, 0)
		c = c + 5
		self.assertEqual(c, 5)
		c = c - 3
		self.assertEqual(c, 2)
		c = c * 3
		self.assertEqual(c, 6)
		c = c / 2
		self.assertEqual(c, 3)

		c = Currency(0)
		self.assertEqual(c, 0)
		c += 5
		self.assertEqual(c, 5)
		c -= 3
		self.assertEqual(c, 2)
		c *= 3
		self.assertEqual(c, 6)
		c /= 2
		self.assertEqual(c, 3)

	def test_operations2(self):
		c = Currency(10)
		# self.assertEqual(-c, -10)
		# self.assertIsInstance(-c, Currency)
		c *= -1
		self.assertEqual(c, -10)

	def test_parse(self):
		self.assertEqual(Currency("$2"), 200)
		self.assertEqual(Currency("-$2"), -200)
		self.assertEqual(Currency("$2.56"), 256)

if __name__ == "__main__":
	unittest.main()
