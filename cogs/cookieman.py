import nextcord
from nextcord.ext import commands
from main import db, logger_error
from nextcord import Interaction, SlashOption

class Cookieman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @nextcord.slash_command(name="clearcookies", description="Clear your cookies (RESETS YOUR CHAT HISTORY)", guild_ids=[1089971424367755345])
    async def clearcookies(self, interaction: Interaction):

        user_id = str(interaction.user.id)

        try:
            await db.delete_cookies(user_id)
            await interaction.send("Your cookies have been cleared.", ephemeral=True)
        except Exception as e:
            logger_error.error(f'{e}')
            await interaction.send('Error:\n{}'.format(e))

    @nextcord.slash_command(name="updatecookie", description="Update your cookies", guild_ids=[1089971424367755345])
    async def updatecookies(self, interaction: Interaction, host_session: str = SlashOption(description="Your __Host-session cookie from https://pi.ai/talk", required=True)):

        user_id = str(interaction.user.id)

        try:
            await db.save_cookies(host_session, user_id)
            await interaction.send("Your cookies have been updated to:\n __Host-session: `{}`".format(host_session), ephemeral=True)
        except Exception as e:
            logger_error.error(f'{e}')
            await interaction.send('Error:\n{}'.format(e))

    @nextcord.slash_command(name="getcookie", description="Get your cookie", guild_ids=[1089971424367755345])
    async def getcookies(self, interaction: Interaction):

        user_id = str(interaction.user.id)

        try:
            if await db.load_cookies(user_id) is None:
                await interaction.send('You do not have any cookies yet.\nRun </chat:1131149453101912074> at least once in order to display your cookie', ephemeral=True)
                return
            cookies = await db.load_cookies(user_id)
            await interaction.send(f"Make sure not to share your cookies with anyone and treat them like a password!\n __Host-session: `{cookies['__Host-session']}`", ephemeral=True)
        except Exception as e:
            logger_error.error(f'{e}')
            await interaction.send('Error:\n{}'.format(e))
            

            
def setup(bot):
    bot.add_cog(Cookieman(bot))