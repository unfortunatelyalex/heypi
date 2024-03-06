from main import *

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @nextcord.slash_command(description="See all available commands.")
    async def help(self, interaction: Interaction):
        embed = nextcord.Embed(title=f'Help', color=0x418a2f)
        embed.set_thumbnail(
            url=f"{bot.user.avatar.url}"
        )
        embed.add_field(
            name="Chat",
            value=f"</chat:1131149453101912074>\n> Chat with Pi!\n(You can also direct message Pi!)",
            inline=True
        )
        embed.add_field(
            name="Help",
            value=f"</help:1131149359648604291>\n> This message.",
            inline=True
        )
        embed.add_field(
            name="FAQ",
            value=f"</faq:1131149274269368392>\n> Frequently asked questions.",
            inline=True
        )
        embed.add_field(
            name="Discord Invites",
            value=f"</discord:1131843277033836595>\n> Invite links regarding Pi.",
            inline=True
        )
        embed.add_field(
            name="About",
            value=f"</about:1131149280388845578>\n> About {bot.user.name}",
            inline=True
        )
        embed.add_field(
            name="Privacy",
            value=f"</privacy:1182253246585249842>\n> Privacy policy.",
            inline=True
        )
        # embed.add_field(
        #     name="Cookie management",
        #     value=f"</clearcookies:1131149276089700443>\n> Clears your cookies along with your chat history!",
        #     inline=True
        # )
        # embed.add_field(
        #     name="‎ ",
        #     value=f"</updatecookie:1131149277628997703>\n> Updates your cookies to \"load\" another chat session.",
        #     inline=True
        # )
        # embed.add_field(
        #     name="‎ ",
        #     value=f"</getcookie:1131149279046676501>\n> Shows the cookie you're currently using.",
        #     inline=True
        # )
        embed.set_footer(
            text=embed_footer,
            icon_url=bot.user.avatar.url
        )

        if interaction.user.avatar is not None:
            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.avatar.url
            )
        else:
            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.default_avatar.url
            )
        await interaction.send(embed=embed)
            

            
def setup(bot):
    bot.add_cog(Help(bot))