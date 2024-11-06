import os
import sys
import pytz
import github
import platform
import nextcord
import traceback
from nextcord import Embed
import nextcord.context_managers
from nextcord.ext import commands
from dotenv import load_dotenv
from main import bot, logger_github

# Load environment variables from .env file
load_dotenv()

class ApplicationCommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.github_repo = "unfortunatelyalex/heypi"
        self.private_key_path = os.getenv('GITHUB_KEY_PATH')
        self.app_id = os.getenv('GITHUB_APP_ID')
        self.installation_id = os.getenv('GITHUB_APP_INSTALLATION_ID')

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: nextcord.Interaction, exception):
        error_message = str(exception)
        tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
        traceback_str = "".join(tb).strip()
        utc_time = interaction.created_at
        cet_time = utc_time.astimezone(pytz.timezone('Europe/Berlin'))

        # Determine if the channel is a direct message
        channel_type = "Direct Message" if isinstance(interaction.channel, nextcord.DMChannel) else "Guild Channel"

        issue_title = f"Interaction error encountered: {error_message}"
        issue_body = (f"**User Message:** {interaction.data}\n"
                      f"**Error:** {error_message}\n"
                      f"**Traceback:** \n```python\n{traceback_str}\n```\n"
                      f"**Time:** {cet_time.strftime('%d-%m-%Y  -  %H:%M:%S')}\n"
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



    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, exception):
        error_message = str(exception.original) if hasattr(exception, 'original') else str(exception)
        tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
        traceback_str = "".join(tb).strip()
        utc_time = ctx.message.created_at
        cet_time = utc_time.astimezone(pytz.timezone('Europe/Berlin'))

        # Determine if the channel is a direct message
        channel_type = "Direct Message" if isinstance(ctx.channel, nextcord.DMChannel) else "Guild Channel"

        issue_title = f"Event error encountered: {error_message}"
        issue_body = (f"**User Message:** {ctx.message.content}\n"
                      f"**Error:** {error_message}\n"
                      f"**Traceback:** \n```python\n{traceback_str}\n```\n"
                      f"**Time:** {cet_time.strftime('%d-%m-%Y  -  %H:%M:%S')}\n"
                      f"**Command:** `{ctx.command.qualified_name}`\n"
                      f"**Author:** {ctx.author}\n"
                      f"**Channel:** {ctx.channel} ({channel_type})\n"
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