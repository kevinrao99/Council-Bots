# bot.py
import discord

import math
import random
import re
import numpy as np

import csv_io

from discord.ext import commands


intents = discord.Intents(messages=True, members=True)

bot = commands.Bot(command_prefix='-', intents = intents)
bot.remove_command('help')


outcomes_emojis = [':regional_indicator_a:', ':regional_indicator_b:', ':regional_indicator_c:', ':regional_indicator_d:', ':regional_indicator_e:']
outcomes_list = ['A', 'B', 'C', 'D', 'E']

@bot.event
async def on_ready():
    print("I am running on " + bot.user.name)
    print("With the ID: " + str(bot.user.id))
    print('Bot is ready to be used')
   # after it is ready do it

    takenGuild = bot.get_guild(831331716223729685)
    print(takenGuild.id)

    for guild in bot.guilds:
        print('guild: ' + str(guild))
        print(guild.id)


@bot.command(name = 'help')
async def help_menu(ctx):
	embed=discord.Embed(title="Basic Commands", description="Basic commands for gambling with your Planet Tokens (PT)\n", color=0xff0000)

	embed.add_field(name="-help", value="Displays this help menu!", inline=False)
	embed.add_field(name="-balance", value="Returns your balance", inline=False)
	embed.add_field(name="-list", value="Lists all active contracts", inline=False)
	embed.add_field(name="-view [contract id]", value="Views the specified contract in more detail\ne.g. \"-view 13\" views contract 13", inline=False)
	embed.add_field(name="-wager [contract id] [outcome] [amount]", value="Places a wager on the specified contract and outcome (this cannot be undone!)\ne.g. \"-wager 13 A 100\" places a wager of 100 PT on outcome :regional_indicator_a: of contract 13", inline=False)
	embed.add_field(name="-my_wagers", value="Lists your active wagers", inline=False)
	embed.add_field(name="-help_contract", value="Displays this help menu for creating and managing your own contracts", inline=False)

	await ctx.send(embed=embed)


@bot.command(name = 'help_contract')
async def help_menu_contract(ctx):
	embed=discord.Embed(title="Contract Commands", description="Commands for creating and managing your own contracts\n", color=0xff0000)

	embed.add_field(name="-open [topic] [outcome A; outcome B; outcome C; outcome D; outcome E]", value="Creates a new contract with at most 5 possible outcomes\ne.g. \"-open [First to die on Sire Heroic?] [Spikes; Not Spikes]\" ", inline=False)
	embed.add_field(name="-close [contract id]", value="Closes the specified contract from taking more wagers\ne.g. \"-closes 13\" closes contract 13", inline=False)
	embed.add_field(name="-cancel [contract_id]", value="Cancels the specified contract and refunds all wagers\ne.g. \"-cancel 13\" cancels contract 13", inline=False)
	embed.add_field(name="-resolve [contract_id] [outcome]", value="Resolves the contract with the specified outcome, calculating and sending winnings\ne.g. \"-resolve 13 A\" declares that outcome A won contract 13", inline=False)

	await ctx.send(embed=embed)


@bot.command(name = 'balance', help = 'Returns the caller\'s balance')
async def get_balance(ctx):
	(user, balance) = csv_io.return_balance(ctx.author.name)

	#TODO change to displaying server nickname


	if user is None:
		await ctx.send(f'User {ctx.author.name} is not in the balance sheet')
		#TODO proper exception handling

	await ctx.send(f'{user}\'s balance is {balance}')
	#TODO format output to be truncated to correct number of decimal points


@bot.command(name = 'list', help = 'Lists all active contracts')
async def list_contracts(ctx):
	global outcomes_list

	embed=discord.Embed(title="Active Contracts", description="All unresolved (both open and closed) contracts", color=0xff0000)

	contract_list = csv_io.list_contracts()
	for contract in contract_list:
		if not (str(contract[8]) == '0' or str(contract[8]) == '1'):
			continue

		relevant_wagers = csv_io.list_relevant_wagers(str(contract[0]))
		
		embed.add_field(name = "Contract ID: " + str(contract[0]), value = 'opened by ' + contract[1] + ('' if str(contract[8]) == '0' else '\n(now closed)'), inline = True)

		outcome_field_value = ''
		outcome_stake_value = ''

		for j in range(3, 8): #TODO display each outcome's total as well (possibly in markdown)
			if type(contract[j]) == type(1.5) and math.isnan(contract[j]):
				break

			tot_wagers = 0
			for wager in relevant_wagers:
				if wager[3] == outcomes_list[j - 3]:
					tot_wagers += wager[4]

			outcome_field_value = outcome_field_value + outcomes_emojis[j - 3] + ': ' + contract[j] + '\n'
			outcome_stake_value = outcome_stake_value + outcomes_emojis[j - 3] + ' current stake: '+ str(tot_wagers) + ' PT\n'

		embed.add_field(name = contract[2], value = outcome_field_value, inline = True)
		embed.add_field(name = 'Outcome Pools', value = outcome_stake_value, inline = True)
		embed.add_field(name = '-', value = '-', inline = False)


	await ctx.send(embed=embed)


@bot.command(name = 'view', help = 'Views the details of the given contract')
async def view_contract(ctx, contract_id):
	global outcomes_list
	
	specified_contract = csv_io.get_contract(contract_id)
	if specified_contract is None:
		#TODO proper exception handling
		await ctx.send(f'Could not find a contract with ID {contract_id}')
		return

	relevant_wagers = csv_io.list_relevant_wagers(contract_id)
	print(contract_id)
	print(relevant_wagers)

	output_str = '```Contract ID: ' + str(specified_contract[0]) + ', opened by ' + specified_contract[1] + ':\n' + specified_contract[2] + '\n'
	for i in range(3, 8):
		cur = outcomes_list[i - 3]

		if type(specified_contract[i]) == type(1.5) and math.isnan(specified_contract[i]):
			break
		output_str = output_str + '   Outcome ' + outcomes_emojis[i - 3] + ': ' + specified_contract[i] + '\n'

		
		cur_wagers = []
		for wager in relevant_wagers:
			if wager[3] == cur:
				cur_wagers.append((wager[1], wager[4]))

		sorted_wagers = sorted(cur_wagers, key=lambda wager: -1 * wager[1])
		for wager in sorted_wagers:
			output_str = output_str + '      ' + wager[0] + '  bet ' + str(wager[1]) + '\n'

		#TODO markdown for better formatting

	if not (str(specified_contract[8]) == '0'):
		if specified_contract[8] == 'F':
			output_str = output_str + 'NOTE: this contract has been cancelled'
		else:
			output_str = output_str + 'NOTE: this contract has been resolved with outcome ' + str(specified_contract[8])

	output_str = output_str + "```"
	await ctx.send(output_str)


@bot.command(name = 'wager', help = '-wager contract_id outcome amount places a wager of the specified amount on the contract\'s specified outcome e.g. -wager 13 A 100')
async def place_wager(ctx, contract_id, outcome, amount):

	specified_contract = csv_io.get_contract(contract_id)
	if specified_contract is None:
		#TODO proper exception handling
		await ctx.send(f'Could not find a contract with ID \"{contract_id}\"')
		return
	if str(specified_contract[8]) == '1':
		await ctx.send(f'The contract {contract_id} has been closed and is no longer taking wagers')
		return
	elif not (str(specified_contract[8]) == '0'):
		#TODO proper exception handling
		await ctx.send(f'The contract {contract_id} is no longer active')
		return

	if len(re.findall(r"[ABCDE]", outcome)) != 1:
		#TODO proper exception handling
		await ctx.send('The outcome must be exactly one of (uppercase) A, B, C, D, or E') #TODO allow uppercase
		return

	#TODO confirm the outcome for the wager is not nan


	try:
		int(amount)
	except ValueError:
		#TODO proper exception handling
		await ctx.send('The amount must be a positive integer number of Planet Tokens')
		return

	if int(amount) < 1:
		await ctx.send('The amount must be a positive integer number of Planet Tokens')
		return

	(_, player_balance) = csv_io.return_balance(ctx.author.name)
	if player_balance < int(amount):
		#TODO proper exception handling
		await ctx.send(f'{ctx.author.name}\'s balance is {player_balance} PT and is not enough for a wager of {amount} PT')
		return

	csv_io.create_wager(ctx.author.name, contract_id, outcome, amount)
	csv_io.change_balance(ctx.author.name, -1 * int(amount))
	await ctx.send(f'Created a wager for {ctx.author.name} on contract {contract_id}, outcome {outcome.upper()} for {amount} Planet Tokens')


@bot.command(name = 'my_wagers', help = 'Lists your wagers')
async def my_wagers(ctx):

	wagers = csv_io.list_wagers()

	output_list = []

	for wager in wagers:
		if wager[1] == ctx.author.name and wager[5] == 0:
			output_list.append((wager[2], wager[3], wager[4]))

	output_str = ''
	for (contract_id, outcome, amount) in output_list:
		output_str = output_str + str(amount) + ' on contract ' + str(contract_id) + ' to have outcome ' + outcome + '\n'

	await ctx.send(output_str)


@bot.command(name = 'open', help = '-open_contract [Contents] [outcome 1; outcome 2; dots] creates a new contract')
async def open_contract(ctx, *args): #TODO have this make an announcement in a non bot commands channel
	input_string = ' '.join(args)
	split_input = re.split(r"[\[\];]+", input_string) #TODO add warning not to use brackets or semicolons in the thingies?

	contract_contents = split_input[1]
	contract_outcomes = []
	for i in range(3, len(split_input)):
		if split_input[i] == '':
			break
		contract_outcomes.append(split_input[i])
	for i in range(len(contract_outcomes), 5):
		contract_outcomes.append('')

	#TODO proper exception handling
	if len(contract_outcomes) <= 1:
		await ctx.send('Error: contract needs at least two outcomes')
		return
	elif len(contract_outcomes) > 5:
		await ctx.send('Error: contract can have at most five outcomes')
		return

	create_result = csv_io.create_contract(ctx.author.name, contract_contents, contract_outcomes)

	await ctx.send(f'Successfully opened the contract [{contract_contents}] with id {create_result} and outcomes:')

	
	for i in range(len(contract_outcomes)):
		if contract_outcomes[i] == '':
			break
		await ctx.send(f'{outcomes_emojis[i]}:   {contract_outcomes[i]}')


@bot.command(name = 'close', help = 'Closes the contract from more wagers')
async def close_contract(ctx, contract_id):
	#TODO send announcement that contract has been closed

	contract = csv_io.get_contract(contract_id)
	if contract is None:
		#TODO proper exception handling
		await ctx.send(f'could not find a contract with ID \"{contract_id}\"')
		return

	if not (ctx.author.name == 'pieslinger' or ctx.author.name == contract[1]):
		#TODO proper exception handling
		await ctx.send(f'You do not have permission to close a contract opened by {contract[1]}')
		return

	csv_io.close_contract(contract_id, '1')

	await ctx.send(f'Closed contract {contract_id}')


@bot.command(name = 'cancel', help = 'Cancels the contract, returning all bets')
async def cancel_contract(ctx, contract_id):
	#TODO send announcement that contract has been cancelled and all bets refunded

	contract = csv_io.get_contract(contract_id)

	if contract is None:
		#TODO proper exception handling
		await ctx.send(f'Could not find a contract with ID \"{contract_id}\"')
		return
	if not (str(contract[8]) == '0'):
		#TODO proper exception handling
		await ctx.send(f'The contract {contract_id} is already inactive')
		return

	if not (ctx.author.name == 'pieslinger' or ctx.author.name == contract[1]):
		#TODO proper exception handling
		await ctx.send(f'You do not have permission to cancel a contract opened by {contract[1]}')
		return

	relevant_wagers = csv_io.list_relevant_wagers(contract_id)
	for wager in relevant_wagers:
		csv_io.resolve_wager(wager[0], 1) #TODO send private message
		csv_io.change_balance(wager[1], wager[4])

	csv_io.close_contract(contract_id, 'F')

	await ctx.send(f'Successfully cancelled contract {contract_id}')


@bot.command(name = 'resolve', help = 'Resolves the contract, sending Planet Tokens to the winners')
async def resolve_contract(ctx, contract_id, outcome):
	#TODO have resolve send an announcement in a non bot commands channel

	assert(outcome == 'A' or outcome == 'B' or outcome == 'C' or outcome == 'D' or outcome == 'E')
	#TODO confirm that the resolved outcome is not nan

	contract = csv_io.get_contract(contract_id)

	if contract is None:
		#TODO proper exception handling
		await ctx.send(f'Could not find a contract with ID \"{contract_id}\"')
		return
	if not (str(contract[8]) == '0'):
		#TODO proper exception handling
		await ctx.send(f'The contract {contract_id} is already inactive')
		return

	if not (ctx.author.name == 'pieslinger' or ctx.author.name == contract[1]):
		#TODO proper exception handling
		await ctx.send(f'You do not have permission to resolve a contract opened by {contract[1]}')
		return

	relevant_wagers = csv_io.list_relevant_wagers(contract_id)
	
	#First determine winnings multiplier
	tot_wagers = 0
	tot_winning = 0
	for wager in relevant_wagers:
		tot_wagers += wager[4]
		if wager[3] == outcome:
			tot_winning += wager[4]

	if tot_winning > 0:
		winning_ratio = tot_wagers / tot_winning
	else:
		winning_ratio = -1
	print(f'winning ratio for {contract_id} is {winning_ratio}')
	#TODO figure out how to profit here

	for wager in relevant_wagers:
		if wager[3] == outcome:
			csv_io.resolve_wager(wager[0], 1)
			csv_io.change_balance(wager[1], wager[4] * winning_ratio) #TODO send notif in private messages
		else:
			csv_io.resolve_wager(wager[0], -1)

	csv_io.close_contract(contract_id, outcome)

	await ctx.send(f'Successfully resolved contract {contract_id} with outcome {outcome} winning')



#Admin commands

@bot.command(name = 'change_balance', help = 'Changes the user\'s balance')
async def change_balance(ctx, user_name, delta_balance : int):
	#TODO handle exception for passing in float instead of int

	if not (ctx.author.name == 'pieslinger'):
		#TODO proper exception handling
		await ctx.send(f'You do not have permission to change a user\'s balance')
		return

	(change_result, user, old_balance, new_balance) = csv_io.change_balance(user_name, delta_balance)

	#TODO change to displaying server nickname

	if change_result == -1:
		await ctx.send(f'Error: this command would result in negative balance for {user_name} so their balance was not updated')
	elif change_result == 0:
		await ctx.send(f'{user} has been added to the table and balance set to {new_balance}')
		#TODO send welcome message in DMs
	elif change_result == 1:
		await ctx.send(f'{user}\'s balance has been updated from {old_balance} to {new_balance}')
	else:
		await ctx.send('Shouldn\'t be here in bot change_balance!')
		#TODO ??

	#TODO format output to be truncated to correct number of decimal points


@bot.command()
async def test(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, name='general')
    if channel is None:
        await ctx.send("Error")
    else:
        await channel.send("Testing")
    #count_members = len(ctx.guild.members)
    #for members in ctx.guild.members:
        #await ctx.send(members)

#TODO admin commands like announcements etc

if __name__ == '__main__':
	print('In main')

	bot.run('ODMxMzIxODg5NTk0NTQwMDQz.YHTi1w.jm9N4CySvF-0Gndgs1n-sNgyhTU')


















