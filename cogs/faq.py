import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from main import bot, embed_footer, logger_error


class FAQ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @nextcord.slash_command(description="Frequently Asked Questions")
    async def faq(self, interaction: Interaction):
        try:
            embed = nextcord.Embed(title="Frequently Asked Questions", color=0x418a2f)
            embed.set_thumbnail(
                url=f"{bot.user.avatar.url}"
            )
            # embed.add_field(
            #     name="Q: Why does Pi not remember what I said?",
            #     value="A: Unfortunately due to some limitations with the communication with Pi, it is not possible to save your chat history.",
            #     inline=False
            # )
            embed.add_field(
                name="Q: What is Pi?",
                value="A: Pi is an AI, a new type of computer program designed to be kind and helpful.",
                inline=False
            )
            embed.add_field(
                name="Q: What can I talk about with Pi?",
                value="A: Anything and everything! Pi is very knowledgeable and happy to help with a wide range of topics.",
                inline=False
            )
            embed.add_field(
                name="Q: Can HeyPi join a voice channel?",
                value="A: Unfortunately, Pi is a text-based AI and cannot join voice channels.",
                inline=False
            )
            embed.add_field(
                name="Q: Can HeyPi see images or videos?",
                value="A: Pi can't see images, videos or other file types you send it. But it can help you with text-based information.",
                inline=False
            )
            embed.add_field(
                name="Q: What's Pi's personality?",
                value="A: Pi is kind, supportive, knowledgeable, creative, fun, curious, and eager to improve.",
                inline=False
            )
            embed.add_field(
                name="Q: Is Pi male or female?",
                value="A: Pi is an AI and doesn't have a gender. Pi goes by 'it'.",
                inline=False
            )
            embed.add_field(
                name="Q: What is Pi not good at?",
                value="A: Pi is still in its early stages and shouldn't be relied upon for professional advice.",
                inline=False
            )
            embed.add_field(
                name="Q: How do I know if Pi is telling the truth?",
                value="A: Pi is still improving, and it's important to double-check its answers against other sources.",
                inline=False
            )
            embed.add_field(
                name="Q: What happens when Pi 'hallucinates' and makes something up?",
                value="A: Pi can sometimes provide incorrect information, so it's advisable to verify with other sources.",
                inline=False
            )
            embed.add_field(
                name="Q: What happens when Pi gets confused and is stuck on a topic?",
                value="A: If Pi gets stuck, you can encourage it to change the topic.",
                inline=False
            )
            embed.add_field(
                name="Q: What technology does Pi use?",
                value="A: Pi is built on a proprietary large language model developed by Inflection AI.",
                inline=False
            )
            # embed.add_field(
            #     name="Q: Why does Pi say it's \"LLaMA\" when I ask it who it is?",
            #     value="A: For requests that the API deems \"too simple\", stuff like \"hi\" \"hello\" \"what version are you\" \"who are you\", these responses will be handled by an open source model. That OSS model, provided by MetaAI (LLaMA-2), only can answer in english too."
            # )
            embed.set_footer(
                text=f"{embed_footer}",
                icon_url=f"{bot.user.avatar.url}"
            )
            await interaction.send(embed=embed)
        except Exception as e:
            logger_error.error(f"An error occurred: {e}")
            raise e
            

            
def setup(bot):
    bot.add_cog(FAQ(bot))