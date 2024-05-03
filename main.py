import discord
from discord.ext import commands
from credentials import *
# define the credentials file (credentials.py) with the following variables:
# bot_token
# geminiCookie
# music_dir
# See readme for more information


# define bot token in credentials file
global pickP
pickP = 0
global queue
queue = []

# HELPER FUNCTIONS---------------------------------------------

# define function to queue music
async def queueMusic(name, message):
  import os
  files = os.listdir(music_dir)
  # Check if the file exists in the music directory
  for file in files:
    if name.lower() in file.lower():
      # Add the name to the queue
      queue.append(file)
      await message.channel.send(f"{file} added to the queue.")
      return
  await message.channel.send("File not found.")

# define function to play music from local file
async def play_local_file(name, message):
  import os
  # Get the list of files in the music directory
  files = os.listdir(music_dir)

  # Check if "queue" is in the message content
  if "queue" in message.content:
    # Check if the queue is empty
    global queue
    if queue.count == 0:
      await message.channel.send("Queue is empty.")
    else:
      # Play files from the queue in order
      for file in queue:
        print("Playing file:", file)
        await message.channel.send(f"Playing {file}...")
        # Check if the bot is already connected to a voice channel
        if bot.voice_clients:
          voice_client = bot.voice_clients[0]
        else:
          # Connect to the voice channel
          voice_channel = message.author.voice.channel
          voice_client = await voice_channel.connect()
        
        # Check if audio is already playing
        if voice_client.is_playing():
          # Stop the current audio
          voice_client.stop()
        
        # Play the file using FFmpegPCMAudio
        source = discord.FFmpegPCMAudio(os.path.join(music_dir, file))
        voice_client.play(source)
      
      # Reset the queue
      queue = []
  else:
    # Search for the file based on the given name
    for file in files:
      if name.lower() in file.lower():
        print("Playing file:", file)
        await message.channel.send(f"Playing {file}...")
        # Check if the bot is already connected to a voice channel
        if bot.voice_clients:
          voice_client = bot.voice_clients[0]
        else:
          # Connect to the voice channel
          voice_channel = message.author.voice.channel
          voice_client = await voice_channel.connect()
        
        # Check if audio is already playing
        if voice_client.is_playing():
          # Stop the current audio
          voice_client.stop()
        
        # Play the file using FFmpegPCMAudio
        source = discord.FFmpegPCMAudio(os.path.join(music_dir, file))
        voice_client.play(source)
        return  # Exit the function if the file is found
    # If no matching file is found
    await message.channel.send("File not found.")

# Define a function to quit the current voice channel
async def quit_voice_channel(bot):
  if bot.voice_clients:
    for vc in bot.voice_clients:
      await vc.disconnect()

# define function to call AI
async def CallAI(text):
  from gemini import Gemini
  global pickP

  #gemini = Gemini(auto_cookies=False, cookies=geminiCookie)
  gemini = Gemini(auto_cookies=True, cookies=geminiCookie) 

  # Define the personality based on the number
  if pickP == 0:
    personality = "You are now a discord bot. Respond like this to the text beyond the ':'. DO not say anything else except for the response to the text beyond the :. After you respond, put 'START' and after you finish that part of the response put 'END': "
  elif pickP == 1:
    personality = "You are now a discord bot and you only respond in sarcastic tones. Respond like this to the text beyond the ':'. DO not say anything else except for the response to the text beyond the :. After you respond, put 'START' and after you finish that part of the response put 'END': "
  elif pickP == 2:
    personality = "You are now a discord bot. When you speak you say japanese english sounding puns like arregato-full and similar. You also love japan and love to boast about your manga collection. You are very nerdy and are obsessed with anime. Respond like this to the text beyond the ':'. DO not say anything else except for the response to the text beyond the :. After you respond, put 'START' and after you finish that part of the response put 'END': "
  elif pickP == 3:
    personality = "You are now a discord bot. When you respond you are off topic. You avoid talking about whatever is asked, and you make really bad knock knock jokes all the time. Sometimes you do answer the prompts, but with really generic or odly specific answers. You love cows and the farm, and love farming. Respond like this to the text beyond the ':'. DO not say anything else except for the response to the text beyond the :. After you respond, put 'START' and after you finish that part of the response put 'END': "
  elif pickP == 4:
    personality = "You are now a discord bot. Lets do some roleplay. Your name is now Lukas Graber. You are a boy from Medina Ohio. You love anime and love to talk about your school work and 5.0 gpa. Your best friend is Andrew Novotny. You are in boy scouts and highschool. You are aged 17, born 2006. You enjoy being smart and like to brag about it. Respond like this to the text beyond the ':'. DO not say anything else except for the response to the text beyond the :. After you respond, put 'START' and after you finish that part of the response put 'END': "
  else:
    personality = ""

  response = gemini.generate_content(personality + text)
  response = str(response.payload['candidates'][0]['text'])
  print(response)

  # Find the starting and ending positions of the desired data
  start_pos = response.find("START")
  end_pos = response.find("END")

  # Extract the data between "START" and "END"
  desired_data = response[start_pos + len("START"):end_pos].strip()

  return (desired_data)


#BOT STARTS HERE---------------------------------------------

# Replace 'bot_token' with your actual bot token
BOT_TOKEN = bot_token

# Define the intents your bot requires.
intents = discord.Intents.default()
intents.members = True  # This allows the bot to receive member-related events, like join/leave.

# Create a bot instance with a command prefix (e.g., '!bot ')
bot = commands.Bot(command_prefix='!bot ', intents=intents)

# Event: Bot is ready and connected to Discord.
@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')
  print(f'Bot ID: {bot.user.id}')
  print('------')


# Event: Check if the bot is mentioned and respond with the same message.
# WARNING: this event is order specific, use caution
@bot.event
async def on_message(message):

  # Don't respond to the bot's own messages
  if message.author == bot.user:
    return
  
  print("Message Recieved:"+message.content)
  
  #HELP---------------------------------------------
  if bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> help'):
    print("Event fired: help")
    response = "Hello! I am a Discord bot that can respond to messages using AI. To get started, mention me in a message and I will respond to you. You can also change my personality by using the command '@bot personality <number>'. To message a user, use the command '@bot message <username> <message>'."
    await message.channel.send(response)
  
  #ECHO---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> echo'):
    # Extract the word after the mention in the message content
    content = message.clean_content.replace(f'<@!{bot.user.id}>', '').strip()
    content = message.clean_content.replace(f'echo', '').strip()
    content = content.split(None, 1)[1]
    await message.channel.send(content)
  # END OF METHOD ----------------
  
  #PLAY MUSIC FROM LOCAL FILE---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> play'):
    print("Event fired: play music")
    # Extract the word after the mention in the message content
    content = message.clean_content.replace(f'<@!{bot.user.id}>', '').strip()
    content = message.clean_content.replace(f'play', '').strip()
    content = content.split(None, 1)[1]
    await play_local_file(content, message)
  # END OF METHOD ----------------
  
  #LIST ALL FILES IN MUSIC DIRECTORY---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> list music'):
    print("Event fired: list music files")
    import os
    # Get the list of files in the music directory
    files = os.listdir(music_dir)
    await message.channel.send("List of music files:")
    counter = 1
    # Create a text file to store the list of music files
    file_path = "music_files.txt"
    file_content = ""
    for file in files:
      try:
        file_content += f"{counter}. {file}\n"
      except UnicodeEncodeError:
        file_content += f"{counter}. {file.encode('utf-8').decode('utf-8', 'ignore')}\n"
      counter += 1
    with open(file_path, "w", encoding="utf-8") as file:
      file.write(file_content)

    # Send the text file
    await message.channel.send(file=discord.File(file_path))

    # Delete the text file after sending
    os.remove(file_path)
  
  #STOP PLAYING MUSIC---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> stop' or f'<@{bot.user.id}> quit' or f'<@{bot.user.id}> leave'):
    print("Event fired: stop playing music")
    await quit_voice_channel(bot)
    await message.channel.send("Bot has left.")
  # END OF METHOD ----------------
  
  #QUEUE MUSIC---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> queue'):
    print("Event fired: queue music")
    print(bot.user.id, bot.user.mention, bot.user.name, message.content)
    content = message.clean_content.replace(f'<@!{bot.user.id}>', '').strip()
    content = message.clean_content.replace(f'queue', '').strip()
    content = content.split(None, 1)[1]
    print(content)
    await queueMusic(content, message)
  # END OF METHOD ----------------
  
  #CLEAR QUEUE---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> clear queue'):
    print("Event fired: clear queue")
    queue.clear()
    await message.channel.send("Queue cleared.")
      
  #LIST QUEUED MUSIC---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> list queue'):
    print("Event fired: list queued music")
    if len(queue) == 0:
      await message.channel.send("Queue is empty.")
    else:
      await message.channel.send("List of queued music:")
      for i, file in enumerate(queue, start=1):
        await message.channel.send(f"{i}. {file}")
        
  #SPEAK VIA BOT---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> speak'):
    print("Event fired: speak via bot")
    import os
    import pyttsx3
    import asyncio
    import random

    # Extract the text to speak from the message
    parts = message.content.split()
    if len(parts) >= 3:
    
      text_to_speak = ' '.join(parts[2:])
      # Join the voice channel of the user who sent the message
      voice_channel = message.author.voice.channel
      voice_client = await voice_channel.connect()
      
      # Initialize the TTS engine
      engine = pyttsx3.init()
      
      # Set the speech rate
      engine.setProperty('rate', 150)
      
      # Set the voice
      voices = engine.getProperty('voices')
      engine.setProperty('voice', voices[(random.randint(0,1))].id)

      # Convert the text to speech
      engine.save_to_file(text_to_speak, 'output.mp3')
      engine.runAndWait()

      # Play the saved audio file
      voice_client.play(discord.FFmpegPCMAudio('output.mp3'))
    
      # Wait for the audio to finish playing
      while voice_client.is_playing():
        await asyncio.sleep(1)
      
      # Delete the audio file
      os.remove('output.mp3')
      
      # Leave the voice channel
      await voice_client.disconnect()
      
    else:
        await message.channel.send(
          "Invalid input. Please use '@bot speak <text>'.")
  
  #SET STATUS OF BOT---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> status'):
    print("Event fired: set status")
    # Extract the status from the message
    parts = message.content.split()
    if len(parts) >= 3:
      try:
        status = ' '.join(parts[2:])
        await bot.change_presence(activity=discord.Game(name=status))
        await message.channel.send(f"Status set to '{status}'.")
      except ValueError:
        await message.channel.send(
          "Invalid status. Please use '@bot status <status>'.")
    else:
      await message.channel.send(
        "Invalid input. Please use '@bot status <status>'.")
  
  #MESSAGE A USER---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> message'):
    print("Event fired: message a user")
    # Extract the username and message content from the message
    parts = message.content.split()
    if len(parts) >= 4:
      try:
        username = parts[2]
        user = discord.utils.get(bot.users, name=username)
        print(user)
        if user:
          message_content = ' '.join(parts[3:])
          await user.send(message_content)
          await message.channel.send(f"Message sent to {user.name}.")
        else:
          await message.channel.send("User not found.")
      except ValueError:
        await message.channel.send(
          "Invalid username. Please use '@bot message <username> <message>'.")
    else:
      await message.channel.send(
        "Invalid input. Please use '@bot message <username> <message>'.")
  # END OF METHOD ----------------

  #CHANGE PERSONALITY---------------------------------------------
  elif bot.user.mentioned_in(message) and message.content.startswith(
      f'<@{bot.user.id}> personality'):
    print("Event fired: change personality")
    # Extract the personality number from the message
    parts = message.content.split()
    if len(parts) == 3:
      try:
        new_personality = int(parts[2])
        if new_personality in range(0, 5):
          global pickP
          pickP = new_personality
          await message.channel.send(f"Personality set to {new_personality}")
        else:
          await message.channel.send(
            "Invalid personality number. Please choose a number between 1 and 4."
          )
      except ValueError:
        await message.channel.send(
          "Invalid input. Please use '@bot personality <number>'.")
    else:
      await message.channel.send(
        "Invalid input. Please use '@bot personality <number>'.")
  # END OF METHOD ----------------

  # RESPOND VIA BARD METHOD---------------------------------------------
  elif bot.user.mentioned_in(message):
    print("Event fired: respond via Bard")
    # Extract the word after the mention in the message content
    content = message.clean_content.replace(f'<@!{bot.user.id}>', '').strip()
    content = content.split(None, 1)[1]

    ## Call the AI to get the response
    try: 
      response = CallAI(content)
    except:
      response = "AI is not avaliable. Please try again."

    await message.channel.send(response)
  # END OF METHOD -------------------
  
  # Process bot commands (helps to avoid conflicts with other commands)
  await bot.process_commands(message)

# Run the bot with the specified token.
bot.run(BOT_TOKEN)
