#!/usr/bin/env python3
"""
Is it overengineered? Absolutely. Do I regret making it this complicated? Absolutely not.
"""

import locale
import functools
locale.setlocale(locale.LC_ALL, 'en_US.UTF8')

def parse_money(amount: str) -> int:
	"""Convert currency representation as a string into the amount as an integer, in cents."""
	amount = amount.replace("-$", "$-")
	parts = amount.strip("$").split(".")
	dollars = locale.atoi(parts[0])
	cents = locale.atoi(parts[1]) if len(parts) > 1 else 0
	return dollars * 100 + cents

class Currency(int):
	"""Represents currency in cents so that floating point rounding errors are not a problem."""

	def __new__(cls, value, *args, **kwargs):
		if isinstance(value, str):
			value = parse_money(value)
		return super(Currency, cls).__new__(cls, value)

	def __str__(self):
		return locale.currency(int(self) / 100)

	def __repr__(self):
		return str(self)

	def __add__(self, other):
		res = super(Currency, self).__add__(other)
		return self.__class__(res)

	def __sub__(self, other):
		res = super(Currency, self).__sub__(other)
		return self.__class__(res)

	def __mul__(self, other):
		res = super(Currency, self).__mul__(other)
		return self.__class__(res)

	def __truediv__(self, other):
		res = super(Currency, self).__truediv__(other)
		return self.__class__(res)

	def __floordiv__(self, other):
		res = super(Currency, self).__floordiv__(other)
		return self.__class__(res)

	def __mod__(self, other):
		res = super(Currency, self).__mod__(other)
		return self.__class__(res)

	def __divmod__(self, other):
		res = super(Currency, self).__divmod__(other)
		return self.__class__(res)

	def __neg__(self):
		res = super(Currency, self).__neg__()
		return self.__class__(res)

	def __pos__(self):
		res = super(Currency, self).__pos__()
		return self.__class__(res)

	def __invert__(self):
		res = super(Currency, self).__invert__()
		return self.__class__(res)

	def __abs__(self):
		res = super(Currency, self).__abs__()
		return self.__class__(res)

class Account:
	"""
	Attributes:
		holder (str): The name of the account holder.
		account_id (str): Unique identifier of the account. Also called account number.
		balance (int): Balance of the account.
	"""
	holder: str = ""
	account_id: str = ""
	balance: Currency = Currency(0)
	withdraw_limit_percent: int = 10

	count_withdraw: int = 0
	count_deposit: int = 0
	count_penalty: int = 0

	def __init__(self, holder: str, account_id: str, balance: str):
		self.holder = holder
		self.account_id = account_id
		self.balance = Currency(balance)

	def __str__(self) -> str:
		return f"Account<{self.holder} [{self.account_id}], balance: {self.balance}>"

	def __commit_transaction(self, amount: Currency, penalty: bool=False):
		"""Commit the transaction to the account."""
		if penalty:
			assert amount == -500
			self.balance += amount
			self.count_penalty += 1
			return
		self.balance += amount
		if amount > 0:
			self.count_deposit += 1
		else:
			self.count_withdraw += 1

	def withdraw(self, amount: Currency):
		if not isinstance(amount, Currency):
			amount = Currency(amount)
		if amount <= 0:
			raise TransactionException(self, amount, f"Unable to withdraw {amount}: Cannot withdraw negative or zero amount")
		if amount > self.balance // 100 * self.withdraw_limit_percent:
			raise TransactionException(self, amount, f"Unable to withdraw {amount}: Over withdraw limit", penalty=True)
		self.__commit_transaction(amount * -1)

	def deposit(self, amount: Currency):
		if amount <= 0:
			raise TransactionException(self, amount, f"Unable to deposit {amount}: Cannot deposit negative or zero amount")
		self.__commit_transaction(amount)

	def apply_penalty(self) -> Currency:
		amount = Currency("$5")
		self.__commit_transaction(-amount, penalty=True)
		return amount

class TransactionException(Exception):
	def __init__(self, account: Account, amount: Currency, message: str, penalty: bool=False):
		self.account = account
		self.amount = amount
		self.message = message
		self.penalty = penalty

def on_nephew_transaction_success(account: Account, amount: Currency):
	global accounts
	print(f"{account.holder} withdrew {amount}")
	scrooge = get_account("100001")
	for a in accounts:
		if a.account_id == account.account_id or a.account_id == scrooge.account_id:
			continue
		scrooge.withdraw(amount)
		a.deposit(amount)

def on_nephew_transaction_failure(account: Account, amount: Currency, exception=None):
	print(f"{account.holder} failed to withdraw {amount}: {exception.message}")
	if exception and exception.penalty:
		scrooge = get_account("100001")
		amount = account.apply_penalty()
		scrooge.deposit(amount)

accounts = [
	Account("Scrooge McDuck", "100001", "$1,000,000"),
	Account("Huey Duck", "700007", "$150"),
	Account("Dewey Duck", "800008", "$350"),
	Account("Louie Duck", "900009", "$25"),
]

@functools.cache
def get_account(account_id: str) -> Account:
	for account in accounts:
		if account.account_id == account_id:
			return account
	raise Exception(f"Unable to find account with id: {account_id}")

transactions:list[tuple[str, Currency]] = [
	("900009", Currency("-$2")),
	("800008", Currency("-$20")),
	("700007", Currency("-$20")),
	("900009", Currency("-$10")),
	("800008", Currency("-$20")),
	("700007", Currency("-$30")),
	("900009", Currency("-$40")),
]

def dump():
	print("┌ STATE")
	for account in accounts:
		print(f"├┬ {account}")
		print(f"│├─ withdraws={account.count_withdraw}")
		print(f"│├─ deposits={account.count_deposit}")
		print(f"│└─ penalties={account.count_penalty}")

def main():
	dump()

	for account_id, amount in transactions:
		print(f"Processing transaction: {account_id} {amount}")
		account = get_account(account_id)
		if amount < 0:
			amount *= -1
			print(f"Withdrawing {amount} from {account}")
			try:
				account.withdraw(amount)
				on_nephew_transaction_success(account, amount)
			except TransactionException as e:
				print(f"Transaction failed: {e.message}")
				on_nephew_transaction_failure(account, amount, e)
		dump()

if __name__ == "__main__":
	main()
