# custom help utility from command description with pagination

import discord
from typing import TYPE_CHECKING, Mapping, List
from .abstract import Cog
from .abstract import EmbedPaginator
from ext import EmbedBuilder
from discord.ext import commands
from discord import app_commands

if TYPE_CHECKING:
    from core.bot import Spruce
    from core.abstract import Cog

class HelpCommand(commands.HelpCommand):
    def __init__(self) -> None:
        super().__init__(
            verify_checks=False,
            command_attrs={
                "cooldown": commands.CooldownMapping.from_cooldown(1, 8.0, commands.BucketType.member),
                "help": "Shows help about the bot, a command, or a category",
            },
        )

    async def send_bot_help(self, mapping: Mapping[Cog, List[commands.Command]]):
            ctx = self.context

            hidden = ("HelpCog", "DevCog")

            embeds: list[EmbedBuilder] = [ ]

            server = f"[Support Server](https://dsc.gg/spruce)"
            invite = f"[Invite Me](https://dsc.gg/sprucebot)"
            dashboard = f"[Privacy Policy](https://sprucebot.tech/privacy) | [Terms of Service](https://sprucebot.tech/terms)"
            main_menu = EmbedBuilder(
                    title="Main Menu",
                    description=f"{server} **|** {invite} **|** {dashboard}\n\n",
                    emoji="ℹ️",
                )
            
            embeds.append(main_menu)
            cog : "Cog"

            for cog, commands in mapping.items():
                
                cog_emoji = getattr(cog, 'emoji', None) or ""
                cog_name = cog.qualified_name.title() if cog else "General Commands"
                main_menu.add_field(name=f"{cog_emoji}{cog_name}", value="", inline=False)

                embed = EmbedBuilder(
                    title=cog.qualified_name.title() if cog else "General Commands"
                )

                if cog and cog.qualified_name not in hidden:
                    _app_commands = cog.get_app_commands()

                    if _app_commands:
                        embed.add_field(
                            name="Application Commands",
                            value=", ".join(map(lambda x: f"`{x}`", _app_commands)),
                            inline=False,
                        )

                    embed.add_field(
                        inline=False,
                        name=cog.qualified_name.title(),
                        value=", ".join(map(lambda x: f"`{x}`", commands or []))
                    )
                    embeds.append(embed)

            _paginator = EmbedPaginator(pages=embeds, author=ctx.author, delete_on_timeout=True)
            await _paginator.start(ctx)
