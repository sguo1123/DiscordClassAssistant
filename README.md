# DiscordClassAssistant

DiscordClassAssistant is a Python based Discord Bot to help with streaming/lecturing during COVID-19

## Installation
#### Create a server
If you don't already have a server, create one free one at https://discordapp.com. Simply log in, and then click the plus sign on the left side of the main window to create a new server.

#### Create an app
Go to https://discordapp.com/developers/applications/me and create a new app. On your app detail page, save the Client ID. You will need it later to authorize your bot for your server.

#### Create a bot account for your app
After creating app, on the app details page, scroll down to the section named bot, and create a bot user. **Save the token**, you will need it later to run the bot.

#### Authorize the bot for your server
Visit the URL https://discordapp.com/oauth2/authorize?client_id=XXXXXXXXXXXX&scope=bot but replace XXXX with your app client ID. Choose the server you want to add it to and select authorize.

#### Install the python package discord.py
Run pip install from your system terminal/shell/command prompt.

```bash
python -m pip install discord.py
```

#### Download and extract source files
Download the compressed ZIP file [here](https://github.com/sguo1123/MathFansJuggler/archive/master.zip) and unzip.

Instructions Sourced from: [Dungeon Dev](https://www.devdungeon.com/content/make-discord-bot-python)

## Usage
To start your instance of the bot some changes are needed to the main python file.

Open `config.ini` with a text editor such as notepad, notepad++, etc.

On download, the file should look like:
```ini
[DEFAULT]
Token = your_bot_token_here
Instructor = instructor_id
CurrentVoiceChannel = voicechannel_id
QuestionMode = single   #single or auto
```

You will need to change these values to:
1. Your personal **token** found when you created the bot account on discord (see Installation)
2. Your personal **client_id** which can be found by right clicking your username in any discord chat and selecting 'copy id' at the bottom (Discord Developer Mode must be enabled)
3. Your guilds **voicechannel_id** where the bot will mute or unmute students which can be found by right clicking the channel and selecting 'copy id' at the bottom (Discord Developer Mode must be enabled)

The resulting file should look something like this:
```ini
[DEFAULT]
Token = D43f5y0ahjqew82jZ4NViEr2YafMKhue
Instructor = 123456789012345
CurrentVoiceChannel = 23456789012345
QuestionMode = single   #single or auto
```

Once you have verified that the submitted information is correct, save and exit. Then run the attached 'run.bat'

## Commands

For the Student:
Command | Function
------------ | -------------
**!attendance or !join** | logs the student to the attendance log
**!leave** | signs student out at end of class
**!talk** | adds the user to the voice queue
**!done** | removes the user from the voice queue
**!queue** | shows current queue to ask questions
**!poll** | creates a reaction poll with format [!poll question? option1:option2]
**!equation `latex equation`** | renders latex equation as image in chat

For the Instructor:
Command | Function
------------ | -------------
**!start** | start class, will mute users in voice chat
**!end** | ends class, will unmutes all users in voice chat
**!qauto** | changes questions to cycle automatically
**!qsingle** | changes questions to cycle one at a time
**!next** | cycles to the next student in line
**!setbreakout {num}** | creates new breakout room category and creates 'num' of rooms for Students
**!clearbreakout** | removes breakout category and channels
**!clearqueue** | clears current queue for Students
**!changeinstructor {instructor_id}** | changes the current instructor to a new instructor
**!changechannel {channel_id}** | changes the current active voice channel to new channel

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
