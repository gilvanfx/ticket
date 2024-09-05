import discord
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Lista para armazenar canais de chamados
active_tickets = {}

# ID da categoria onde os canais de chamados serão criados (Substitua pelo ID da categoria)
CATEGORY_ID = 1281299670349648024  # Coloque o ID da sua categoria aqui

class TicketButton(Button):
    def __init__(self):
        super().__init__(label="Abrir Chamado", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        author = interaction.user

        # Verifica se o usuário já tem um chamado aberto
        if author.id in active_tickets:
            await interaction.response.send_message("Você já tem um chamado aberto!", ephemeral=True)
            return

        # Buscar a categoria onde os canais serão criados
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
        if not category:
            await interaction.response.send_message("Categoria não encontrada!", ephemeral=True)
            return

        # Criar um canal dentro da categoria específica
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            discord.utils.get(guild.roles, name="Moderador"): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await category.create_text_channel(f"chamado-{author.name}", overwrites=overwrites)

        # Armazena o canal na lista de chamados ativos
        active_tickets[author.id] = ticket_channel.id

        await interaction.response.send_message(f"Seu chamado foi aberto: {ticket_channel.mention}", ephemeral=True)

        # Enviar botão de fechar dentro do canal criado
        close_button = Button(label="Fechar Chamado", style=discord.ButtonStyle.red)
        close_view = View()
        close_view.add_item(close_button)

        async def close_callback(interaction: discord.Interaction):
            if interaction.user.id == author.id or discord.utils.get(guild.roles, name="Moderador") in interaction.user.roles:
                await ticket_channel.delete()
                del active_tickets[author.id]
            else:
                await interaction.response.send_message("Apenas o autor ou moderadores podem fechar o chamado.", ephemeral=True)

        close_button.callback = close_callback

        await ticket_channel.send(f"{author.mention} abriu um chamado.", view=close_view)

@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")

@bot.command(name="ticket")
async def ticket(ctx):
    # Envia o botão de abrir chamado no canal
    view = View()
    view.add_item(TicketButton())
    await ctx.send("Clique no botão para abrir um chamado:", view=view)

bot.run("MTI4MTI5NjIzMTk1NTQzNTU2MA.GTnSTj.Fod7jQRgPel8huNTUSxwc3uYG3rFkC0oqhWX9w")
