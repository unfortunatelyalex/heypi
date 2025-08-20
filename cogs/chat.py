from datetime import datetime
import re
import json
import random
import asyncio
import nextcord
import pytz
from typing import List, Optional, Any, cast
from util.ua import user_agents
from nextcord.ext import commands
from curl_cffi.requests import AsyncSession
from nextcord import Interaction, SlashOption
from playwright.async_api import async_playwright
from main import db, bot, logger_debug, logger_info, logger_error, check_user_in_database, add_user_to_database, is_user_banned, why_is_user_banned

MAX_DISCORD_MESSAGE_LEN = 2000


async def fetch_and_save_cookies(context, user_id):
    logger_debug.debug(f"1. Round - Command - Opening Browser for user {user_id}")
    page = await context.new_page()
    try:
        logger_debug.debug(f"1. Round - Command - Opening Pi for user {user_id}")
        await page.goto('https://pi.ai/', wait_until='domcontentloaded')
        # Prefer deterministic wait over fixed sleep
        try:
            await page.wait_for_load_state('networkidle', timeout=5000)
        except Exception:
            # Not all pages hit networkidle; that's fine
            pass
        logger_debug.debug(f"1. Round - Command - Fetching cookies for user {user_id}")
        cookies_from_browser = await context.cookies()
        logger_debug.debug(f"1. Round - Command - Saving cookies for user {user_id}")
        host_session = next((cookie for cookie in cookies_from_browser if cookie.get('name') == '__Host-session'), {}).get('value')
        if host_session:
            await db.save_cookies(host_session, user_id)
            logger_debug.debug(f"1. Round - Command - Saved cookies for user {user_id}")
        else:
            logger_error.error(f"Could not find __Host-session cookie for user {user_id} (round 1). Not saving to DB.")
    finally:
        await page.close()
    await asyncio.sleep(0.2)

async def fetch_and_save_cookies_second_round(context, user_id):
    logger_debug.debug(f"2. Round - Command - Opening Browser for user {user_id}")
    page = await context.new_page()
    try:
        logger_debug.debug(f"2. Round - Command - Opening Pi for user {user_id}")
        await page.goto('https://pi.ai/', wait_until='domcontentloaded')
        try:
            await page.wait_for_load_state('networkidle', timeout=5000)
        except Exception:
            pass
        logger_debug.debug(f"2. Round - Command - Fetching cookies for user {user_id}")
        cookies_from_browser = await context.cookies()
        logger_debug.debug(f"2. Round - Command - Saving cookies for user {user_id}")
        host_session = next((cookie for cookie in cookies_from_browser if cookie.get('name') == '__Host-session'), {}).get('value')
        if host_session:
            await db.save_cookies(host_session, user_id)
            logger_debug.debug(f"2. Round - Command - Saved cookies for user {user_id}")
        else:
            logger_error.error(f"Could not find __Host-session cookie for user {user_id} (round 2). Not saving to DB.")
    finally:
        await page.close()
    await asyncio.sleep(0.2)
    return await db.load_cookies(user_id)


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @nextcord.slash_command(name="chat", description="Talk to Pi!")
    async def chat(self, interaction: Interaction, text: str = SlashOption(description="The text to send to Pi", required=True)):
        # Ban gate
        user = interaction.user
        if user is None:
            await interaction.response.send_message("Interaction has no user context.", ephemeral=True)
            return
        if await is_user_banned(user.id):
            reason = await why_is_user_banned(user.id)
            await interaction.response.send_message(
                f"You are banned from using this command. If you want to appeal your ban, try joining the support discord.\n\nReason: {reason}",
                ephemeral=True,
            )
            return

        logger_debug.debug(f"Processing chat command for user: {user.id}")
        await interaction.response.defer(ephemeral=False)

        user_id = str(user.id)

        # First-message DM
        try:
            has_received_message = await check_user_in_database(user_id)
            if not has_received_message:
                await add_user_to_database(user_id)
                try:
                    logger_info.info(f"{user.id} / {user.name} got the message!")
                    await user.send(
                        "You can also continue the conversation with me here to keep it private! It's the same conversation just without the hassle of the slash command!"
                    )
                except Exception as e:
                    logger_error.error(f"Error sending onboarding DM: {e}")
        except Exception as e:
            logger_error.error(f"DB check/add failed: {e}")

        # Talk to pi.ai
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            ua = random.choice(user_agents)
            context = await browser.new_context(
                user_agent=ua,
                java_script_enabled=True,
            )

            try:
                # Ensure we have a cookie saved
                cookie_dict = await db.load_cookies(user_id)
                if not cookie_dict or "__Host-session" not in cookie_dict:
                    await fetch_and_save_cookies(context, user_id)
                    cookie_dict = await db.load_cookies(user_id)
                    if not cookie_dict or "__Host-session" not in cookie_dict:
                        cookie_dict = await fetch_and_save_cookies_second_round(context, user_id)

                cookie = cookie_dict.get("__Host-session") if cookie_dict else None

                payload = json.dumps({"text": text})
                url = "https://pi.ai/api/chat"

                def build_headers(sess_cookie: str | None):
                    return {
                        'User-Agent': ua,
                        'Accept-Language': 'en-US,en;q=0.7',
                        'Referer': 'https://pi.ai/api/chat',
                        'Content-Type': 'application/json',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                        'Connection': 'keep-alive',
                        'Cookie': f'__Host-session={sess_cookie}' if sess_cookie else ''
                    }

                async def send_once(sess_cookie: str | None):
                    async with AsyncSession() as s:
                        return await s.post(
                            url,
                            headers=build_headers(sess_cookie),
                            data=payload,
                            impersonate="chrome136",
                            timeout=500,
                        )

                # First attempt
                response = await send_once(cookie)
                if response.status_code in (400, 401, 403):
                    logger_debug.debug(f"{response.status_code} from pi.ai, refreshing cookie for user {user_id}")
                    await db.delete_cookies(user_id)
                    cookie_dict = await fetch_and_save_cookies_second_round(context, user_id)
                    cookie = cookie_dict.get("__Host-session") if cookie_dict else None
                    response = await send_once(cookie)

                if response.status_code != 200:
                    channel = bot.get_channel(1129005486973407272)
                    germany_timezone = pytz.timezone('Europe/Berlin')
                    germany_time = datetime.now(germany_timezone).strftime('%d-%m-%Y %H:%M:%S')
                    if channel is not None:
                        try:
                            await cast(Any, channel).send(
                                f"<@399668151475765258>\n> From: <@{user.id}>\n> Statuscode: {response.status_code} - `{response.content}`\n> Timestamp: {germany_time}"
                            )
                        except Exception:
                            pass

                decoded_log = response.content.decode("utf-8", errors='ignore').strip()
                logger_debug.debug(
                    f"Received response with status: {response.status_code} and content: {decoded_log}"
                )
                accumulated_text = process_response(response)

                # If empty, retry once with fresh cookie and inform the user
                if not accumulated_text.strip():
                    logger_error.error(
                        f"Empty response received for user {user.id}. Refreshing cookie and retrying automatically..."
                    )
                    await db.delete_cookies(user_id)
                    cookie_dict = await fetch_and_save_cookies_second_round(context, user_id)
                    new_cookie = cookie_dict.get("__Host-session") if cookie_dict else None
                    if not new_cookie:
                        await interaction.followup.send(
                            "I'm having trouble establishing a session. Please try again in a moment."
                        )
                        return

                    thinking_msg = await interaction.followup.send("Let me think about that for a moment...")
                    retry_response = await send_once(new_cookie)
                    if retry_response.status_code == 200:
                        retry_text = process_response(retry_response)
                        if retry_text.strip():
                            parts = split_message(retry_text)
                            await cast(Any, thinking_msg).edit(content=parts[0])
                            for part in parts[1:]:
                                await interaction.followup.send(part)
                        else:
                            await cast(Any, thinking_msg).edit(content=retry_text)
                        return

                    await cast(Any, thinking_msg).edit(content="I'm having trouble responding right now. Please try again in a moment.")
                    return

                # Normal response path
                parts = split_message(accumulated_text)
                await interaction.followup.send(parts[0])
                for part in parts[1:]:
                    await interaction.followup.send(part)

            # Fix: Use a different variable name for the exception
            except Exception as browser_error:
                logger_error.error(f"Exception of type {type(browser_error).__name__} occurred: {browser_error}")
                #await interaction.followup.send(f'Welp, looks like the bot doesn\'t want to. Report this to the dev please: (Skinwalker)\nPlease join the following Discord Server and submit the error message as a bug report:\nhttps://discord.gg/CUc9PAgUYB\n\n```Error: ' + str(browser_error) + "```")
                raise browser_error

            finally:
                await context.close()
                await browser.close()


def process_response(response):
    decoded_data = response.content.decode("utf-8")
    # Fix: Use the imported re module directly here as well
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
            except Exception:
                pass
    
    return accumulated_text


def split_message(text: str) -> list[str]:
    """Split a message into Discord-safe chunks."""
    if not text:
        return ["(empty response)"]
    if len(text) <= MAX_DISCORD_MESSAGE_LEN:
        return [text]
    parts: list[str] = []
    remaining = text
    while len(remaining) > MAX_DISCORD_MESSAGE_LEN:
        window = remaining[:MAX_DISCORD_MESSAGE_LEN]
        split_index = window.rfind(' ')
        if split_index == -1:
            split_index = MAX_DISCORD_MESSAGE_LEN
        parts.append(remaining[:split_index])
        remaining = remaining[split_index:].strip()
    if remaining:
        parts.append(remaining)
    return parts


def setup(bot):
    bot.add_cog(Chat(bot))
