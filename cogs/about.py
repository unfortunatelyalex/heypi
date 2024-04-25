from main import *

class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @nextcord.slash_command(description="Information about the bot")
    async def about(self, interaction: Interaction):
        embed = nextcord.Embed(title=f'About {bot.user.name}', color=0x418a2f)
        embed.set_thumbnail(
            url=f"{bot.user.avatar.url}"
        )
        embed.add_field(
            name="General Info",
            value=f"> Created on <t:1684771260:F> \n> ID: `{bot.user.id}`",
            inline=False
        )
        embed.add_field(
            name="About Me",
            value=f"> I'm in `{len(bot.guilds)}` servers!\n> I was written by @alexdot / <@399668151475765258>",
            inline=True
        )
        embed.add_field(
            name="Support the creator!",
            value=f"> [on Ko-fi](https://ko-fi.com/unfortunatelyalex)",
            inline=True
        )
        embed.add_field(
            name="Other links",
            value=f"> See </discord:1131843277033836595>",
            inline=False
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
    bot.add_cog(About(bot))