import os
import json
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from main import bot, logger_info, logger_error, is_user_banned, why_is_user_banned , ban_user, unban_user

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @nextcord.slash_command(name="sync", description="Syncs all available slash commands", guild_ids=[1089971424367755345])
    async def sync(self, i: Interaction):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        
        await i.response.defer()
        try:
            await bot.sync_all_application_commands()
            await i.edit_original_message(content="Synced all slash commands")
            logger_info.info("Successfully syncronized all slash commands")
        except Exception as e:
            await i.edit_original_message(content=f"Something weird happened while syncing: {e}")
            logger_error.error(f"Something weird happened while syncronizing all commands: {e}")


        

    @nextcord.slash_command(name="reloadall", description="Reload all cogs", guild_ids=[1089971424367755345])
    async def reload_all_cogs(self, i: Interaction):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        try:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    bot.reload_extension(f'cogs.{filename[:-3]}')
                    print(f"Reloaded {filename}")
            await i.send(f"Reloaded {len(bot.cogs)} cogs", ephemeral=True)
        except Exception as e:
            await i.response.send_message(f"Failed to reload all cogs: {e}", ephemeral=False)


    @nextcord.slash_command(name="loadall", description="Load all cogs", guild_ids=[1089971424367755345])
    async def load_all_cogs(self, i: Interaction):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        
        try:
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f"Loaded {filename}")
            await i.send(f"Loaded {len(bot.cogs)} cogs", ephemeral=True)
        except Exception as e:
            await i.response.send_message(f"Failed to load all cogs: {e}", ephemeral=False)




    @nextcord.slash_command(name="reload", description="Reload a cog", guild_ids=[1089971424367755345])
    async def reload_cog(self, i: Interaction, cog: str = SlashOption(description="Cog to reload", required=True, choices=sorted([cog[:-3] for cog in os.listdir('./cogs') if cog.endswith('.py')]))):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        
        try:
            self.bot.reload_extension(f'cogs.{cog}')
            await i.response.send_message(f"Reloaded cog `{cog}`", ephemeral=True)
        except Exception as e:
            await i.response.send_message(f"Failed to reload cog `{cog}`: {e}", ephemeral=False)




    @nextcord.slash_command(name="unload", description="Unload a cog", guild_ids=[1089971424367755345])
    async def unload_cog(self, i: Interaction, cog: str = SlashOption(description="Cog to unload", required=True, choices=[cog[:-3] for cog in os.listdir('./cogs') if cog.endswith('.py')])):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        
        try:
            bot.unload_extension(f'cogs.{cog}')
            await i.response.send_message(f"Unloaded cog `{cog}`", ephemeral=True)
        except Exception as e:
            await i.response.send_message(f"Failed to unload cog `{cog}`: {e}", ephemeral=False)
            



    @nextcord.slash_command(name="load", description="Load a cog", guild_ids=[1089971424367755345])
    async def load_cog(self, i: Interaction, cog: str = SlashOption(description="Cog to load", required=True, choices=[cog[:-3] for cog in os.listdir('./cogs') if cog.endswith('.py')])):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        
        try:
            bot.load_extension(f'cogs.{cog}')
            await i.response.send_message(f"Loaded cog `{cog}`", ephemeral=True)
        except Exception as e:
            await i.response.send_message(f"Failed to load cog `{cog}`: {e}", ephemeral=False)
            



    @nextcord.slash_command(name="getservers", description="Get all servers the bot is in", guild_ids=[1089971424367755345])
    async def get_servers(self, i: Interaction):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        
        servers = [f"{guild.id} - {guild.name}" for guild in bot.guilds if guild.id not in [1089971424367755345, 1128726543779246180 ]]
        if len("\n".join(servers)) > 1500:
            with open("servers.txt", "w") as f:
                f.write("\n".join(servers))
            await i.response.send_message(file=nextcord.File("servers.txt"), ephemeral=False)
            os.remove("servers.txt")
        else:
            await i.response.send_message(f"```json\n{json.dumps(servers, indent=4)}```", ephemeral=False)



    @nextcord.slash_command(name="stats", description="Get some statistics about the bot", guild_ids=[1089971424367755345])
    async def stats(self, i: Interaction):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        await i.response.defer()
        # create stats embed
        stats = nextcord.Embed(title=f'Statistics about HeyPi', color=0x418a2f)
        stats.add_field(
            name=" ",
            value=f"> Servers: `{len(bot.guilds)}`\n> Commands: `{len(bot.commands)}`",
        )
        await i.edit_original_message(embed=stats)


    # shard status
    @nextcord.slash_command(name="shard", description="Get shard status", guild_ids=[1089971424367755345])
    async def getshard(self, i: Interaction):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        await i.response.defer()
        # create stats embed
        stats = nextcord.Embed(title=f'Shard Status', color=0x418a2f)
        stats.add_field(
            name=" ",
            value=f"> Shard ID: `{bot.shard_id}`\n> Shard Count: `{bot.shard_count}`",
        )
        await i.edit_original_message(embed=stats)



    @nextcord.slash_command(name="ban", description="Ban a user from chatting with Pi", guild_ids=[1089971424367755345])
    async def ban(self, i: Interaction, user: nextcord.User = SlashOption(description="User to ban", required=True), reason: str = SlashOption(description="Reason for banning", required=True)):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        # check if the user is already in the banned_users.db
        banned = await is_user_banned(user.id)
        if banned:
            await i.response.send_message(f"{user.mention} is already banned", ephemeral=False)
            return
        # add the user to the banned_users.db
        try:
            await ban_user(user.id, reason)
            await i.response.send_message(f"{user.mention} is now banned", ephemeral=False)
        except Exception as e:
            await i.response.send_message(f"Failed to ban {user.mention}: {e}", ephemeral=False)

    
    @nextcord.slash_command(name="unban", description="Unban a user from using the chat commands", guild_ids=[1089971424367755345])
    async def unban(self, i: Interaction, user: nextcord.User = SlashOption(description="User to unban", required=True)):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        # check if the user is already in the banned_users.db
        banned = await is_user_banned(user.id)
        if not banned:
            await i.response.send_message(f"{user.mention} is not banned", ephemeral=False)
            return
        # remove the user from the banned_users.db
        try:
            await unban_user(user.id)
            await i.response.send_message(f"{user.mention} is now unbanned", ephemeral=False)
        except Exception as e:
            await i.response.send_message(f"Failed to unban {user.mention}: {e}", ephemeral=False)

    
    @nextcord.slash_command(name="whyisbanned", description="Get the reason why a user is banned", guild_ids=[1089971424367755345])
    async def why_is_banned(self, i: Interaction, user: nextcord.User = SlashOption(description="User to check", required=True)):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        # check if the user is already in the banned_users.db
        banned = await is_user_banned(user.id)
        if not banned:
            await i.response.send_message(f"{user.mention} is not banned", ephemeral=False)
            return
        # get the reason why the user is banned
        try:
            reason = await why_is_user_banned(user.id)
            await i.response.send_message(f"{user.mention} is banned because: {reason}", ephemeral=False)
        except Exception as e:
            await i.response.send_message(f"Failed to get the reason why {user.mention} is banned: {e}", ephemeral=False)

    
    
    @nextcord.slash_command(name="getmutualservers", description="Gets mutual servers of a user", guild_ids=[1089971424367755345])
    async def servers(self, i: Interaction, user: nextcord.User = SlashOption(description="User to get mutual servers with", required=True)):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        await i.send("Disabled until I apply and get approved for the server members intent")
        # await i.response.defer()
        # mutual_servers = [guild.name for guild in bot.guilds if guild.get_member(user.id)]
        # await i.followup.send(f"Mutual servers with {user.mention}:\n```\n{', '.join(mutual_servers)}```", ephemeral=True)


    
    @nextcord.slash_command(name="getcommunityservers", description="Get all community servers the bot is in", guild_ids=[1089971424367755345])
    async def get_community_servers(self, interaction: Interaction):
        if interaction.user.id != 399668151475765258:
            await interaction.send("You're not allowed to run this command", ephemeral=True)
            return
        
        servers = [f"{guild.id} - {guild.name}" for guild in bot.guilds if guild.id == 1128726543779246180]
        if len("\n".join(servers)) > 1500:
            with open("community_servers.txt", "w") as f:
                f.write("\n".join(servers))
            await interaction.response.send_message(file=nextcord.File("community_servers.txt"), ephemeral=False)
            os.remove("community_servers.txt")
        else:
            await interaction.response.send_message(f"```json\n{json.dumps(servers, indent=4)}```", ephemeral=False)

    # server info command
    @nextcord.slash_command(name="serverinfo", description="Get information about the server", guild_ids=[1089971424367755345])
    async def server_info(self, i: Interaction, guild_id: str = SlashOption(description="Server ID", required=False)):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        if guild_id:
            guild = bot.get_guild(int(guild_id))  # Convert string back to int when fetching guild
        else:
            guild = i.guild
        if not guild:
            await i.send("I'm not in that server", ephemeral=True)
            return

        # create server info embed
        server_info = nextcord.Embed(title='Server Info', color=0x418a2f)
        server_info.add_field(
            name=" ",
            value=f"> Name: `{guild.name}`\n> ID: `{guild.id}`\n> Owner: <@{guild.owner_id}>\n> Members: `{guild.member_count}`\n> Created at: `{guild.created_at.strftime('%d/%m/%Y %H:%M:%S')}`\n> Is community server: `{guild.features}`",
        )

        # Add guild features
        features = "\n".join([f"> {feature.replace('_', ' ').title()}" for feature in guild.features])
        server_info.add_field(name="Features", value=features if features else "No special features", inline=False)

        await i.send(embed=server_info, ephemeral=False)


    @nextcord.slash_command(name="messageinfo", description="Get information about a message", guild_ids=[1089971424367755345])
    async def message_info(self, i: Interaction, message_id: str = SlashOption(description="Message ID", required=True)):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return

        message = None
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                try:
                    message = await channel.fetch_message(message_id)
                    if message:
                        break
                except nextcord.NotFound:
                    continue
            if message:
                break

        if not message:
            await i.send("Message not found", ephemeral=True)
            return

        # create message info embed
        message_info = nextcord.Embed(title='Message Info', color=0x418a2f)
        message_info.add_field(
            name=" ",
            value=f"> Content: {message.content}\n> Author: {message.author.mention}\n> Server: {message.guild}\n> Channel: {message.channel.mention}\n> Created at: {message.created_at.strftime('%d/%m/%Y %H:%M:%S')}",
        )

        await i.send(embed=message_info, ephemeral=False)


    @nextcord.slash_command(name="error", description="Raise an error", guild_ids=[1089971424367755345])
    async def error(self, i: Interaction):
        if i.user.id != 399668151475765258:
            await i.send("You're not allowed to run this command", ephemeral=True)
            return
        try:
            # try an impossible division
            1 / 0
        except Exception as e:
            await i.send(f"Division by 0. xd", ephemeral=True)
            raise e


def setup(bot):
    bot.add_cog(Admin(bot))
