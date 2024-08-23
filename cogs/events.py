import re
import json
import random
import asyncio
import nextcord
from util.ua import user_agents
from nextcord.ext import commands
from nextcord.ext.commands import Cog
from curl_cffi.requests import AsyncSession
from playwright.async_api import async_playwright
from main import add_user_to_database, bot, check_user_in_database, db, logger_debug, logger_error, logger_info, is_user_banned, why_is_user_banned, save_channel_id, get_channel_id, delete_channel_id, update_channel_id
import pytz
from datetime import datetime


async def fetch_and_save_cookies(context, user_id):
    logger_debug.debug(f"1. Round - Event - Opening Browser for user {user_id}")
    page = await context.new_page()
    logger_debug.debug(f"1. Round - Event - Opening Pi for user {user_id}")
    await page.goto('https://pi.ai/')
    logger_debug.debug(f"Event - Waiting 5 seconds for user {user_id}")
    await asyncio.sleep(5)
    logger_debug.debug(f"1. Round - Event - Fetching cookies for user {user_id}")
    cookies_from_browser = await context.cookies()
    logger_debug.debug(f"1. Round - Event - Saving cookies for user {user_id}")
    host_session = next((cookie for cookie in cookies_from_browser if cookie.get('name') == '__Host-session'), {}).get('value')
    await db.save_cookies(host_session, user_id)
    logger_debug.debug(f"1. Round - Event - Saved cookies for user {user_id}")
    await asyncio.sleep(0.5)

async def fetch_and_save_cookies_second_round(context, user_id):
    logger_error.error(f"2. Round - Event - Opening Browser for user {user_id}")
    page = await context.new_page()
    logger_error.error(f"2. Round - Event - Opening Pi for user {user_id}")
    await page.goto('https://pi.ai/')
    logger_error.error(f"2. Round - Event - Waiting 5 seconds for user {user_id}")
    await asyncio.sleep(5)
    logger_error.error(f"2. Round - Event - Fetching cookies for user {user_id}")
    cookies_from_browser = await context.cookies()
    logger_error.error(f"2. Round - Event - Saving cookies for user {user_id}")
    host_session = next((cookie for cookie in cookies_from_browser if cookie.get('name') == '__Host-session'), {}).get('value')
    await db.save_cookies(host_session, user_id)
    logger_error.error(f"2. Round - Event - Saved cookies for user {user_id}")
    await asyncio.sleep(0.5)
    return await db.load_cookies(user_id)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @nextcord.slash_command(name="setup", description="Setup a message channel")
    async def setup_channel(self, i: nextcord.Interaction, channel: nextcord.TextChannel = nextcord.SlashOption(description="The channel to setup")):
        # Check if the user is an admin
        if i.user.guild_permissions.administrator:
            guild_id = str(i.guild_id)  # Convert guild ID to string if your database expects a string
            # Check if there's already a channel id defined for the guild
            existing_channel_id = await get_channel_id(guild_id)
            if existing_channel_id:
                # Update the channel id
                await update_channel_id(guild_id, channel.id)
                await i.response.send_message(f"Channel {channel.mention} has been updated as the message channel.", ephemeral=True)
            else:
                # Save the channel id
                await save_channel_id(guild_id, channel.id)
                await i.response.send_message(f"Channel {channel.mention} has been set as the message channel.", ephemeral=True)
        else:
            await i.response.send_message("You need to be an admin to use this command.", ephemeral=True)

    @nextcord.slash_command(name="delsetup", description="Delete the message channel")
    async def delete_channel(self, i: nextcord.Interaction):
        # Check if the user is an admin
        if i.user.guild_permissions.administrator:
            guild_id = str(i.guild_id)
            # Check if there's already a channel id defined for the guild
            existing_channel_id = await get_channel_id(guild_id)
            if existing_channel_id:
                # Delete the channel id
                await delete_channel_id(guild_id)  # Use the correct function to delete the channel ID
                await i.response.send_message("Message channel has been deleted.", ephemeral=True)
            else:
                await i.response.send_message("There's no message channel set up.", ephemeral=True)
        else:
            await i.response.send_message("You need to be an admin to use this command.", ephemeral=True)

    

    @Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author == self.bot.user:
            return
        

        if message.guild is None and not message.author.bot:
            # check if user is banned
            if await is_user_banned(message.author.id):
                reason = await why_is_user_banned(message.author.id)
                await message.reply(f"You are banned from using this command. If you want to appeal your ban, try joining the support discord.\n\nReason: {reason}")
                return
            else:
                pass
            
            
            #await message.author.send("Maintenance, please try again later or join the Discord to stay up to date!")

            logger_debug.debug(f"Processing message command for user: {message.author.id}")
            url = 'https://pi.ai/api/chat'

            user_id = str(message.author.id)
            cookies = await db.load_cookies(user_id)
            
            has_received_message = await check_user_in_database(user_id)

            if not has_received_message:
                # Add the user to the database if they haven't received a message yet
                await add_user_to_database(user_id)
                try:
                    logger_info.info(f"{message.author.id} / {message.author.name} got the message!")
                    await message.author.send("You can also continue the conversation with me by using </chat:1131149453101912074> in any server I'm in. You can of course also stay in here if you want to keep your conversations private.")
                except Exception as e:
                    logger_error.error(f"Error: {e}")
                    await message.author.send(f"Error: {e}")
            else:
                # logger_info.info("User already in database!")
                pass

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(user_agent=random.choice(user_agents),
                                                    #record_video_dir=f"/www/wwwroot/secbot/videos/{message.author.id}/",
                                                    java_script_enabled=True)
                
                try:
                    cookies = await db.load_cookies(user_id)
                    if cookies is None:
                        await message.channel.trigger_typing()
                        cookies = await fetch_and_save_cookies(context, user_id)
                        cookie = await db.load_cookies(user_id)
                        logger_debug.debug(f"Fetched and saved cookie {cookie} for user {message.author.id}")
                    else:
                        await message.channel.trigger_typing()
                        logger_debug.debug(f"Using: {cookies}")

                    payload = json.dumps({"text": message.content})

                    cookie_dict = await db.load_cookies(message.author.id)
                    #logger_info.info("Cookie dict: ", cookie_dict)
                    cookie = cookie_dict.get("__Host-session", None)
                    #logger_info.info(f"final cookie: {cookie}")

                    url = "https://pi.ai/api/chat"

                    init_headers = {
                            'User-Agent': random.choice(user_agents),
                            'Accept-Language': 'en-US,en;q=0.7',
                            'Referer': 'https://pi.ai/api/chat',
                            'Content-Type': 'application/json',
                            'Sec-Fetch-Dest': 'empty',
                            'Sec-Fetch-Mode': 'cors',
                            'Sec-Fetch-Site': 'same-origin',
                            'Connection': 'keep-alive',
                            'Cookie': f'__Host-session={cookie}'
                    }

                    init_headers["Cookie"] = f"__Host-session={cookie}"

                    async with AsyncSession() as s:
                        response = await s.post(url, headers=init_headers, data=payload,impersonate="chrome110",timeout=500)
                            # logger_info.info(f"Posted data for user: {user_id}")
                        if response.status_code in (403, 401):
                            # Log that a 401 error was caught
                            logger_debug.debug(f"401 error caught. Refreshing cookie for user {user_id}")

                            # Delete the old cookie
                            await db.delete_cookies(user_id)
                            logger_debug.debug(f"Deleted old cookies for user {user_id}")

                            # Fetch and save the new cookie
                            new_cookie = await fetch_and_save_cookies_second_round(context, user_id)
                            logger_debug.debug(f"Fetched and saved new cookie for user {user_id}: {new_cookie}")
                            new_cookie_value = new_cookie['__Host-session']

                            error_headers = {
                                'User-Agent': init_headers['User-Agent'],
                                'Accept-Language': 'en-US,en;q=0.7',
                                'Referer': 'https://pi.ai/api/chat',
                                'Content-Type': 'application/json',
                                'Sec-Fetch-Dest': 'empty',
                                'Sec-Fetch-Mode': 'cors',
                                'Sec-Fetch-Site': 'same-origin',
                                'Connection': 'keep-alive',
                                'Cookie': f'__Host-session={new_cookie_value}'
                            }

                            logger_debug.debug(f"Sending request with the headers: {error_headers}")
                            # Resend the request with the updated headers
                            response = await s.post(url, headers=error_headers, data=payload, impersonate="chrome110", timeout=500)
                            logger_debug.debug(f"Resent request with new cookie. Status Code: {response.status_code}")
                            
                        elif response.status_code != 200:
                            #logger_error.error(f"Statuscode: {response.status_code} - {response.reason}")
                            # get the channel by id 1129005486973407272
                            channel = bot.get_channel(1129005486973407272)
                            germany_timezone = pytz.timezone('Europe/Berlin')
                            germany_time = datetime.now(germany_timezone).strftime('%d-%m-%Y %H:%M:%S')

                            await channel.send(f"<@399668151475765258>\n> From: <@{message.author.id}>\n> Statuscode: {response.status_code} - `{response.content}`\n> Timestamp: {germany_time}")

                        decoded_data = response.content.decode("utf-8")
                        #logger_info.info(f"Received response with status: {response.status_code} and content: {decoded_data}")

                        decoded_data = re.sub('\n+', '\n', decoded_data).strip()
                        #logger_info.info(f"Decoded data: {decoded_data}")
                        data_strings = decoded_data.split('\n')
                        accumulated_text = ""
                        # print("data_strings: ",data_strings)

                        for data_string in data_strings:
                            if data_string.startswith('data:'):
                                json_str = data_string[5:].strip()
                                # print("json_str: ",json_str)
                                try:
                                    data = json.loads(json_str)
                                    if 'text' in data:
                                        accumulated_text += data['text']
                                except Exception as e:
                                    logger_error.error(f"Exception of type {type(e).__name__} occurred: {e}")
                                    await message.author.send(f'Looks like an error occurred. Report this to the dev please: (Beetle)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(e) + "```")
                    try:
                        await message.author.send(accumulated_text)
                        logger_info.info(f"\n------------------------------- MESSAGE COMMAND -------------------------------\nUser {message.author.id} / {message.author.name}: {message.content}\nPi: {accumulated_text}\n------------------------------- MESSAGE COMMAND -------------------------------")
                    except Exception as e:
                        logger_error.error(f"Exception of type {type(e).__name__} occurred: {e}")
                        await message.author.send(f'Looks like an error occurred. Report this to the dev please: (Will Smith)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(e) + "```")


                except Exception as e:
                    logger_error.error(f"Exception of type {type(e).__name__} occurred: {e}")
                    await message.author.send(f'Welp, looks like the bot doesn\'t want to. Report this to the dev please: (Firefly)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(e) + "```")

                finally:
                    await context.close()
                    await browser.close()
                    return





        guild_id = str(message.guild.id)  # Convert guild ID to string if necessary
        if await is_user_banned(message.author.id):
            channel_id = await get_channel_id(guild_id)  # Updated to include guild_id
            if channel_id and message.channel.id == int(channel_id):
                if (message.reference and message.reference.resolved and message.reference.resolved.author == self.bot.user) or self.bot.user in message.mentions:
                    reason = await why_is_user_banned(message.author.id)
                    await message.reply(f"You are banned from using this command. If you want to appeal your ban, try joining the support discord.\n\nReason: {reason}")
                return
            else:
                return
        
    
        channel_id = await get_channel_id(guild_id)  # Updated to include guild_id
        if channel_id and message.channel.id == int(channel_id):
            # Check if the message is a reply to the bot
            if (message.reference and message.reference.resolved and message.reference.resolved.author == self.bot.user) or self.bot.user in message.mentions:
                logger_debug.debug(f"Processing API request for user: {message.author.id}")
                url = 'https://pi.ai/api/chat'

                user_id = str(message.author.id)
                cookies = await db.load_cookies(user_id)

                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(user_agent=random.choice(user_agents))
                    
                    try:
                        if cookies is None:
                            await message.channel.trigger_typing()
                            cookies = await fetch_and_save_cookies(context, user_id)
                            cookie = await db.load_cookies(user_id)
                            logger_debug.debug(f"Fetched and saved cookie {cookie} for user {message.author.id}")
                        else:
                            await message.channel.trigger_typing()
                            logger_debug.debug(f"Using: {cookies}")

                        payload = json.dumps({"text": message.content})

                        cookie_dict = await db.load_cookies(message.author.id)
                        cookie = cookie_dict.get("__Host-session", None)

                        init_headers = {
                            'User-Agent': random.choice(user_agents),
                            'Accept-Language': 'en-US,en;q=0.7',
                            'Referer': 'https://pi.ai/api/chat',
                            'Content-Type': 'application/json',
                            'Sec-Fetch-Dest': 'empty',
                            'Sec-Fetch-Mode': 'cors',
                            'Sec-Fetch-Site': 'same-origin',
                            'Connection': 'keep-alive',
                            'Cookie': f'__Host-session={cookie}'
                        }

                        async with AsyncSession() as s:
                            response = await s.post(url, headers=init_headers, data=payload, impersonate="chrome110", timeout=500)
                            if response.status_code in (403, 401):
                                # Log that a 401 error was caught
                                logger_debug.debug(f"401 error caught. Refreshing cookie for user {user_id}")

                                # Delete the old cookie
                                await db.delete_cookies(user_id)
                                logger_debug.debug(f"Deleted old cookies for user {user_id}")

                                # Fetch and save the new cookie
                                new_cookie = await fetch_and_save_cookies_second_round(context, user_id)
                                logger_debug.debug(f"Fetched and saved new cookie for user {user_id}: {new_cookie}")
                                new_cookie_value = new_cookie['__Host-session']

                                headers = {
                                    'User-Agent': init_headers['User-Agent'],
                                    'Accept-Language': 'en-US,en;q=0.7',
                                    'Referer': 'https://pi.ai/api/chat',
                                    'Content-Type': 'application/json',
                                    'Sec-Fetch-Dest': 'empty',
                                    'Sec-Fetch-Mode': 'cors',
                                    'Sec-Fetch-Site': 'same-origin',
                                    'Connection': 'keep-alive',
                                    'Cookie': f'__Host-session={new_cookie_value}'
                                }

                                logger_debug.debug(f"Sending request with the headers: {headers}")
                                # Resend the request with the updated headers
                                response = await s.post(url, headers=headers, data=payload, impersonate="chrome110", timeout=500)
                                logger_debug.debug(f"Resent request with new cookie. Status Code: {response.status_code}")
                                
                            elif response.status_code != 200:
                                #logger_error.error(f"Statuscode: {response.status_code} - {response.reason}")
                                # get the channel by id 1129005486973407272
                                channel = bot.get_channel(1129005486973407272)
                                germany_timezone = pytz.timezone('Europe/Berlin')
                                germany_time = datetime.now(germany_timezone).strftime('%d-%m-%Y %H:%M:%S')

                                await channel.send(f"<@399668151475765258>\n> From: <@{message.author.id}>\n> Statuscode: {response.status_code} - `{response.content}`\n> Timestamp: {germany_time}")

                            if response.status_code == 200:
                                decoded_data = response.content.decode("utf-8")
                                decoded_data = re.sub('\n+', '\n', decoded_data).strip()
                                data_strings = decoded_data.split('\n')
                                accumulated_text = ""

                                for data_string in data_strings:
                                    if data_string.startswith('data:'):
                                        json_str = data_string[5:].strip()
                                        try:
                                            data = json.loads(json_str)
                                            if 'text' in data:
                                                accumulated_text += data['text']
                                        except Exception as e:
                                            logger_error.error(f"Exception of type {type(e).__name__} occurred: {e}")
                                            await message.reply(f'Looks like an error occurred. Report this to the dev please: (MC Cheese)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(e) + "```")
                                await message.reply(accumulated_text)
                                logger_info.info(f"\n------------------------------- MESSAGE CHANNEL COMMAND -------------------------------\nUser {message.author.id} / {message.author.name}: {message.content}\nPi: {accumulated_text}\n------------------------------- MESSAGE CHANNEL COMMAND -------------------------------")
                            else:
                                logger_error.error(f"Failed to get a valid response from the API. Status Code: {response.status_code}")
                                await message.reply("Sorry, I couldn't process your request. Please try again later. (uh oh)")
                    except Exception as e:
                        logger_error.error(f"Exception of type {type(e).__name__} occurred: {e}")
                        await message.reply(f'Looks like an error occurred. Report this to the dev please: (MC Slot)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(e) + "```")
                    finally:
                        await context.close()
                        await browser.close()




            
        await self.bot.process_commands(message)



def setup(bot):
    bot.add_cog(Events(bot))