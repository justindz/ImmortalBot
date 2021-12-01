# ImmortalBot

## Overview

ImmortalBot is a Discord bot that provides convenience features for players of Asheron's Call via ACE server emulators. The bot connects to a single ACE instance, and therefore needs to be deployed separately to each Discord server and connected to its respective ACE server. This ensures that the bot's creator (https://www.cranemountaingaming.com) does not have any connection info for private servers that use the bot for security purposes, and also prevents mishaps incase ACE server owners change aspects of the game which would make the bot's features inaccurate (e.g. modifying rent timers, quest timers, or global damage calculations).

## Features

As of the current version, ImmortalBot supports the following commands:

### /timer account: quest:

The bot will look up the quest timers for a pre-configured set of quests for all characters on the specified account and DM the information to you. This command uses DMs as the resulting info for large accounts can spam channels.

The currently supported quests are:
* Aug Gem: Bellas
* Aug Gem: Luminance
* Aug Gem: Diemos
* Stipend - Society
* Stipend - General

To suggest more quest timers, please use the GitHub issues or find the author (justindz) on the DrunkenFell or ACEmulator Discord servers.

### /rent account:

The bot will look up the rent due timer for the specified account. This may have odd results if rent timers have been disabled on your ACE server.

### /ig min: max: cantrip:

The bot will calculate and recommand the optimum combination of Iron and Granite (hence, ig) tinkers based on the provided starting weapon characteristics. For calculation purposes, the bot uses the following assumptions:
* Critical Hit Rate of 11%
* Critical Hit Mod of 2x
* Damage Rating of 5 (Weapon Mastery)
* Blood Drinker 8
* 9 Tinks
* Resistance or Armor Rend Imbue (does not support Critical Strike or Crippling Blow)

These assumptions produce consistent results for most characters below an extreme power level. Note that the resulting average damage numbers display a bit differently from Endy's Tinkering Calculator and Xenocide's Calculator, due to some of the assumptions made and the lower complexity level of the calculation, but the resulting variance, iron/granite recommendations, and overall result have been tested against both calculators to ensure consistency. If you find any deviations across calculators in the optimum recommendation (not the display numbers), please use the GitHub issues to report them.

## Dependencies

* ImmortalBot is written in Python (currently 3.10)
* PyMySQL 1.0.2 is used to connect to the ACE database
* discord.py 1.7.3 is used for Discord interaction
* discord-py-interactions 3.0.2 adds support for Discord's slash commands

## Requirements

In order to run the bot successfully with your ACE and Discord servers, you need the following:
* A Discord developer application
* A read-only user for the bot to connect to the ACE DBs
* A server from which to run the bot, which has Python 3 and the above Dependencies installed

### Discord Setup

Discord application and bot setup is a bit specialized to repeat entirely here, and subject to some amount of change on Discord's end. Therefore, this section of the guide only covers specifically what ImmortalBot needs as a bot to operate correctly.

General steps:
* Create a new Discord application in the developer portal (recommended to call it ImmortalBot for consistency, and I would be chuffed if you reached out to me to use the Crane Mountain Gaming logo for the bot's avatar!)
* Copy the token from the Bot section, which you will need later in Bot Configuration
* Set up the following OAuth2 Scopes and Bot Permissions
* Generate an OAuth2 URL and invoke it to authorize your bot to join your Discord Server

OAuth2 Scopes:
* bot
* applications.commands

OAuth2 Bot Permissions:
* Manage Roles (future use)
* Read Messages/View Channels
* Send Messages
* Manage Messages
* Read Message History
* Mention Everyone (future use)
* Add Reactions (future use)
* Use Slash Commands

### Bot Configuration

* Create a file named "secrets.py" in the bot's directory (same location as main.py, quests.py, and weapon_tinkering.py) to house connection information for the bot
* If you plan to use source control to customize your bot or submit pull requests, please make sure to gitignore your secrets.py file so you do not share your private connection info!
* Add the following variables to secrets.py (order does not matter, syntax is standard Python):
```
token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # a long string provided by Discord when you successfully complete Discord Setup
servers = [1234567890] # the integer IDs of the Discord server(s) you want the bot to join, which needs to be an array even if a single value
db_uri = 'localhost' # the address of the ACE server as a string, which may be localhost/127.0.0.1 or an internet address depending on where you run the bot
db_port = 3306 # your ACE DB port number as an integer
db_user = 'immortalbot' # recommended to create a unique read-only DB user for the bot, but any user with read permissions should work
db_pwd = 'password' # please don't use this password!
```

### Bot Deployment

The bot is run by simply running 'main.py' as a Python process. Note that the bot will display the following non-fatal warning:
> Detected discord.Client! It is highly recommended to use `commands.Bot`. Do not add any `on_socket_response` event.

Provided no additional warnings or errors display, which may take a few seconds to appear due to Discord-side latency in registering the slash commands, you should see the bot as an online member on your Discord server and be able to use the /timer and /ig slash commands.

## Customization

You may wish to extend the bot by adding additional quest timers or customizing the tinkering calculator. The latter is a bit more complicated, so generally poke around in weapon_tinkering.py to understand how it works and which default values you can change. The calculations were ported from a decompiled version of Endy's Tinkering Calculator, and simplified with the list of assumptions above. If you want to increase the complexity of the calculations beyond changing default assumptions such as damage ratings, I recommend decompiling Endy's Tinkering Calculator and following those patterns and testing against Endy's and Xenocide's calculators.

Adding quest timers is more straightforward. The python code file 'quests.py' contains a dictionary of supported quests. You can add additional quests by extending the dictionary and restarting the bot. The key for each entry is the quest string from the ACE database, and the value is a tuple of the display string you want to show up as the slash command option and the quest timer in days.

Generally, I recommend customizing to include any quest timers which may be unique to your server (aka, custom content). For any quest timers that are supported by "vanilla" ACE, please either submit a pull request, add an issue, or just contact me (Discord or ace@cranemountaingaming.com) with the suggestion depending on your technical skills and we'll add it to the official bot for everyone to enjoy!

## License

The MIT License (MIT)
Copyright © 2021 Crane Mountain Gaming, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
