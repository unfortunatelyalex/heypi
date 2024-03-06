from main import *

class Discord(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @nextcord.slash_command(description="Invite links regarding Pi / This is also in the about command")
    async def discord(self, interaction: Interaction):
        embed = nextcord.Embed(title=f'Important discord invites', description=f"> [Support Server of this bot](https://discord.gg/CUc9PAgUYB) \n> [Official Pi Server](https://discord.com/invite/VavJn8Ff5Y) \n> [Invite me to your server](https://discord.com/oauth2/authorize?client_id=1110266304709021847&permissions=2048&scope=bot%20applications.commands)", color=0x418a2f, )
        embed.set_thumbnail(
            url=f"{bot.user.avatar.url}"
        )
        embed.set_footer(
            text=f"{embed_footer}",
            icon_url=f"{bot.user.avatar.url}"
        )

        if interaction.user.avatar is not None:
            embed.set_author(
                name=f"{interaction.user.name}",
                icon_url=f"{interaction.user.avatar.url}"
            )
        else:
            embed.set_author(
                name=f"{interaction.user.name}",
                icon_url=f"{interaction.user.default_avatar.url}"
            )
        await interaction.send(embed=embed)
            

            
def setup(bot):
    bot.add_cog(Discord(bot))