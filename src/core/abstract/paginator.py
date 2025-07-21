"""
This project is licensed under the GNU GPL v3.0.
    :author: hunter87
    :Copyright: (C) 2022-present hunter87.dev@gmail.com
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
"""

import asyncio
from typing import List, Optional, Any, Union, Dict
from discord import Embed, SelectOption, Interaction, ButtonStyle, User, Member
from discord.ui import View, Button, Select
from discord.ext import commands
from ext import EmbedBuilder, color, emoji


class PageSelect(Select):
    """Dropdown select for page navigation"""
    
    def __init__(self, paginator: "Paginator"):
        self.paginator = paginator
        
        # Create options for each page
        options = []
        for i, page in enumerate(paginator.pages):
            # Use embed title if available, otherwise use page number
            label = f"Page {i + 1}"
            if isinstance(page, Embed) and page.title:
                label = page.title[:100]  # Discord limit for select option label
            elif hasattr(page, 'title') and page.title:
                label = page.title[:100]

            # Add description from embed if available
            description = ""
            if isinstance(page, Embed) and page.description:
                description = page.short_desc or page.description[:100]  # Discord limit for select option description
            
            options.append(SelectOption(
                label=label,
                description=description,
                value=str(i),
                emoji=getattr(page, 'emoji', None) or "📄"
            ))
        
        super().__init__(
            placeholder="Select a page...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: Interaction):
        """Handle page selection from dropdown"""
        if not await self.paginator._check_author(interaction):
            return
            
        page_index = int(self.values[0])
        await self.paginator._update_page(interaction, page_index)


class NavigationButton(Button):
    """Custom button for pagination navigation"""
    
    def __init__(self, action: str, paginator: "Paginator", **kwargs):
        self.action = action
        self.paginator = paginator
        super().__init__(**kwargs)
    
    async def callback(self, interaction: Interaction):
        """Handle button clicks"""
        if not await self.paginator._check_author(interaction):
            return
            
        current = self.paginator.current_page
        
        if self.action == "first":
            new_page = 0
        elif self.action == "previous":
            new_page = max(0, current - 1)
        elif self.action == "next":
            new_page = min(len(self.paginator.pages) - 1, current + 1)
        elif self.action == "last":
            new_page = len(self.paginator.pages) - 1
        elif self.action == "stop":
            await self.paginator.stop_paginator(interaction)
            return
        else:
            return
            
        await self.paginator._update_page(interaction, new_page)


class Paginator(View):
    """
    A custom paginator with dropdown view functionality for Discord embeds.
    
    Features:
    - Navigation buttons (first, previous, next, last, stop)
    - Dropdown select menu for quick page jumping
    - Author-only interaction control
    - Customizable timeout
    - Support for both Embed objects and dictionaries
    """
    
    def __init__(
        self,
        pages: List[Union[EmbedBuilder, Dict[str, Any]]],
        *,
        author: Union[User, Member],
        timeout: float = 180.0,
        show_buttons: bool = True,
        show_dropdown: bool = True,
        delete_on_timeout: bool = False
    ):
        """
        Initialize the paginator.
        
        Args:
            pages: List of embeds or embed dictionaries to paginate
            author: User who can interact with the paginator
            timeout: How long to wait before timing out (seconds)
            show_buttons: Whether to show navigation buttons
            show_dropdown: Whether to show page dropdown
            delete_on_timeout: Whether to delete the message on timeout
        """
        super().__init__(timeout=timeout)
        
        if not pages:
            raise ValueError("Pages list cannot be empty")
            
        self.pages = pages
        self.author = author
        self.current_page = 0
        self.show_buttons = show_buttons
        self.show_dropdown = show_dropdown
        self.delete_on_timeout = delete_on_timeout
        self.message = None
        
        # Only add components if we have multiple pages
        if len(self.pages) > 1:
            self._setup_components()
    
    def _setup_components(self):
        """Setup the UI components (buttons and dropdown)"""
        if self.show_buttons:
            # First page button
            self.add_item(NavigationButton(
                action="first",
                paginator=self,
                emoji="⏪",
                style=ButtonStyle.secondary,
                disabled=True
            ))
            
            # Previous page button
            self.add_item(NavigationButton(
                action="previous",
                paginator=self,
                emoji="◀️",
                style=ButtonStyle.primary,
                disabled=True
            ))
            
            # Stop button
            self.add_item(NavigationButton(
                action="stop",
                paginator=self,
                emoji="⏹️",
                style=ButtonStyle.danger
            ))
            
            # Next page button
            self.add_item(NavigationButton(
                action="next",
                paginator=self,
                emoji="▶️",
                style=ButtonStyle.primary,
                disabled=len(self.pages) <= 1
            ))
            
            # Last page button
            self.add_item(NavigationButton(
                action="last",
                paginator=self,
                emoji="⏩",
                style=ButtonStyle.secondary,
                disabled=len(self.pages) <= 1
            ))
        
        # Add dropdown if enabled and we have multiple pages
        if self.show_dropdown and len(self.pages) > 1:
            self.add_item(PageSelect(self))
    
    def _update_button_states(self):
        """Update button disabled states based on current page"""
        if not self.show_buttons:
            return
            
        for item in self.children:
            if isinstance(item, NavigationButton):
                if item.action == "first" or item.action == "previous":
                    item.disabled = (self.current_page == 0)
                elif item.action == "next" or item.action == "last":
                    item.disabled = (self.current_page == len(self.pages) - 1)
    
    async def _check_author(self, interaction: Interaction) -> bool:
        """Check if the interaction user is authorized"""
        if interaction.user.id != self.author.id:
            embed = EmbedBuilder.warning("You are not authorized to use this paginator.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True
    
    async def _update_page(self, interaction: Interaction, page_index: int):
        """Update to a specific page"""
        if 0 <= page_index < len(self.pages):
            self.current_page = page_index
            self._update_button_states()
            
            # Get the embed for the current page
            embed = self.get_current_embed()
            
            await interaction.response.edit_message(embed=embed, view=self)
    
    def get_current_embed(self) -> Embed:
        """Get the embed for the current page"""
        page = self.pages[self.current_page]
        
        if isinstance(page, Embed):
            embed = page
        elif isinstance(page, dict):
            embed = Embed.from_dict(page)
        else:
            # Fallback: create a basic embed
            embed = EmbedBuilder(description=str(page))
        
        # Add page indicator to footer if multiple pages
        if len(self.pages) > 1:
            footer_text = f"Page {self.current_page + 1}/{len(self.pages)}"
            if embed.footer.text:
                footer_text = f"{embed.footer.text} • {footer_text}"
            embed.set_footer(text=footer_text, icon_url=embed.footer.icon_url)
        
        return embed

    async def start(self, ctx: commands.Context, **kwargs) -> None:
        """Start the paginator by sending the initial message"""
        embed = self.get_current_embed()
        
        if len(self.pages) == 1:
            # Single page, just send without view
            self.message = await ctx.send(embed=embed, **kwargs)
        else:
            # Multiple pages, send with view
            self.message = await ctx.send(embed=embed, view=self, **kwargs)
    
    async def start_interaction(self, interaction: Interaction, **kwargs) -> None:
        """Start the paginator by responding to an interaction"""
        embed = self.get_current_embed()
        
        if len(self.pages) == 1:
            # Single page, just respond without view
            await interaction.response.send_message(embed=embed, **kwargs)
        else:
            # Multiple pages, respond with view
            await interaction.response.send_message(embed=embed, view=self, **kwargs)
            self.message = await interaction.original_response()
    
    async def stop_paginator(self, interaction: Interaction):
        """Stop the paginator and clean up"""
        self.stop()
        
        if self.delete_on_timeout and self.message:
            try:
                await self.message.delete()
            except:
                pass
        else:
            # Disable all components
            for item in self.children:
                item.disabled = True
            
            embed = self.get_current_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        """Handle view timeout"""
        if self.delete_on_timeout and self.message:
            try:
                await self.message.delete()
            except:
                pass
        elif self.message:
            # Disable all components
            for item in self.children:
                item.disabled = True
            
            try:
                embed = self.get_current_embed()
                await self.message.edit(embed=embed, view=self)
            except:
                pass


class EmbedPaginator(Paginator):
    """Convenience class specifically for embed pagination"""
    
    @classmethod
    def from_embeds(
        cls,
        embeds: List[Embed],
        *,
        author: Union[User, Member],
        **kwargs
    ) -> "EmbedPaginator":
        """Create paginator from a list of embeds"""
        return cls(embeds, author=author, **kwargs)
    
    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        *,
        author: Union[User, Member],
        title: str = None,
        color: int = color.cyan,
        **kwargs
    ) -> "EmbedPaginator":
        """Create paginator from a list of text strings"""
        embeds = []
        for i, text in enumerate(texts):
            embed_title = f"{title} - Page {i + 1}" if title else f"Page {i + 1}"
            embed = EmbedBuilder(title=embed_title, description=text, color=color)
            embeds.append(embed)
        
        return cls(embeds, author=author, **kwargs)
    
    @classmethod
    def from_fields(
        cls,
        fields: List[tuple],
        *,
        author: Union[User, Member],
        title: str = None,
        description: str = None,
        fields_per_page: int = 10,
        color: int = color.cyan,
        **kwargs
    ) -> "EmbedPaginator":
        """
        Create paginator from a list of field tuples.
        
        Args:
            fields: List of tuples (name, value, inline=False)
            fields_per_page: Number of fields per page
        """
        embeds = []
        
        for i in range(0, len(fields), fields_per_page):
            page_fields = fields[i:i + fields_per_page]
            page_num = (i // fields_per_page) + 1
            
            embed_title = f"{title} - Page {page_num}" if title else f"Page {page_num}"
            embed = EmbedBuilder(title=embed_title, description=description, color=color)
            
            for field in page_fields:
                if len(field) == 2:
                    name, value = field
                    inline = False
                elif len(field) == 3:
                    name, value, inline = field
                else:
                    continue
                
                embed.add_field(name=name, value=value, inline=inline)
            
            embeds.append(embed)
        
        return cls(embeds, author=author, **kwargs)


# Utility functions for quick paginator creation

async def paginate_embeds(
    ctx: commands.Context,
    embeds: List[Embed],
    **kwargs
) -> Paginator:
    """Quick function to paginate embeds"""
    paginator = EmbedPaginator.from_embeds(embeds, author=ctx.author, **kwargs)
    await paginator.start(ctx)
    return paginator


async def paginate_text(
    ctx: commands.Context,
    texts: List[str],
    title: str = None,
    **kwargs
) -> Paginator:
    """Quick function to paginate text"""
    paginator = EmbedPaginator.from_texts(texts, author=ctx.author, title=title, **kwargs)
    await paginator.start(ctx)
    return paginator


async def paginate_fields(
    ctx: commands.Context,
    fields: List[tuple],
    title: str = None,
    fields_per_page: int = 10,
    **kwargs
) -> Paginator:
    """Quick function to paginate fields"""
    paginator = EmbedPaginator.from_fields(
        fields,
        author=ctx.author,
        title=title,
        fields_per_page=fields_per_page,
        **kwargs
    )
    await paginator.start(ctx)
    return paginator
