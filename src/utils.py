# Leah
# utils.py
# Written by aquova et al., 2022
# https://github.com/StardewValleyDiscord/leah

import discord
from discord.ext.commands import Context
from config import ROLES_CHAN, ADMIN_ROLE
from typing import Union, List


def format_roles_error(error: str, roles: List[str]) -> str:
    """
    :param error: Unformatted error message.
    :param roles: List of required roles to display in the error message.
    :return: Formatted error message.
    """
    return error.format(", ".join([f"<@&{role}>" for role in roles]), f"<#{ROLES_CHAN}>")

def check_roles(user: Union[discord.User, discord.Member], roles: List[discord.Role]) -> bool:
    """
    Check roles
    :param user: A user or member object, where a user that is not a member is ensured not to have any roles.
    :param roles: A list of role IDs to check for.
    :return: Whether a user has any of the roles in a given list.
    """
    return (isinstance(user, discord.Member)
            and len(roles) > 0 and len([r for r in user.roles if r.id in roles]) > 0)

def requires_admin(ctx: Context) -> bool:
    """
    Requires admin

    Command check for whether the author has an admin role.
    """
    return check_roles(ctx.message.author, [ADMIN_ROLE])
