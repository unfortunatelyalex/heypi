import nextcord
from nextcord.ext import commands
from main import db, logger_error
from nextcord import Interaction, SlashOption

class Cookieman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @nextcord.slash_command(name="clearcookies", description="Clear your cookies (RESETS YOUR CHAT HISTORY)", guild_ids=[1089971424367755345])
    async def clearcookies(self, interaction: Interaction):
        if interaction.user is None:
            await interaction.response.send_message("No user context.", ephemeral=True)
            return
        user_id = str(interaction.user.id)
        try:
            await db.delete_cookies(user_id)
            if interaction.response.is_done():
                await interaction.followup.send("Your cookies have been cleared.", ephemeral=True)
            else:
                await interaction.response.send_message("Your cookies have been cleared.", ephemeral=True)
        except Exception as e:
            logger_error.error(f'{e}')
            if interaction.response.is_done():
                await interaction.followup.send(f'Error:\n{e}', ephemeral=True)
            else:
                await interaction.response.send_message(f'Error:\n{e}', ephemeral=True)
            raise e

    @nextcord.slash_command(name="updatecookie", description="Update your cookies", guild_ids=[1089971424367755345])
    async def updatecookies(self, interaction: Interaction, host_session: str = SlashOption(description="Your __Host-session cookie from https://pi.ai/talk", required=True)):
        if interaction.user is None:
            await interaction.response.send_message("No user context.", ephemeral=True)
            return
        user_id = str(interaction.user.id)
        try:
            await db.save_cookies(host_session, user_id)
            msg = "Your cookies have been updated."
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except Exception as e:
            logger_error.error(f'{e}')
            if interaction.response.is_done():
                await interaction.followup.send(f'Error:\n{e}', ephemeral=True)
            else:
                await interaction.response.send_message(f'Error:\n{e}', ephemeral=True)
            raise e

    @nextcord.slash_command(name="getcookie", description="Get your cookie", guild_ids=[1089971424367755345])
    async def getcookies(self, interaction: Interaction):
        if interaction.user is None:
            await interaction.response.send_message("No user context.", ephemeral=True)
            return
        user_id = str(interaction.user.id)
        try:
            cookies = await db.load_cookies(user_id)
            if cookies is None:
                msg = 'You do not have any cookies yet. Run </chat:1131149453101912074> at least once to initialize.'
                if interaction.response.is_done():
                    await interaction.followup.send(msg, ephemeral=True)
                else:
                    await interaction.response.send_message(msg, ephemeral=True)
                return
            # Provide minimal confirmation but avoid echoing secrets back when possible
            confirm = 'Your cookie is stored. Treat it like a password and do not share it.'
            if interaction.response.is_done():
                await interaction.followup.send(confirm, ephemeral=True)
            else:
                await interaction.response.send_message(confirm, ephemeral=True)
        except Exception as e:
            logger_error.error(f'{e}')
            if interaction.response.is_done():
                await interaction.followup.send(f'Error:\n{e}', ephemeral=True)
            else:
                await interaction.response.send_message(f'Error:\n{e}', ephemeral=True)
            raise e
            

            
def setup(bot):
    bot.add_cog(Cookieman(bot))