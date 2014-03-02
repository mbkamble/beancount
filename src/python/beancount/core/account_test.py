import unittest
import re

from beancount.core.account import *


class TestAccount(unittest.TestCase):

    def test_ctor(self):
        account = Account("Expenses:Toys:Computer", 'Expenses')
        self.assertEqual("Expenses:Toys:Computer", account.name)
        self.assertEqual("Expenses", account.type)

    def test_account_from_name(self):
        account = account_from_name("Expenses:Toys:Computer")
        self.assertEqual("Expenses:Toys:Computer", account.name)
        self.assertEqual("Expenses", account.type)

    def test_account_name_parent(self):
        self.assertEqual("Expenses:Toys", account_name_parent("Expenses:Toys:Computer"))
        self.assertEqual("Expenses", account_name_parent("Expenses:Toys"))
        self.assertEqual("", account_name_parent("Expenses"))
        self.assertEqual(None, account_name_parent(""))

    def test_account_name_leaf(self):
        self.assertEqual("Computer", account_name_leaf("Expenses:Toys:Computer"))
        self.assertEqual("Toys", account_name_leaf("Expenses:Toys"))
        self.assertEqual("Expenses", account_name_leaf("Expenses"))
        self.assertEqual(None, account_name_leaf(""))

    def test_account_sortkey(self):
        account_names_input = [
            "Expenses:Toys:Computer",
            "Income:US:Intel",
            "Income:US:ETrade:Dividends",
            "Equity:OpeningBalances",
            "Liabilities:US:RBS:MortgageLoan",
            "Equity:NetIncome",
            "Assets:US:RBS:Savings",
            "Assets:US:RBS:Checking"
        ]
        account_names_expected = [
            "Assets:US:RBS:Checking",
            "Assets:US:RBS:Savings",
            "Liabilities:US:RBS:MortgageLoan",
            "Equity:NetIncome",
            "Equity:OpeningBalances",
            "Income:US:ETrade:Dividends",
            "Income:US:Intel",
            "Expenses:Toys:Computer",
        ]

        # Test account_name_sortkey.
        account_names_actual = sorted(account_names_input,
                                      key=account_name_sortkey)
        self.assertEqual(account_names_expected, account_names_actual)

        # Test account_sortkey.
        accounts_input = map(account_from_name, account_names_input)
        accounts_actual = sorted(accounts_input,
                                 key=account_sortkey)
        self.assertEqual(account_names_expected,
                         [account.name for account in accounts_actual])
        accounts_expected = list(map(account_from_name, account_names_expected))
        self.assertEqual(accounts_expected, accounts_actual)

    def test_account_name_type(self):
        self.assertEqual("Assets", account_name_type("Assets:US:RBS:Checking"))
        self.assertEqual("Assets", account_name_type("Assets:US:RBS:Savings"))
        self.assertEqual("Liabilities", account_name_type("Liabilities:US:RBS:MortgageLoan"))
        self.assertEqual("Equity", account_name_type("Equity:NetIncome"))
        self.assertEqual("Equity", account_name_type("Equity:OpeningBalances"))
        self.assertEqual("Income", account_name_type("Income:US:ETrade:Dividends"))
        self.assertEqual("Income", account_name_type("Income:US:Intel"))
        self.assertEqual("Expenses", account_name_type("Expenses:Toys:Computer"))
        with self.assertRaises(AssertionError):
            account_name_type("Invalid:Toys:Computer")

    def test_is_account_name(self):
        self.assertTrue(is_account_name("Assets:US:RBS:Checking"))
        self.assertTrue(is_account_name("Equity:OpeningBalances"))
        self.assertTrue(is_account_name("Income:US:ETrade:Dividends-USD"))
        self.assertTrue(is_account_name("Assets:US:RBS"))
        self.assertTrue(is_account_name("Assets:US"))
        self.assertFalse(is_account_name("Assets"))
        self.assertFalse(is_account_name("Invalid"))
        self.assertFalse(is_account_name("Other"))
        self.assertFalse(is_account_name("Assets:US:RBS*Checking"))
        self.assertFalse(is_account_name("Assets:US:RBS:Checking&"))
        self.assertFalse(is_account_name("Assets:US:RBS:checking"))
        self.assertFalse(is_account_name("Assets:us:RBS:checking"))

    def test_is_account_name_root(self):
        for account_name, expected in [
                ("Assets:US:RBS:Checking", False),
                ("Equity:OpeningBalances", False),
                ("Income:US:ETrade:Dividends-USD", False),
                ("Assets", True),
                ("Liabilities", True),
                ("Equity", True),
                ("Income", True),
                ("Expenses", True),
                ("Invalid", False),
                ]:
            self.assertEqual(expected, is_account_name_root(account_name), account_name)

    OPTIONS = {'name_assets'      : 'Assets',
               'name_liabilities' : 'Liabilities',
               'name_equity'      : 'Equity',
               'name_income'      : 'Income',
               'name_expenses'    : 'Expenses'}

    def test_is_account_categories(self):
        for account_name, expected in [
                ("Assets:US:RBS:Savings", True),
                ("Liabilities:US:RBS:MortgageLoan", True),
                ("Equity:OpeningBalances", True),
                ("Income:US:ETrade:Dividends", False),
                ("Expenses:Toys:Computer", False),
                ]:
            self.assertEqual(expected,
                             is_balance_sheet_account(account_name, self.OPTIONS))

            self.assertEqual(not expected,
                             is_income_statement_account(account_name, self.OPTIONS))

    def test_accountify_dict(self):
        accvalue_dict = {"b6edc1bf714a": "Assets:US:RBS:Savings",
                         "21a4647fe535": "Liabilities:US:RBS:MortgageLoan",
                         "6d17539d6c32": "Equity:OpeningBalances",
                         "421833fa2cb9": "Income:US:Intel",
                         "391bb475127e": "Expenses:Toys:Computer"}
        newdict = accountify_dict(accvalue_dict)
        self.assertTrue(isinstance(newdict, dict))
        self.assertEqual("Income:US:Intel", newdict["421833fa2cb9"].name)


__incomplete__ = True  ## You need to update the tests for new changes in account.py
