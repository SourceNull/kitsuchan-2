#!/usr/bin/env python3

from discord.ext import commands


class Help:
    """Help command."""

    @commands.command(aliases=["commands"])
    @commands.cooldown(1, 2)
    async def help(self, ctx, *cmds: str):
        """Help command.

        * command_or_cog - The name of a command or cog.
        """
        if not cmds:
            commands_list = []
            for command in ctx.bot.commands:
                if command.hidden:
                    continue
                try:
                    can_run = await command.can_run(ctx)
                except Exception:
                    continue
                if can_run:
                    commands_list.append(command.name)
            commands_list.sort()
            help_text = f'```{", ".join(commands_list)}```'
            help_text += f"\nRun **help command** for more details on a command."
            help_text = "**List of commands:**\n" + help_text
            await ctx.send(help_text)
        else:
            # This is awful, haha
            await ctx.bot.all_commands["old_help"].callback(ctx, *cmds)


def setup(bot):
    """Set up the extension."""
    try:
        help_command = bot.all_commands["help"]
        help_command.hidden = True
        help_command.name = "old_help"
        bot.remove_command("help")
        bot.add_command(help_command)
    except KeyError:  # This means the setup already did its thing.
        pass
    bot.add_cog(Help())
