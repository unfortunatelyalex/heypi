from main import *

class Privacy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @nextcord.slash_command(description="Data information about the bot")
    async def privacy(self, interaction: Interaction):
        await interaction.send("""
Privacy Policy for HeyPi Discord Bot

    Last updated: 7th of December, 2023

    This Privacy Policy explains how the HeyPi Discord Bot ("HeyPi," "we," "us," or "our") may collect, use, and disclose your information, specifically the information sent through messages when interacting with the bot on the Discord platform. We are committed to maintaining the privacy of users and ensuring the security of any information collected.

    By using HeyPi on Discord, you agree to the collection and use of information in accordance with this Privacy Policy.

    
1. Information we collect

    When interacting with HeyPi, we may temporarily (15 days) store your User ID for the purpose of tracking your requests to see if everything went through, as well as providing appropriate responses. This information may include but is not limited to:

    
- Your User ID, message content and your username on Discord

    Please note that we do not collect any sensitive personal information.

    
2. How we use your Information

    We use the information collected for the following purposes:

    
- To provide the features and functionality of HeyPi
  - To improve and optimize the performance of HeyPi
    - To monitor usage and detect, prevent, and address technical issues
    - To respond to user support requests.
""", ephemeral=True)
        await interaction.followup.send("""
3. Information Sharing & Disclosure

    We do not sell, trade, or rent any user's personal identification information to third parties. We may share generic aggregated demographic information not linked to any personal identification information regarding HeyPi users.

    
4. Deleting your Information

    If you wish to delete any information that was temporarily stored while using HeyPi, please submit a request in the support server, under the #support channel <#1129005475669737512>, and mention the bot's creator, @alexdot. We will address your request as soon as possible.

    
5. Changes to this Privacy Policy

    We reserve the right to update or change our Privacy Policy at any time, and it is your responsibility to check this Privacy Policy periodically. Your continued use of HeyPi after we post any modifications to the Privacy Policy will constitute your acknowledgment of these changes and consent to abide and be bound by the modified Privacy Policy.

    
6. Contact Us

    If you have any questions about this Privacy Policy, please contact the creator of HeyPi by sending a message directly to @alexdot on Discord.
""", ephemeral=True)            

            
def setup(bot):
    bot.add_cog(Privacy(bot))