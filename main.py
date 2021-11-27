from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from datetime import datetime, timedelta
from quests import quests

import secrets
import weapon_tinkering
import pymysql

# Connect to ACE Databases
accounts_db = pymysql.connect(host=secrets.db_uri,
                              port=secrets.db_port,
                              user=secrets.db_user,
                              password=secrets.db_pwd,
                              database='ace_auth',
                              cursorclass=pymysql.cursors.DictCursor)

characters_db = pymysql.connect(host=secrets.db_uri,
                                port=secrets.db_port,
                                user=secrets.db_user,
                                password=secrets.db_pwd,
                                database='ace_shard',
                                cursorclass=pymysql.cursors.DictCursor)

# Connect to Discord
client = Client(intents=Intents.all())
slash = SlashCommand(client, sync_commands=True)
servers = secrets.servers

# Register Slash Commands
quest_choices = []

for key in quests:
    quest_choices.append(create_choice(name=quests[key][0], value=key))


@slash.slash(name="timer",
             description="Check a quest timer for toons on the specified account.",
             options=[
                 create_option(
                     name='account',
                     description='The username for your ACE account.',
                     option_type=3,
                     required=True
                 ),
                 create_option(
                     name='quest',
                     description='The shorthand text for the quest (e.g. "bellas").',
                     option_type=3,
                     required=True,
                     choices=quest_choices
                 )
             ],
             guild_ids=servers)
async def timer(ctx: SlashContext, account: str, quest: str):
    await ctx.author.send(f'Looking up quest timer for {quests[quest][0]} for toons on account {account}:')

    with accounts_db:
        with accounts_db.cursor() as cursor:
            sql = 'SELECT `accountId` FROM `account` WHERE `accountName`=%s'
            cursor.execute(sql, (account.lower().strip(),))
            result_account_id = cursor.fetchone()

            if result_account_id is not None:
                account_id = result_account_id['accountId']

                with characters_db:
                    with characters_db.cursor() as cursor2:
                        sql = f'SELECT `id`, `name` FROM `character` WHERE `account_Id`={account_id}'
                        cursor2.execute(sql)
                        result_characters = cursor2.fetchall()

                        if len(result_characters) < 1:
                            await ctx.author.send(f'Account {account} has no characters.')
                        else:
                            for character in result_characters:
                                character_id = character['id']
                                character_name = character['name']
                                sql = f'SELECT `last_Time_Completed` FROM `character_properties_quest_registry` WHERE `character_Id`={character_id} AND `quest_Name`="{quest}"'
                                cursor2.execute(sql)
                                result_timer = cursor2.fetchone()

                                if result_timer is not None:
                                    quest_timer = datetime.fromtimestamp(result_timer['last_Time_Completed'])
                                    is_timer_up = quest_timer.today() - quest_timer > timedelta(quests[quest][1])
                                    # TODO are we at the 27 day maximum of 4 for Stipends?
                                    await ctx.author.send(
                                        f'- {character_name} {quest_timer} {":green_circle:" if is_timer_up else ":red_square:"}')
                                else:
                                    await ctx.author.send(f'- {character_name} N/A')
            else:
                await ctx.author.send(f'Account {account} not found on this ACE server.')


@slash.slash(name="rent",
             description="Check rent for the housing on the specified account.",
             options=[
                 create_option(
                     name='account',
                     description='The username for your ACE account.',
                     option_type=3,
                     required=True
                 )
             ],
             guild_ids=servers)
async def rent(ctx: SlashContext, account: str):
    with accounts_db:
        with accounts_db.cursor() as cursor:
            sql = 'SELECT `accountId` FROM `account` WHERE `accountName`=%s'
            cursor.execute(sql, (account.lower().strip(),))
            result_account_id = cursor.fetchone()

            if result_account_id is not None:
                account_id = result_account_id['accountId']

                with characters_db:
                    with characters_db.cursor() as cursor2:
                        sql = f'SELECT `id` FROM `character` WHERE `account_Id`={account_id}'
                        cursor2.execute(sql)
                        result_character = cursor2.fetchone()

                        if result_character is None:
                            await ctx.author.send(f'Account {account} has no characters.')
                        else:
                            character_id = result_character['id']
                            sql = f'SELECT `value` FROM `biota_properties_int` WHERE `object_Id`={character_id} AND `type`=9011'
                            cursor2.execute(sql)
                            result_timer = cursor2.fetchone()

                            if result_timer is not None:
                                rent_timer = datetime.fromtimestamp(result_timer['value']).strftime('%B %d %Y %H:%M')
                                await ctx.author.send(f'Your rent is due: {rent_timer}')
                            else:
                                await ctx.author.send(f'Account {account} does not appear to have a rental property.')
            else:
                await ctx.author.send(f'Account {account} not found on this ACE server.')


@slash.slash(name="ig",
             description="Calculate best 9 iron/granite tinks on a rend weapon, assuming BD 8 and basic augs.",
             options=[
                 create_option(
                     name='min',
                     description='The unbuffed minimum damage on the weapon.',
                     option_type=10,
                     required=True
                 ),
                 create_option(
                     name='max',
                     description='The unbuffed maximum damage on the weapon.',
                     option_type=10,
                     required=True
                 ),
                 create_option(
                     name='cantrip',
                     description='The Blood Thirst cantrip on the weapon.',
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name='None', value=0),
                         create_choice(name='Minor', value=2),
                         create_choice(name='Major', value=4),
                         create_choice(name='Epic', value=7),
                         create_choice(name='Legendary', value=10),
                     ]
                 )
             ],
             guild_ids=servers)
async def ig(ctx: SlashContext, min: float, max: float, cantrip: int):
    # await ctx.send(f'For this weapon, the starting average damage is {weapon_tinkering.starting_average_damage(min, max, 24.0, float(cantrip))} and starting variance is {weapon_tinkering.starting_weapon_variance(min, max)}%')

    best_average_damage = 0
    best_iron = 0
    best_granite = 0

    for i in range(0, 10):
        average_damage = weapon_tinkering.average_damage(min, max, float(cantrip), i)
        iron = i
        granite = 9 - i

        if average_damage >= best_average_damage:
            best_average_damage = average_damage
            best_iron = iron
            best_granite = granite

    await ctx.send(f'For this weapon, the best average damage is {best_average_damage} using {best_iron} iron and {best_granite} granite.')

client.run(secrets.token)
