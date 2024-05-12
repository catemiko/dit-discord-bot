import logging
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context

from database.db import DatabaseClient
import exceptions


class Bot(commands.Bot):
    def __init__(
        self, database: DatabaseClient, intents=discord.Intents.all(), **kwargs
    ):
        commands.Bot.__init__(self, intents=discord.Intents.all(), **kwargs)
        self.database = database
        self.add_commands()

    async def on_ready(self):
        logger.info("Bot is ready")

    def add_commands(self):
        @self.hybrid_group(name="role", help="Manage roles")
        async def _role(ctx: Context):
            pass

        @_role.command(name="table", help="Print all roles")
        async def _role_list_all(ctx: Context):
            guild = self.database.create_guild(ctx.guild.id)
            roles = self.database.list_all_roles(guild)
            await ctx.channel.send(f"All roles: {[role.name for role in roles]}")

        @_role.command(name="create", help="Create role")
        async def _role_create(ctx: Context, name: str):
            guild = self.database.create_guild(ctx.guild.id)
            role = self.database.create_role(guild, name)
            if role is None:
                raise exceptions.RoleNotFound()
            await ctx.channel.send(f"Created role '{role.name}'!")

        @_role.command(name="delete", help="Delete role")
        async def _role_delete(ctx: Context, role_name: str):
            guild = self.database.create_guild(ctx.guild.id)
            role = self.database.get_role(guild, role_name)
            if role is None:
                raise exceptions.RoleNotFound()
            self.database.delete_role(role)
            await ctx.channel.send(f"Deleted role '{role.name}'!")

        @_role.command(name="assign", help="Assign role to user")
        async def _role_assign(ctx: Context, member: discord.Member, role_name: str):
            guild = self.database.create_guild(ctx.guild.id)
            role = self.database.get_role(guild, role_name)
            if role is None:
                raise exceptions.RoleNotFound()
            user = self.database.create_user(member.id)
            if role in user.roles:
                raise exceptions.RoleAlreadyAssigned()
            self.database.assign_role(user, role)
            await ctx.channel.send(
                f"Assigned role '{role.name}' to user {member.mention}!"
            )

        @_role.command(name="unassign", help="Unassign role from user")
        async def _role_unassign(ctx: Context, member: discord.Member, role_name: str):
            guild = self.database.create_guild(ctx.guild.id)
            role = self.database.get_role(guild, role_name)
            if role is None:
                raise exceptions.RoleNotFound()
            user = self.database.create_user(member.id)
            if role not in user.roles:
                raise exceptions.RoleAlreadyUnassigned()
            self.database.unassign_role(user, role)
            await ctx.channel.send(
                f"Unassigned role '{role.name}' from user {member.mention}!"
            )

        @_role.command(name="list", help="List roles for user")
        async def _role_list(ctx: Context, member: discord.Member):
            guild = self.database.create_guild(ctx.guild.id)
            user = self.database.create_user(member.id)
            roles = self.database.list_user_roles(guild, user)
            await ctx.channel.send(
                f"Roles for user {member.mention}: {[role.name for role in roles]}"
            )

        @_role_create.error
        @_role_delete.error
        async def _role_error(ctx: Context, error: commands.CommandError):
            match type(error):
                case commands.CommandInvokeError:
                    match type(error.original):
                        case exceptions.RoleNotFound:
                            await ctx.send("Role not found!")
                case commands.MissingRequiredArgument:
                    await ctx.send("Missing arguments [role]!")
                case commands.MemberNotFound:
                    await ctx.send("Can't find such role!")
                case _:
                    await ctx.send("Unknown error!")

        @_role_assign.error
        @_role_unassign.error
        @_role_list.error
        async def _role_user_error(ctx: Context, error: commands.CommandError):
            match type(error):
                case commands.CommandInvokeError:
                    match type(error.original):
                        case exceptions.RoleNotFound:
                            await ctx.send("Role not found!")
                        case exceptions.RoleAlreadyAssigned:
                            await ctx.send("Role had been unassigned already!")
                        case exceptions.RoleAlreadyUnassigned:
                            await ctx.send("Role had been assigned already!")
                case commands.MissingRequiredArgument:
                    await ctx.send("Missing arguments [user, role]!")
                case commands.MemberNotFound:
                    await ctx.send("Can't find such user!")
                case _:
                    await ctx.send("Unknown error!")
