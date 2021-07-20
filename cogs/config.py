from discord.ext import commands
import discord, typing, aiohttp
from discord import Webhook
from core import Parrot, Context, Cog

from database.server_config import collection as csc, guild_join, guild_update
from database.global_chat import collection as cgc, gchat_on_join, gchat_update
from database.mee6 import guild_join as ge_mee6, guild_remove as gr_mee6, insert_lvl_role, update_lvl_role, collection as cm6


class BotConfig(Cog, name="botconfig"):
    """To config the bot. In the server"""
    def __init__(self, bot: Parrot):
        self.bot = bot

    @commands.group()
    @commands.check_any(commands.has_permissions(administrator=True))
    @commands.bot_has_permissions(embed_links=True)
    async def config(self, ctx: Context):
        """
				To config the bot, mod role, prefix, or you can disable the commands and cogs.
				"""
        pass

    @config.command()
    @commands.check_any(commands.has_permissions(administrator=True))
    async def botprefix(self, ctx: Context, *, arg: commands.clean_content):
        """
				To set the prefix of the bot. Whatever prefix you passed, will be case sensitive. It is advised to keep a symbol as a prefix.
				"""
        if not csc.find_one({'_id': ctx.guild.id}):
            await guild_join(ctx.guild.id)
        if len(arg) > 6:
            return await ctx.reply(
                f"{ctx.author.mention} length of prefix can not be more than 6 characters."
            )
        post = {'prefix': arg}
        await guild_update(ctx.guild.id, post)

        await ctx.reply(
            f"{ctx.author.mention} success! Prefix for **{ctx.guild.name}** is **{arg}**."
        )

    @config.command(aliases=['mute-role'])
    @commands.check_any(commands.has_permissions(administrator=True))
    async def muterole(self, ctx: Context, *, role: discord.Role):
        """
				To set the mute role of the server. By default role with name `Muted` is consider as mute role.
				"""
        if not csc.find_one({'_id': ctx.guild.id}):
            await guild_join(ctx.guild.id)
        post = {'mute_role': role.id}
        await guild_update(ctx.guild.id, post)

        await ctx.reply(
            f"{ctx.author.mention} success! Mute role for **{ctx.guild.name}** is **{role.name} ({role.id})**"
        )

    @config.command(aliases=['mod-role'])
    @commands.check_any(commands.has_permissions(administrator=True))
    async def modrole(self, ctx: Context, *, role: discord.Role):
        """
				To set mod role of the server. People with mod role can accesss the Moderation power of Parrot. By default the mod functionality works on the basis of permission
				"""
        if not csc.find_one({'_id': ctx.guild.id}):
            await guild_join(ctx.guild.id)

        post = {'mod_role': role.id}
        await guild_update(ctx.guild.id, post)

        await ctx.reply(
            f"{ctx.author.mention} success! Mod role for **{ctx.guild.name}** is **{role.name} ({role.id})**"
        )

    @config.command(aliases=['giveaway-role'])
    @commands.check_any(commands.has_permissions(administrator=True))
    async def giveawayrole(self, ctx: Context, *, role: discord.Role):
        if not csc.find_one({'_id': ctx.guild.id}):
            await guild_join(ctx.guild.id)

        post = {'giveaway_role': role.id}
        await guild_update(ctx.guild.id, post)

        await ctx.reply(
            f"{ctx.author.mention} success! Giveaway role for **{ctx.guild.name}** is **{role.name} ({role.id})**"
        )

    @config.command(aliases=['action-log'])
    @commands.check_any(commands.has_permissions(administrator=True))
    async def actionlog(self,
                        ctx: Context,
                        *,
                        channel: discord.TextChannel = None):
        """
				To set the action log, basically the mod log.
				"""
        channel = channel or ctx.channel
        if not csc.find_one({'_id': ctx.guild.id}):
            await guild_join(ctx.guild.id)

        post = {'action_log': channel.id}
        await guild_update(ctx.guild.id, post)

        await ctx.reply(
            f"{ctx.author.mention} success! Action log for **{ctx.guild.name}** is **{channel.name} ({channel.id})**"
        )

    @config.command(name='mee6')
    @commands.check_any(commands.has_permissions(administrator=True))
    async def mee6(self,
                   ctx: Context,
                   settings: str,
                   level: int = None,
                   *,
                   role: discord.Role = None):
        if not cm6.find_one(ctx.guild.id):
            await ge_mee6(ctx.guild.id)

        if settings.lower() == 'removeall':
            await gr_mee6(ctx.guild.id)
            await ge_mee6(ctx.guild.id)
            return await ctx.send(f'{ctx.author.mention} removed all the level and its respective roles')
        
        if settings.lower() == 'addlvl':
            if not level and not role:
                return 
            else:
                await insert_lvl_role(ctx.guild.id, level, role.id)
        
        if settings.lower() == 'updlvl':
            if not level and not role:
                return
            else:
                await update_lvl_role(ctx.guild.id, level, role.id)

    @config.command(aliases=['g-setup'])
    @commands.check_any(commands.has_permissions(administrator=True))
    @commands.bot_has_permissions(manage_channels=True,
                                  manage_webhooks=True,
                                  manage_roles=True)
    async def gchatsetup(self,
                         ctx: Context,
                         setting: str = None,
                         *,
                         role: typing.Union[discord.Role]):
        """
				This command will connect your server with other servers which then connected to #global-chat must try this once
				"""
        if not cgc.find_one({'_id': ctx.guild.id}):
            await gchat_on_join(ctx.guild.id)

        if not setting:
            guild = ctx.guild
            overwrites = {
                guild.default_role:
                discord.PermissionOverwrite(read_messages=True,
                                            send_messages=True,
                                            read_message_history=True),
                guild.me:
                discord.PermissionOverwrite(read_messages=True,
                                            send_messages=True,
                                            read_message_history=True)
            }
            channel = await guild.create_text_channel(
                'global-chat',
                topic="Hmm. Please be calm, be very calm",
                overwrites=overwrites)

            webhook = await channel.create_webhook(name="GlobalChat",
                                                   avatar=await
                                                   ctx.me.avatar.url.read())

            post = {'chanel_id': channel.id, 'webhook': webhook.url}

            await gchat_update(guild.id, post)
            await ctx.send(f"{channel.mention} created successfully.")
            return

        if (setting.lower() in ['ignore-role', 'ignore_role', 'ignorerole'
                                ]) and (role is not None):
            post = {'ignore-role': role.id}
            await gchat_update(ctx.guild.id, post)
            await ctx.reply(
                f"{ctx.author.mention} success! **{role.name} ({role.id})** will be ignored from global chat!"
            )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def broadcast(self, ctx: Context, *, message: str):
        """
				To broadcast all over the global channel. Only for owners.
				"""
        data = cgc.find({})

        for webhooks in data:
            hook = webhooks['webhook']
            try:

                async def send_webhook():
                    async with aiohttp.ClientSession() as session:
                        webhook = Webhook.from_url(f"{hook}", adapter=session)

                        await webhook.send(
                            content=f"{message}",
                            username="SYSTEM",
                            avatar_url=f"{self.bot.guild.me.avatar.url}")

                await send_webhook()
            except:
                continue


def setup(bot):
    bot.add_cog(BotConfig(bot))
