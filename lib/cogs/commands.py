from typing import Optional
import typing
import disnake

from disnake.ext.commands import Cog, has_permissions, Param
from disnake.ext.commands.slash_core import slash_command
from lib.db import db


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('Commands')

    @slash_command(name="setup")
    @has_permissions(manage_guild=True)
    async def vouches_setup(self, inter, role: disnake.Role,  channel: Optional[disnake.TextChannel] = None):
        """Use this command to get started! If you don't tag a channel, one will be created
        
        Parameters
        ----------
        role: Role that users need to have in order to receive a vouch
        channel: Channel where users vouches will be sent to.
        """
        if channel is None:
            channel = await inter.guild.create_text_channel(name="🤞︱staff-feedback")

        db.execute("UPDATE guild SET VouchChannel = ?, StaffRole = ?",
                   channel.id, role.id)

        db.commit()
        await inter.send("Setup is now complete, Users can now use `/vouch @user` to give a staff member a vouch.", ephemeral=True)

    @slash_command(name="vouch")
    async def vouch(self, inter, reason: str, member: typing.Optional[disnake.Member] = None):
        """Add a vouch for a member, you must provide a valid reason."""
        staff = inter.guild.get_role(db.field("SELECT StaffRole FROM guild"))

        if staff not in member.roles:
            await inter.send(f"The member must have the {staff.mention} role to be vouched.", ephemeral=True)
            return
        
        words = reason.split()
        word_len = sum(len(word) for word in words)

        if word_len < 5:
            await inter.send("Length of reason is too short.", ephemeral=True)
            return

        if member is inter.author:
            await inter.send("You can't vouch yourself.", ephemeral=True)
            return

        else:
            channel_id = db.field("SELECT VouchChannel FROM guild")
            channel = self.bot.get_channel(channel_id)
            db.execute(
                    "UPDATE vouches SET Vouches = Vouches + ? WHERE UserID = ?", 1, member.id)

            vouches = db.field(
                "SELECT Vouches FROM vouches WHERE UserID = ?", member.id)


            if inter.guild.icon is None:
                icon = "https://cdn.discordapp.com/embed/avatars/0.png"


            else:
                icon = inter.guild.icon.url
            
            if member is None:
                embed = disnake.Embed(descriptions= "New Vouch!", colour=member.colour)

            else:    
                embed = disnake.Embed(description=f'{member.mention} has been vouched for by {inter.author.mention}.',
                          colour=member.colour)

            embed.add_field(name="Reason:", value=reason)
            embed.add_field(name="Vouches:", value=vouches)
            embed.set_author(name='Vouch Notification',
                             icon_url=icon)
            embed.set_thumbnail(url=member.avatar.url)
            await channel.send(embed=embed)
            await inter.send(f"Vouch has been added for {member}", ephemeral=True)
        db.commit()

    @slash_command(name="vouches")
    async def user_vouches(self, inter, member: Optional[disnake.Member] = None):
        """Show the amount of vouches a member has."""
        if member is None:
            member = inter.author

        channel = self.bot.get_channel(db.field(
            "SELECT VouchChannel FROM guild"))

        vouches = db.field(
            "SELECT Vouches FROM vouches WHERE UserID = ?", member.id)

        if inter.guild.icon is None:
            icon = "https://cdn.discordapp.com/embed/avatars/0.png"
        else:
            icon = inter.guild.icon.url

        embed = disnake.Embed(description=f'{member.mention} has {vouches} vouches',
                      colour=member.colour)
        embed.set_author(name='Vouch Stats',
                         icon_url=icon)
        embed.set_thumbnail(url=member.avatar.url)

        await channel.send(embed=embed)

        await inter.send(f"Vouch stats for {member} sent to <#{channel.id}>.", ephemeral=True)

    @slash_command(name="settings")
    @has_permissions(manage_guild=True)
    async def settings(self, inter):
        """Change the settings for the bot."""
        pass

    
    @settings.sub_command(name="reset")
    @has_permissions(manage_guild=True)
    async def user_reset(self, inter, member: disnake.Member, reason: str = None):
        """
        Reset the vouches of a member.
        """
        db.execute("UPDATE vouch SET Vouches = 0 WHERE UserID = ?", member.id)\

        channel = self.bot.get_channel(
            db.field("SELECT VouchChannel FROM guild"))

        await channel.send(f"Vouches have been reset to 0 for {member.mention} by {inter.author.mention} for `{reason}`.")
        await inter.send(f"Vouches have been reset to 0 for {member}.", ephemeral=True)

    @settings.sub_command(name="sync")
    @has_permissions(manage_guild=True)
    async def sync(self, inter):
        """Sync members to the database"""
        await inter.response.defer(with_message=True, ephemeral=True)
        staff_id = db.field("SELECT StaffRole FROM guild")
        staff = inter.guild.get_role(staff_id)

        if staff is None:
            await inter.send("You must set a staff role first.", ephemeral=True)
            return

        for member in inter.guild.members:
            if staff in member.roles:
                db.execute("INSERT INTO vouches (UserID, Vouches) VALUES (?, ?)", member.id, 0)
        db.commit()
        await inter.edit_original_message(content="Members synced to database")

    @slash_command(name="stats")
    async def stats(self, inter):
        """
        Show the bot's stats.
        """
        embed = disnake.Embed(colour=disnake.Colour.blue())
        embed.add_field(name="Servers", value=len(
            self.bot.guilds), inline=True)
        embed.add_field(name="Members", value=len(self.bot.users), inline=True)

        embed.set_author(name="Vanity Stats", icon_url=inter.guild.icon.url)
        embed.set_thumbnail(url=inter.guild.icon.url)
        embed.set_footer(
            text='Jay Development • discord.gg/jdev')

        await inter.send(embed=embed)


def setup(bot):
    bot.add_cog(Commands(bot))
