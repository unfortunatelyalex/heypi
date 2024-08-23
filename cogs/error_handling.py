import os
import sys
import github
import platform
import nextcord
import traceback
from nextcord import Embed
from nextcord.ext import commands
from dotenv import load_dotenv
from main import bot, logger_github

# Load environment variables from .env file
load_dotenv()

class ApplicationCommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.github_repo = "unfortunatelyalex/heypi"  # Replace with your GitHub repository
        self.private_key_path = os.getenv('GITHUB_KEY_PATH')
        self.app_id = os.getenv('GITHUB_APP_ID')
        self.installation_id = os.getenv('GITHUB_APP_INSTALLATION_ID')

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction, exception):
        error_message = str(exception)
        tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
        traceback_str = "".join(tb).strip()

        # Determine if the channel is a direct message
        channel_type = "Direct Message" if isinstance(interaction.channel, nextcord.DMChannel) else "Guild Channel"

        issue_title = f"Auto Generated Report: {error_message}"
        issue_body = (f"**User Message:** {interaction.data}\n"
                      f"**Error:** {error_message}\n"
                      f"**Traceback:** \n```python\n{traceback_str}\n```\n"
                      f"**Command:** `{interaction.application_command.name}`\n"
                      f"**Author:** {interaction.user}\n"
                      f"**Channel:** {interaction.channel} ({channel_type})\n"
                      f"**Python Version:** `{sys.version}`\n"
                      f"**nextcord Version:** `{nextcord.__version__}`\n"
                      f"**OS:** `{platform.system()} {platform.release()}`")

        try:
            if not self.private_key_path:
                raise ValueError("Private key path is not set. Please set the GITHUB_KEY_PATH environment variable.")

            with open(self.private_key_path, 'r') as key_file:
                private_key = key_file.read()

            integration = github.GithubIntegration(self.app_id, private_key)
            token = integration.get_access_token(self.installation_id)

            g = github.Github(token.token)
            repo = g.get_repo(self.github_repo)
            issue = repo.create_issue(title=issue_title, body=issue_body)
            bug_label = repo.get_label("bug")
            issue.add_to_labels(bug_label)

            embed = Embed(title='An error occurred', color=0xff0000, url=issue.html_url)
            embed.add_field(name='Error', value=error_message)
            #await interaction.response.send_message(embed=embed, ephemeral=True)
            logger_github.info(f"New issue opened on GitHub: {issue.html_url}")
        except github.GithubException as gh_exc:
            # await interaction.response.send_message(f"GitHub API error: {gh_exc.data['message']}", ephemeral=True)
            logger_github.error(f"GitHub API error: {gh_exc.data['message']}")
        except ValueError as ve:
            # await interaction.response.send_message(f"Configuration error: {ve}", ephemeral=True)
            logger_github.error(f"Configuration error: {ve}")
        except Exception as e:
            # await interaction.response.send_message(f"Oops, something happened. Unable to record the error.\n{e}", ephemeral=True)
            logger_github.error(f"Unable to open an issue: {e}")

def setup(bot):
    bot.add_cog(ApplicationCommandError(bot))