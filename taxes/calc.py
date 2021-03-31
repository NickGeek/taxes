#!/usr/bin/python3
import sys
import csv
from money.money import Money
from money.currency import Currency
import argparse

def compute_taxes(transactions, is_verbose):
	microsync_income = Money(0, Currency.NZD)
	taxii_income = Money(0, Currency.NZD)
	digitalocean_costs = Money(0, Currency.NZD)
	aws_costs = Money(0, Currency.NZD)

	for transaction in transactions:
		if transaction['Memo'] == None:
			continue

		# MicroSync payment
		if transaction['Payee'] == 'D/C FROM Stripe Payments':
			microsync_income += transaction['Amount']
		elif 'DIGITALOCEAN' in transaction['Memo']:
			digitalocean_costs += (transaction['Amount'] * -1)
		elif 'D/C FROM Google Payment' in transaction['Payee']:
			taxii_income += transaction['Amount']
		elif 'AMAZON MKTPL ACE PMTS AMAZON.COM' in transaction['Memo']:
			aws_costs += (transaction['Amount'] * -1)

	income = microsync_income + taxii_income
	deductions = digitalocean_costs + aws_costs

	if is_verbose:
		print(f'MicroSync Income: {microsync_income.format("en_NZ")}')
		print(f'Taxii Income: {taxii_income.format("en_NZ")}')
		print(f'DigitalOcean Costs: {digitalocean_costs.format("en_NZ")}')
		print(f'AWS Costs: {aws_costs.format("en_NZ")}')
		print('---------------------------------------')

	return income, deductions

def read_bank_statement(csv_file_path, transactions):
	with open(csv_file_path) as csv_file:
		rows = csv.reader(csv_file, delimiter=',', quotechar='"')
		
		# Clear out the header
		keys = []
		for row in rows:
			if len(row) == 0: break
			keys = row

		# Collect a list of little transaction objects
		for row in rows:
			transaction = dict.fromkeys(keys)
			for i, cell in enumerate(row):
				key = keys[i]
				if key == 'Amount':
					cell = Money(cell, Currency.NZD)

				transaction[key] = cell if len(str(cell)) > 0 else None

			transactions.append(transaction)

if __name__ == '__main__':
	# Get args
	args = argparse.ArgumentParser(description='Calculate my tax return')
	args.add_argument('csv_file_path', nargs='+')
	args.add_argument('-v', '--verbose', action='store_true')
	args = args.parse_args()

	# Do taxes
	transactions = []
	for csv_file_path in args.csv_file_path:
		if args.verbose:
			print(f'Calculating taxes from bank statement: {csv_file_path}')
		read_bank_statement(csv_file_path, transactions)

	# Tell me the damage
	income, deductions = compute_taxes(transactions, args.verbose)

	print(f'Total: {(income - deductions).format("en_NZ")}')
	if args.verbose:
		print(f'Income: {income.format("en_NZ")}')
		print(f'Deductions: {deductions.format("en_NZ")}')
