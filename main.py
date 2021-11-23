from discord import Client, Intents, Embed
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from datetime import datetime, timedelta
from quests import quests

import secrets
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

client.run(secrets.token)
