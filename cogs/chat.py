from datetime import datetime
import re
import json
import random
import asyncio
import nextcord
import pytz
from util.ua import user_agents
from nextcord.ext import commands
from curl_cffi.requests import AsyncSession
from nextcord import Interaction, SlashOption
from playwright.async_api import async_playwright
from main import db, bot, logger_debug, logger_info, logger_error, check_user_in_database, add_user_to_database, is_user_banned, why_is_user_banned


async def fetch_and_save_cookies(context, user_id):
    logger_debug.debug(f"1. Round - Command - Opening Browser for user {user_id}")
    page = await context.new_page()
    logger_debug.debug(f"1. Round - Command - Opening Pi for user {user_id}")
    await page.goto('https://pi.ai/')
    logger_debug.debug(f"1. Round - Command - Waiting 5 seconds for user {user_id}")
    await asyncio.sleep(5)
    logger_debug.debug(f"1. Round - Command - Fetching cookies for user {user_id}")
    cookies_from_browser = await context.cookies()
    logger_debug.debug(f"1. Round - Command - Saving cookies for user {user_id}")
    host_session = next((cookie for cookie in cookies_from_browser if cookie.get('name') == '__Host-session'), {}).get('value')
    await db.save_cookies(host_session, user_id)
    logger_debug.debug(f"1. Round - Command - Saved cookies for user {user_id}")
    await asyncio.sleep(0.5)

async def fetch_and_save_cookies_second_round(context, user_id):
    logger_debug.debug(f"2. Round - Command - Opening Browser for user {user_id}")
    page = await context.new_page()
    logger_debug.debug(f"2. Round - Command - Opening Pi for user {user_id}")
    await page.goto('https://pi.ai/')
    logger_debug.debug(f"2. Round - Command - Waiting 5 seconds for user {user_id}")
    await asyncio.sleep(5)
    logger_debug.debug(f"2. Round - Command - Fetching cookies for user {user_id}")
    cookies_from_browser = await context.cookies()
    logger_debug.debug(f"2. Round - Command - Saving cookies for user {user_id}")
    host_session = next((cookie for cookie in cookies_from_browser if cookie.get('name') == '__Host-session'), {}).get('value')
    await db.save_cookies(host_session, user_id)
    logger_debug.debug(f"2. Round - Command - Saved cookies for user {user_id}")
    await asyncio.sleep(0.5)
    return await db.load_cookies(user_id)


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @nextcord.slash_command(name="chat", description="Talk to Pi!")
    async def chat(self, interaction: Interaction, text: str = SlashOption(description="The text to send to Pi", required=True)):
        if await is_user_banned(interaction.user.id):
            reason = await why_is_user_banned(interaction.user.id)
            await interaction.response.send_message(f"You are banned from using this command. If you want to appeal your ban, try joining the support discord.\n\nReason: {reason}", ephemeral=True)
            return
        else:
            pass

        
        #! Wäre nice so einen "Maintenance" Modus zu haben, den ich einfach in der .env datei oder in main.py aktivieren kann
        #! und dann wird nur noch der folgende Text gesendet, wenn man versucht /chat zu benutzen
        # await interaction.send("Maintenance, please try again later or **join the Discord** (</discord:1131843277033836595>) to stay up to date!", ephemeral=True)

        logger_debug.debug(f"Processing chat command for user: {interaction.user.id}")
        url = 'https://pi.ai/api/chat'

        user_id = str(interaction.user.id)
        cookies = await db.load_cookies(user_id)
        
        await interaction.response.defer(ephemeral=False)


        has_received_message = await check_user_in_database(user_id)

        if not has_received_message:
            # Add the user to the database if they haven't received a message yet
            await add_user_to_database(user_id)
            try:
                logger_info.info(f"{interaction.user.id} / {interaction.user.name} got the message!")
                await interaction.user.send("You can also continue the conversation with me here to keep it private! It's the same conversation just without the hassle of the slash command!")
            except Exception as e:
                logger_error.error(f"Error: {e}")
                await interaction.send(f"Error: {e}")
                raise e
        else:
            # logger_info.info("User already in database!")
            pass


        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=random.choice(user_agents),
                                                #record_video_dir=f"/www/wwwroot/secbot/videos/{interaction.user.id}/",
                                                java_script_enabled=True)
            
            try:
                cookies = await db.load_cookies(user_id)
                if cookies is None:
                    cookies = await fetch_and_save_cookies(context, user_id)
                    cookie = await db.load_cookies(user_id)
                    logger_debug.debug(f"Fetched and saved cookie {cookie} for user {interaction.user.id}")
                else:
                    logger_debug.debug(f"Using: {cookies}")

                        
                #logger_info.info(f"Sending request with payload: \"{text}\"")
                
                cookie_dict = await db.load_cookies(interaction.user.id)
                #logger_info.info("Cookie dict: ", cookie_dict)
                cookie = cookie_dict.get('__Host-session', None)
                #logger_info.info(f"final cookie: {cookie}")
                
                #pi = Pi(cookie=cookie, proxy=use_proxy)
                #logger_info.info(f"Created Pi instance with cookie {cookie} and proxy {use_proxy}")
                
                payload = json.dumps({"text": text})

                cookie_dict = await db.load_cookies(interaction.user.id)
                cookie = cookie_dict.get('__Host-session', None)

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

                async with AsyncSession() as s:
                    response = await s.post(url, headers=init_headers, data=payload,impersonate="chrome110",timeout=500)
                        # logger_info.info(f"Posted data for user: {user_id}")
                    if response.status_code in (403, 401, 400):
                        # Log that a 401 error was caught
                        logger_debug.debug(f"{response.status_code} error caught. Refreshing cookie for user {user_id}")

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

                        await channel.send(f"<@399668151475765258>\n> From: <@{interaction.user.id}>\n> Statuscode: {response.status_code} - `{response.content}`\n> Timestamp: {germany_time}")
                    
                    # elif response.status_code == 200:
                    #     logger_debug.debug(f"Headers: {headers}")

                    decoded_data = response.content.decode("utf-8")
                    decoded_data_log = response.content.decode("utf-8").strip
                    logger_debug.debug(f"Received response with status: {response.status_code} and content: {decoded_data_log}")
                    
                    #logger_info.info(f"Received response with status: {response.status_code} and content: {decoded_data}")

                    decoded_data = re.sub('\n+', '\n', decoded_data).strip()
                    #logger_info.info(f"Decoded data: {decoded_data}")
                    data_strings = decoded_data.split('\n')
                    # print("data_strings: ",data_strings)
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
                                await interaction.send(f'Looks like an error occurred. Report this to the dev please: (Beetle)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(e) + "```", ephemeral=True)
                                raise e
                try:
                    # Log the entire accumulated_text before processing
                    logger_info.info(f"\n------------------------------- CHAT COMMAND -------------------------------\nUser {interaction.user.id} / {interaction.user.name}: {text}\nPi: {accumulated_text}\n------------------------------- CHAT COMMAND -------------------------------")
                
                    if len(accumulated_text) > 2000:
                        parts = []
                        while len(accumulated_text) > 2000:
                            split_index = accumulated_text[:2000].rfind(' ')
                            if split_index == -1:
                                split_index = 2000  # If no space is found, split at 2000 characters
                            parts.append(accumulated_text[:split_index])
                            accumulated_text = accumulated_text[split_index:].strip()
                        parts.append(accumulated_text)  # Add the remaining part
                
                        # Send each part
                        await interaction.send(parts[0])
                        for part in parts[1:]:
                            await interaction.followup.send(part)
                    else:
                        await interaction.send(accumulated_text)
                except Exception as f:
                    logger_error.error(f"Exception of type {type(f).__name__} occurred: {f}")
                    await interaction.send(f'Looks like an error occurred. Report this to the dev please: (Will Smith)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(f) + "```")
                    raise f

            except Exception as g:
                logger_error.error(f"Exception of type {type(g).__name__} occurred: {g}")
                #await interaction.followup.send(f'Welp, looks like the bot doesn\'t want to. Report this to the dev please: (Skinwalker)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(g) + "```")
                raise g

            finally:
                await context.close()
                await browser.close()




def setup(bot):
    bot.add_cog(Chat(bot))
