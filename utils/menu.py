import discord

category_emojis = {
    "Profile": "🧍",
    "Utility": "🛠️",
    "Currency": "🪙",
    "Jishaku": "👨‍💻",
    "Homepage": "🏠",
    "Miscellaneous": "⭐"
}


class Menu(discord.ui.View):
    def __init__(self, ctx, source):
        self.selectMenu = None
        self.ctx = ctx
        self.help = source
        self.message = None
        self.mapping = None
        self.embed = None
        self.body = None
        self.current = None
        self.curPage = 0
        super().__init__(timeout=30.0)

    def cogName(self, cog):
        if cog is None:
            return "Miscellaneous"
        if isinstance(cog, discord.ext.commands.Cog):
            return cog.qualified_name
        return str(cog)

    def add_categories(self, mapping: dict, current: str = "Homepage"):
        self.mapping = mapping
        self.current = current
        self.selectMenu = HelpSelect()
        self.selectMenu.add_options(["Homepage"] + list(map(self.cogName, mapping.keys())), current)
        self.add_item(self.selectMenu)

    async def rebind(self, cog, interaction: discord.Interaction, name=None):
        self.selectMenu.add_options(["Homepage"] + list(map(self.cogName, self.help.get_bot_mapping().keys())), name)
        self.embed, self.body = self.help.get_cog_embed(cog, name) if cog else self.help.help_embed()
        await self.goto(0, interaction)

    async def goto(self, pagenum=0, interaction: discord.Interaction = None, edit=True):
        if interaction and interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("This is not your command!", ephemeral=True)
        self.embed.clear_fields()
        self.embed.add_field(name=f"Page {pagenum + 1}/{len(self.body.pages)}", value=self.body.pages[pagenum],
                             inline=True)
        for child in self.children:
            if child.custom_id in ["btnBack", "btnPrev"]:
                child.disabled = pagenum == 0
            if child.custom_id in ["btnNext", "btnForward"]:
                child.disabled = pagenum == len(self.body.pages) - 1

        self.curPage = pagenum
        if edit:
            if interaction.response:
                await interaction.response.edit_message(embed=self.embed, view=self)
            else:
                await self.message.edit(embed=self.embed, view=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.gray, row=1, custom_id="btnBack")
    async def leftBtnCallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.goto(0, interaction)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, row=1, custom_id="btnPrev")
    async def prevBtnCallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.goto(self.curPage - 1, interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, row=1, custom_id="btnNext")
    async def nextBtnCallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.goto(self.curPage + 1, interaction)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.gray, row=1, custom_id="btnForward")
    async def rightBtnCallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.goto(max(len(self.body.pages) - 1, 0), interaction)

    @discord.ui.button(label="Quit", style=discord.ButtonStyle.red, row=1)
    async def quitBtnCallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.on_timeout()
        self.stop()

    async def on_timeout(self) -> None:
        self.clear_items()
        # THANK YOU ilovetocode#9113
        await self.message.edit(view=self)


class HelpSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="What category do you want to check out?", row=0)

    def add_options(self, subjects, default):
        self.options = [
            discord.SelectOption(
                label=subject,
                value=subject,
                default=(subject == default),
                emoji=category_emojis[subject])
            for subject in subjects
        ]

    async def callback(self, interaction):
        if self.values[0] == "Homepage":
            await self.view.rebind(None, interaction, "Homepage")
        elif self.values[0] == "Miscellaneous":
            await self.view.rebind(self.view.help.get_bot_mapping()[None], interaction, "Miscellaneous")
        else:
            await self.view.rebind(self.view.ctx.bot.get_cog(self.values[0]), interaction, self.values[0])