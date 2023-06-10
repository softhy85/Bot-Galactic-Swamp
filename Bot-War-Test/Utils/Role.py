import discord

class Role:
    @staticmethod
    def admin_role(guild: discord.Guild, user: discord.User | discord.Member) -> bool:
        role : discord.Role = discord.utils.get(guild.roles, name="Admin")
        if role in user.roles:
            return True
        return False

    @staticmethod
    def assistant_role(guild: discord.Guild, user: discord.User | discord.Member) -> bool:
        admin_role : discord.Role = discord.utils.get(guild.roles, name="Admin")
        assistant_role : discord.Role = discord.utils.get(guild.roles, name="Assistant")
        if admin_role in user.roles:
            return True
        if assistant_role in user.roles:
            return True
        return False