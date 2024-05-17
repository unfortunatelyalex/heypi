import re
import json
import random
import asyncio
import nextcord
from util.ua import user_agents
from nextcord.ext import commands
from curl_cffi.requests import AsyncSession
from nextcord import Interaction, SlashOption
from playwright.async_api import async_playwright
from main import db, bot, logger_debug, logger_info, logger_error, check_user_in_database, add_user_to_database


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
    logger_error.error(f"2. Round - Command - Opening Browser for user {user_id}")
    page = await context.new_page()
    logger_error.error(f"2. Round - Command - Opening Pi for user {user_id}")
    await page.goto('https://pi.ai/')
    logger_error.error(f"2. Round - Command - Waiting 5 seconds for user {user_id}")
    await asyncio.sleep(5)
    logger_error.error(f"2. Round - Command - Fetching cookies for user {user_id}")
    cookies_from_browser = await context.cookies()
    logger_error.error(f"2. Round - Command - Saving cookies for user {user_id}")
    host_session = next((cookie for cookie in cookies_from_browser if cookie.get('name') == '__Host-session'), {}).get('value')
    await db.save_cookies(host_session, user_id)
    logger_error.error(f"2. Round - Command - Saved cookies for user {user_id}")
    await asyncio.sleep(0.5)
    return await db.load_cookies(user_id)


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @nextcord.slash_command(name="chat", description="Talk to Pi!")
    async def chat(self, interaction: Interaction, text: str = SlashOption(description="The text to send to Pi", required=True)):
        use_proxy = False
        logger_debug.debug(f"Processing chat command for user: {interaction.user.id}")
        url = 'https://pi.ai/api/chat'

        user_id = str(interaction.user.id)
        cookies = await db.load_cookies(user_id)
        
        await interaction.response.defer(ephemeral=False)


        has_received_message = await check_user_in_database(user_id)

        should_send_message = random.randint(1, 1) == 1

        if should_send_message:
            if not has_received_message:
                # Add the user to the database if they haven't received a message yet
                await add_user_to_database(user_id)
                try:
                    logger_info.info(f"{interaction.user.id} / {interaction.user.name} got the message!")
                    await interaction.user.send("You can also chat with HeyPi in here without using </chat:1131149453101912074>!")
                except Exception as e:
                    logger_error.error(f"Error: {e}")
                    await interaction.send(f"Error: {e}")
            else:
                # logger_info.info("User already in database!")
                pass
        else:
            # logger_info.info("User will not receive a message.")
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

                headers = {
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
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
                    response = await s.post(url, headers=headers, data=payload,impersonate="chrome110",timeout=500)
                        # logger_info.info(f"Posted data for user: {user_id}")
                    if response.status_code == 403:
                        # Log that a 401 error was caught
                        logger_debug.debug(f"403 error caught. Refreshing cookie for user {user_id}")

                        # Delete the old cookie
                        await db.delete_cookies(user_id)
                        logger_debug.debug(f"Deleted old cookies for user {user_id}")

                        # Fetch and save the new cookie
                        new_cookie = await fetch_and_save_cookies_second_round(context, user_id)
                        logger_debug.debug(f"Fetched and saved new cookie for user {user_id}: {new_cookie}")
                        new_cookie_value = new_cookie['__Host-session']

                        headers = {
                            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
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
                    elif response.status_code == 401:
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
                            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
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
                        # logger_debug.debug(f"401 caught")
                        # # await interaction.user.send("Your cookie now gets deleted, since Pi asks you to log in.\n" \
                        # #                             "If you want to continue chatting in this session, your `__Host-session` cookie will now" \
                        # #                             "be displayed to you which you can use to log in into Pi in your browser via cookie" \
                        # #                             "editor extension:\nYour `__Host-session` cookie is: `{}`".format(cookies['__Host-session']))
                        # #logger_error.error(f"User {interaction.user.id} / {interaction.user.name}: 403 error detected. Refreshing cookies...")
                    elif response.status_code != 200:
                        #logger_error.error(f"Statuscode: {response.status_code} - {response.reason}")
                        # get the channel by id 1129005486973407272
                        channel = bot.get_channel(1129005486973407272)
                        await channel.send(f"<@399668151475765258>\nFrom: <@{interaction.user.id}> Statuscode: {response.status_code} - {response.content}")
                    
                    # elif response.status_code == 200:
                    #     logger_debug.debug(f"Headers: {headers}")

                    decoded_data = response.content.decode("utf-8")
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
                try:
                    await interaction.send(accumulated_text)
                    logger_info.info(f"\n----------------------- CHAT COMMAND --------------------------------\nUser {interaction.user.id} / {interaction.user.name}: {text}\nPi: {accumulated_text}\n------------------------ CHAT COMMAND -------------------------------")
                except Exception as e:
                    logger_error.error(f"Exception of type {type(e).__name__} occurred: {e}")
                    await interaction.send(f'Looks like an error occurred. Report this to the dev please: (Will Smith)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(e) + "```")

            except Exception as e:
                logger_error.error(f"Exception of type {type(e).__name__} occurred: {e}")
                await interaction.followup.send(f'Welp, looks like the bot doesn\'t want to. Report this to the dev please: (Skinwalker)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(e) + "```")

            finally:
                await context.close()
                await browser.close()




def setup(bot):
    bot.add_cog(Chat(bot))
