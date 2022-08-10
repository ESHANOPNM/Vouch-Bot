from disnake.ext.commands import Cog
from lib.db import db
VIEW_NAME = "RoleView"

class Events(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('Events')

    @Cog.listener()
    async def on_member_update(self, before, after):
        staff_id = db.field("SELECT StaffRole FROM guild", after.guild.id)
        staff = after.guild.get_role(staff_id)
        if before.roles != after.roles:
            if staff in after.roles:
                db.execute("INSERT OR IGNORE INTO vouches (UserID, Vouches) VALUES (?, ?)", after.id, 0)
                db.commit()

    @Cog.listener()
    async def on_message(self, message):
        cID = db.field(
            "SELECT VouchChannel FROM guild")
        if message.channel.id != cID:
            return

        if message.author.bot == True:
            return
        else:
            await message.delete()
            await message.channel.send("Please use /vouch @user `reason` to give a user a vouch.", delete_after=5)

def setup(bot):
    bot.add_cog(Events(bot))
