import pandas as pd
import numpy as np


user_balance_csv = 'data/user_balance.csv'
contracts_csv = 'data/contracts.csv'
wagers_csv = 'data/wagers.csv'

# Returns the user's balance, and (None, None) if the user is not in the table
def return_balance(user):
	global user_balance_csv

	balance_table = np.array(pd.read_csv(user_balance_csv))[:, [1, 2]]

	for i in range(balance_table.shape[0]):
		if balance_table[i][0] == user:
			return (user, balance_table[i][1])

	return (None, None)


# Updates the balance for user_name, returns 0 if the user wasn't in the table, -1 if quit due to negative balance, 1 on normal
def change_balance(user_name, delta_balance):
	(user, balance) = return_balance(user_name)
	assert(user == user_name or user is None)

	return_val = None

	new_balance = 0
	if user is None:
		new_balance = delta_balance
		return_val = 0
	else:
		new_balance = balance + delta_balance
		return_val = 1

	if new_balance < 0:
		# TODO proper exception handling
		return -1

	write_balance(user_name, new_balance)

	print(f'Changed balance of {user_name} by {delta_balance}')

	return (return_val, user_name, balance, new_balance)


# Writes in the user's new balance. Returns 0 if the user was already in the table, and 1 if not
def write_balance(user, new_balance):
	global user_balance_csv

	balance_table = np.array(pd.read_csv(user_balance_csv))[:, [1, 2]]

	user_found = False
	for i in range(balance_table.shape[0]):
		if balance_table[i][0] == user:
			balance_table[i][1] = new_balance
			user_found = True
			break

	if not user_found:
		to_append = np.array([[user, new_balance]])
		balance_table = np.append(balance_table, to_append, axis = 0)

	pd.DataFrame(balance_table).to_csv(user_balance_csv)

	return 0 if user_found else 1

# TODO Drops the user's row in the balance table
def delete_balance(user):
	return

# Contract columns:
# [unique_id, contract_owner, contract_contents, outcome_A, outcome_B, outcome_C, outcome_D, outcome_E, active (0 for open, 1 for closed, A-E for resolved, F for cancelled)]

# Writes contract into csv, returns 0 on success
def create_contract(owner, contract_contents, contract_outcomes):
	global contracts_csv

	contracts_table = np.array(pd.read_csv(contracts_csv))[:, 1:]

	contract_id = contracts_table.shape[0]

	to_append = np.array([[
		contract_id,
		owner,
		contract_contents,
		contract_outcomes[0],
		contract_outcomes[1],
		contract_outcomes[2],
		contract_outcomes[3],
		contract_outcomes[4],
		0
		]])

	contracts_table = np.append(contracts_table, to_append, axis = 0)

	pd.DataFrame(contracts_table).to_csv(contracts_csv)

	return contract_id


# Gets and returns a contract
def get_contract(contract_id):
	global contracts_csv

	contracts_table = np.array(pd.read_csv(contracts_csv))[:, 1:]

	for i in range(contracts_table.shape[0]):
		if str(contracts_table[i][0]) == contract_id:
			return contracts_table[i]

	return None

# Closes contract with specified closing reason
def close_contract(contract_id, reason):

	#TODO proper exception handling
	assert(reason == '1' or reason == 'A' or reason == 'B' or reason == 'C' or reason == 'D' or reason == 'E' or reason == 'F')

	global contracts_csv

	contracts_table = np.array(pd.read_csv(contracts_csv))[:, 1:]

	for i in range(contracts_table.shape[0]):
		if str(contracts_table[i][0]) == contract_id:
			contracts_table[i][8] = reason

	pd.DataFrame(contracts_table).to_csv(contracts_csv)

	return 0

# Returns the full contract table
def list_contracts():
	global contracts_csv

	contracts_table = np.array(pd.read_csv(contracts_csv))[:, 1:]
	return contracts_table

# Wagers columns:
# [wager_id, wager_owner, contract_unique_id, contract_outcome, amount, active (0 for open, -1 for lost, 1 for won/cancelled)]
def create_wager(owner, contract, outcome, amount):
	global wagers_csv

	wagers_table = np.array(pd.read_csv(wagers_csv))[:, 1:]

	to_append = np.array([[
		wagers_table.shape[0],
		owner,
		contract,
		outcome,
		amount,
		0
		]])

	wagers_table = np.append(wagers_table, to_append, axis = 0)


	pd.DataFrame(wagers_table).to_csv(wagers_csv)

	return 0

# Changes the result of the specified wager WITHOUT giving the money back
def resolve_wager(wager_id, result): #TODO: make this take a list of ids and results so we don't have to read/write as many times
	global wagers_csv

	wagers_table = np.array(pd.read_csv(wagers_csv))[:, 1:]

	for i in range(wagers_table.shape[0]):
		if wagers_table[i][0] == wager_id:
			wagers_table[i][5] = result
			break

	pd.DataFrame(wagers_table).to_csv(wagers_csv)

	return 0

# Returns np array of all wagers
def list_wagers():
	global wagers_csv

	wagers_table = np.array(pd.read_csv(wagers_csv))[:, 1:]

	return wagers_table


# Returns an np array of all wagers for this contract
def list_relevant_wagers(contract_id):
	wagers_table = list_wagers()

	output_table = np.empty((0, wagers_table.shape[1]))

	for wager in wagers_table:
		if str(wager[2]) == contract_id:
			output_table = np.append(output_table, [wager], axis = 0)

	return output_table











