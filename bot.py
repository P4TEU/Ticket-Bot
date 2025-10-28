import discord
from discord.ext import commands
from discord import ui
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SUPPORT_ROLE_ID = int(os.getenv('SUPPORT_ROLE_ID', 0))
TICKET_CATEGORY_NAME = os.getenv('TICKET_CATEGORY_NAME', 'Tickets')
TICKET_PREFIX = 'ticket-'

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Commandă simplă pentru postare mesaj ticket
@bot.command()
async def setup_ticket(ctx):
    class TicketView(ui.View):
        @ui.button(label='Deschide ticket', style=discord.ButtonStyle.primary)
        async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
            # creează canal simplu
            category = discord.utils.get(ctx.guild.categories, name=TICKET_CATEGORY_NAME)
            if not category:
                category = await ctx.guild.create_category(TICKET_CATEGORY_NAME)
            safe_name = f"{TICKET_PREFIX}{interaction.user.name.lower()}"
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True)
            }
            if SUPPORT_ROLE_ID:
                role = ctx.guild.get_role(SUPPORT_ROLE_ID)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True)
            channel = await ctx.guild.create_text_channel(safe_name, category=category, overwrites=overwrites)
            await channel.send(f"{interaction.user.mention} Ticket creat! Apasă butonul de mai jos pentru a închide.", view=CloseView(channel))
            await interaction.response.send_message(f'Ticket creat: {channel.mention}', ephemeral=True)

    class CloseView(ui.View):
        def __init__(self, channel):
            super().__init__()
            self.channel = channel

        @ui.button(label='Închide ticket', style=discord.ButtonStyle.danger)
        async def close(self, interaction: discord.Interaction, button: ui.Button):
            await self.channel.delete()

    await ctx.send("Apasă butonul pentru a crea un ticket.", view=TicketView())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
