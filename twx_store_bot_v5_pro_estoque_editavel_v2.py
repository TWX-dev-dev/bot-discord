import asyncio
import io
import json
import os
import random
import re
import unicodedata
from pathlib import Path
from typing import Optional

import discord
import qrcode
from discord import app_commands
from discord.ext import commands

# =========================
# CONFIGURAÇÃO BASE
# =========================
# Segurança: defina o token em variável de ambiente DISCORD_BOT_TOKEN
TOKEN = os.getenv("TOKEN")

GUILD_ID = 1358235999783620771
CATEGORY_TICKETS_ID = 1399236036965568573
CANAL_PAINEL_ID = 1398490374103629996
CANAL_LOGS_ID = 1492745296843641003
CARGO_CLIENTE_ID = 1399977908105252984
CARGO_ADMIN_ID = 1367990975133122581

ARQUIVO_JSON = Path("twx_store_data_v5.json")
COR_PADRAO = 0x7C3AED
COR_SUCESSO = 0x22C55E
COR_ALERTA = 0xF59E0B
COR_ERRO = 0xEF4444
COR_INFO = 0x3B82F6

DEFAULT_BANNER_ONLINE = "https://uploadimagem.com//uploads/img_69dd3eb3300ef.png"
DEFAULT_LOGO = ""
NOME_PADRAO_LOJA = "TWX STORE"
MOEDA_PADRAO = "R$"
MERCHANT_NAME = "TWX STORE"
MERCHANT_CITY = "ARACAJU"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# =========================
# UTILITÁRIOS
# =========================
def default_data() -> dict:
    return {
        "painel": {
            "titulo": NOME_PADRAO_LOJA,
            "status": "online",
            "mensagem_offline": "Loja offline no momento. Volte mais tarde.",
            "cor": COR_PADRAO,
            "banner_online_url": DEFAULT_BANNER_ONLINE,
            "banner_offline_url": "",
            "thumbnail_url": DEFAULT_LOGO,
            "mostrar_calc_no_painel": True,
            "mostrar_resumo_estoque": True,
            "mensagem_boas_vindas": "Escolha uma categoria abaixo para abrir seu atendimento.",
        },
        "pix": {
            "tipo": "aleatoria",
            "chave": "86c32427-7746-4507-ba21-31f8a1139411",
            "beneficiario": MERCHANT_NAME,
            "cidade": MERCHANT_CITY,
            "descricao": "Pagamento Pix",
            "mostrar_chave_no_painel": False,
        },
        "loja": {
            "nome": NOME_PADRAO_LOJA,
            "moeda": MOEDA_PADRAO,
        },
        "categorias": {
            "contas": {
                "nome": "CONTAS",
                "emoji": "👤",
                "descricao": "Contas prontas para compra.",
                "banner_url": "",
                "cor": 0x22C55E,
                "produtos": [
                    {
                        "nome": "RAÇA MÍSTICA ALEATÓRIA + ITENS",
                        "preco": "R$ 12,90",
                        "descricao": "Conta com raça mística aleatória + itens.",
                        "estoque_arquivo": "contas_stock.txt",
                        "stock_quantity": 0,
                    },
                    {
                        "nome": "LEVEL MAX + ITENS",
                        "preco": "R$ 7,90",
                        "descricao": "Conta level max + itens.",
                        "estoque_arquivo": "contas_stock.txt",
                        "stock_quantity": 0,
                    },
                    {
                        "nome": "CONTA PREMIUM SAILOR",
                        "preco": "R$ 19,90",
                        "descricao": "Conta premium Sailor.",
                        "estoque_arquivo": "contas_stock.txt",
                        "stock_quantity": 0,
                    },
                ],
            },
            "itens": {
                "nome": "ITENS",
                "emoji": "🎁",
                "descricao": "Itens raros disponíveis.",
                "banner_url": "",
                "cor": 0x3B82F6,
                "produtos": [
                    {
                        "nome": "KIT DE ITENS RAROS",
                        "preco": "R$ 5,50",
                        "descricao": "Kit com itens raros.",
                        "estoque_arquivo": "itens_stock.txt",
                        "stock_quantity": 0,
                    },
                    {
                        "nome": "CAIXA DE AURA",
                        "preco": "R$ 1,20",
                        "descricao": "Caixa contendo aura aleatória.",
                        "estoque_arquivo": "itens_stock.txt",
                        "stock_quantity": 0,
                    },
                ],
            },
            "reroll_raca": {
                "nome": "REROLL RAÇA",
                "emoji": "🧬",
                "descricao": "Pacotes de reroll de raça.",
                "banner_url": "",
                "cor": 0xF59E0B,
                "produtos": [
                    {
                        "nome": "1k reroll raça",
                        "preco": "R$ 1,00",
                        "descricao": "Pacote 1k reroll raça.",
                        "estoque_arquivo": "reroll_stock.txt",
                        "stock_quantity": 0,
                    },
                    {
                        "nome": "5k reroll raça",
                        "preco": "R$ 4,50",
                        "descricao": "Pacote 5k reroll raça.",
                        "estoque_arquivo": "reroll_stock.txt",
                        "stock_quantity": 0,
                    },
                    {
                        "nome": "10k reroll raça",
                        "preco": "R$ 9,50",
                        "descricao": "Pacote 10k reroll raça.",
                        "estoque_arquivo": "reroll_stock.txt",
                        "stock_quantity": 0,
                    },
                ],
            },
        },
    }


def save_data(data: dict) -> None:
    ARQUIVO_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")



def load_data() -> dict:
    if not ARQUIVO_JSON.exists():
        data = default_data()
        save_data(data)
        return data

    try:
        data = json.loads(ARQUIVO_JSON.read_text(encoding="utf-8"))
    except Exception:
        data = default_data()
        save_data(data)
        return data

    base = default_data()
    changed = False

    for section, section_value in base.items():
        if section not in data:
            data[section] = section_value
            changed = True
            continue

        if isinstance(section_value, dict):
            for key, value in section_value.items():
                if key not in data[section]:
                    data[section][key] = value
                    changed = True

    if "categorias" in base:
        for category_id, category_data in base["categorias"].items():
            if category_id not in data["categorias"]:
                data["categorias"][category_id] = category_data
                changed = True

    for category_id, category in data.get("categorias", {}).items():
        if "produtos" not in category:
            category["produtos"] = []
            changed = True
            continue
        for product in category["produtos"]:
            if "stock_quantity" not in product:
                product["stock_quantity"] = 0
                changed = True
            if "estoque_arquivo" not in product:
                product["estoque_arquivo"] = f"{category_id}_stock.txt"
                changed = True

    if changed:
        save_data(data)
    return data



def is_admin(member: discord.Member) -> bool:
    if member.guild_permissions.administrator:
        return True
    role = member.guild.get_role(CARGO_ADMIN_ID)
    return role in member.roles if role else False



def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9\s_-]", "", text).strip().lower()
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:90] or "item"



def get_color(value) -> discord.Color:
    try:
        if isinstance(value, int):
            return discord.Color(value)
        if isinstance(value, str):
            return discord.Color(int(value.replace("#", ""), 16))
    except Exception:
        pass
    return discord.Color(COR_PADRAO)



def money_to_float(price: str) -> float:
    data = load_data()
    moeda = data["loja"].get("moeda", MOEDA_PADRAO)
    clean = price.replace(moeda, "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(clean)
    except Exception:
        return 0.0



def format_money(value: float) -> str:
    data = load_data()
    moeda = data["loja"].get("moeda", MOEDA_PADRAO)
    return f"{moeda} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")



def stock_count(filename: str) -> int:
    path = Path(filename)
    if not path.exists():
        return 0
    return len([x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()])



def add_stock(filename: str, lines_to_add: list[str]) -> int:
    path = Path(filename)
    current = []
    if path.exists():
        current = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    current.extend([x.strip() for x in lines_to_add if x.strip()])
    path.write_text("\n".join(current), encoding="utf-8")
    return len(lines_to_add)



def pop_stock(filename: str) -> Optional[str]:
    path = Path(filename)
    if not path.exists():
        return None
    lines = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not lines:
        return None
    first = lines.pop(0)
    path.write_text("\n".join(lines), encoding="utf-8")
    return first


def product_display_stock(product: dict) -> int:
    linhas = stock_count(product.get("estoque_arquivo", ""))
    quantidade = int(product.get("stock_quantity", 0) or 0)
    return max(0, linhas + quantidade)


def set_product_stock_quantity(product_name: str, quantidade: int) -> tuple[bool, str, int]:
    data = load_data()
    for category in data["categorias"].values():
        for product in category["produtos"]:
            if product["nome"].casefold() == product_name.casefold():
                product["stock_quantity"] = max(0, int(quantidade))
                save_data(data)
                return True, product["nome"], product_display_stock(product)
    return False, "", 0


def add_product_stock_quantity(product_name: str, quantidade: int) -> tuple[bool, str, int]:
    data = load_data()
    for category in data["categorias"].values():
        for product in category["produtos"]:
            if product["nome"].casefold() == product_name.casefold():
                atual = int(product.get("stock_quantity", 0) or 0)
                product["stock_quantity"] = max(0, atual + int(quantidade))
                save_data(data)
                return True, product["nome"], product_display_stock(product)
    return False, "", 0


def remove_product_stock_quantity(product_name: str, quantidade: int) -> tuple[bool, str, int]:
    data = load_data()
    for category in data["categorias"].values():
        for product in category["produtos"]:
            if product["nome"].casefold() == product_name.casefold():
                atual = int(product.get("stock_quantity", 0) or 0)
                product["stock_quantity"] = max(0, atual - int(quantidade))
                save_data(data)
                return True, product["nome"], product_display_stock(product)
    return False, "", 0


def find_product(product_name: str):
    data = load_data()
    for category_id, category in data["categorias"].items():
        for product in category["produtos"]:
            if product["nome"].casefold() == product_name.casefold():
                return category_id, category, product
    return None, None, None



def parse_buyer_id(channel: discord.TextChannel) -> Optional[int]:
    topic = channel.topic or ""
    match = re.search(r"comprador:(\d+)", topic)
    return int(match.group(1)) if match else None



def parse_product_name(channel: discord.TextChannel) -> Optional[str]:
    topic = channel.topic or ""
    match = re.search(r"produto:(.+)$", topic)
    return match.group(1).strip() if match else None



def base_embed(title: str, description: str, color: discord.Color) -> discord.Embed:
    data = load_data()
    embed = discord.Embed(title=title, description=description, color=color)
    thumb = data["painel"].get("thumbnail_url", "")
    if thumb:
        embed.set_thumbnail(url=thumb)
    embed.set_footer(text=data["loja"].get("nome", NOME_PADRAO_LOJA))
    return embed


# =========================
# PIX / QR CODE
# =========================
def crc16(payload: str) -> str:
    polynomial = 0x1021
    result = 0xFFFF
    for char in payload:
        result ^= ord(char) << 8
        for _ in range(8):
            if result & 0x8000:
                result = (result << 1) ^ polynomial
            else:
                result <<= 1
            result &= 0xFFFF
    return f"{result:04X}"



def emv(field_id: str, value: str) -> str:
    value = str(value)
    return f"{field_id}{len(value):02d}{value}"



def only_ascii(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ASCII", "ignore").decode("ASCII")
    return text.upper().strip()



def build_pix_payload(key: str, amount: Optional[float] = None, txid: str = "***") -> str:
    data = load_data()

    key = (key or "").strip()
    beneficiary = only_ascii(data["pix"].get("beneficiario") or MERCHANT_NAME)[:25]
    city = only_ascii(data["pix"].get("cidade") or MERCHANT_CITY)[:15]
    txid = only_ascii(txid)[:25] or "***"

    gui = emv("00", "BR.GOV.BCB.PIX")
    key_field = emv("01", key)
    merchant_account = emv("26", gui + key_field)

    payload = ""
    payload += emv("00", "01")
    payload += emv("01", "11")
    payload += merchant_account
    payload += emv("52", "0000")
    payload += emv("53", "986")
    if amount is not None and amount > 0:
        payload += emv("54", f"{amount:.2f}")
    payload += emv("58", "BR")
    payload += emv("59", beneficiary)
    payload += emv("60", city)
    payload += emv("62", emv("05", txid))
    payload_with_crc = payload + "6304"
    payload_with_crc += crc16(payload_with_crc)
    return payload_with_crc



def build_qr_file(payload: str) -> discord.File:
    qr = qrcode.QRCode(version=None, box_size=10, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return discord.File(buffer, filename="pix_qrcode.png")



def build_pix_embed(product_name: Optional[str] = None, amount_text: Optional[str] = None) -> tuple[discord.Embed, discord.File]:
    data = load_data()
    key = data["pix"].get("chave", "")
    amount = money_to_float(amount_text) if amount_text else None
    payload = build_pix_payload(key, amount=amount, txid=slugify(product_name or "compra")[:25].upper())
    qr_file = build_qr_file(payload)

    desc = [
        "Escaneie o QR Code ou copie o código Pix abaixo.",
        f"**Tipo:** {data['pix'].get('tipo', 'aleatoria').title()}",
        f"**Chave:** `{key}`",
    ]
    if product_name:
        desc.append(f"**Produto:** {product_name}")
    if amount_text:
        desc.append(f"**Valor:** {amount_text}")

    desc.append(f"\n**Pix Copia e Cola:**\n```\n{payload}\n```")

    embed = base_embed("💳 Pagamento via Pix", "\n".join(desc), discord.Color.gold())
    embed.set_image(url="attachment://pix_qrcode.png")
    return embed, qr_file


# =========================
# LOG / ENTREGA
# =========================
async def send_log(guild: discord.Guild, title: str, buyer=None, product_name: str = "", price: str = "", ticket_channel=None, extra: str = ""):
    channel = guild.get_channel(CANAL_LOGS_ID)
    if not isinstance(channel, discord.TextChannel):
        return

    embed = discord.Embed(title=title, color=discord.Color.blurple())
    if buyer:
        embed.add_field(name="👤 Cliente", value=buyer.mention, inline=False)
    if product_name:
        embed.add_field(name="📦 Produto", value=product_name, inline=False)
    if price:
        embed.add_field(name="💰 Valor", value=price, inline=False)
    if ticket_channel:
        embed.add_field(name="🎫 Ticket", value=ticket_channel.mention, inline=False)
    if extra:
        embed.add_field(name="📌 Extra", value=extra[:1024], inline=False)
    await channel.send(embed=embed)


async def deliver_product(guild: discord.Guild, buyer: Optional[discord.Member], channel: Optional[discord.TextChannel], product_name: str, manual_content: Optional[str] = None):
    _, _, product = find_product(product_name)
    if not product:
        return False, "Produto não encontrado."

    content = manual_content.strip() if manual_content else pop_stock(product["estoque_arquivo"])
    if not content:
        return False, "Sem estoque automático. Use /entrega_manual."

    embed = base_embed(
        f"📦 Entrega — {product_name}",
        f"**Seu item foi liberado com sucesso.**\n\n```\n{content}\n```",
        discord.Color(COR_SUCESSO),
    )

    dm_ok = False
    if buyer:
        try:
            await buyer.send(embed=embed)
            dm_ok = True
        except discord.Forbidden:
            dm_ok = False

    if channel:
        await channel.send(embed=embed)
        if buyer:
            await channel.send(f"✅ Entrega registrada para {buyer.mention}.")

    await send_log(
        guild,
        title="📬 Entrega realizada",
        buyer=buyer,
        product_name=product_name,
        price=product.get("preco", ""),
        ticket_channel=channel,
        extra="DM enviada." if dm_ok else "Entrega feita no ticket. DM bloqueada ou indisponível.",
    )
    return True, "Entrega concluída com sucesso."


# =========================
# VIEWS
# =========================
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fechar", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="twx_close_ticket_v5")
    async def close_ticket(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("Esse botão só funciona em ticket.", ephemeral=True)
            return
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message("Só a equipe pode fechar ticket.", ephemeral=True)
            return
        await interaction.response.send_message("Fechando ticket em 3 segundos.", ephemeral=True)
        await asyncio.sleep(3)
        await interaction.channel.delete()


class TicketActionView(discord.ui.View):
    def __init__(self, buyer_id: int, product_name: str):
        super().__init__(timeout=None)
        self.buyer_id = buyer_id
        self.product_name = product_name

    @discord.ui.button(label="Enviar Pix", style=discord.ButtonStyle.secondary, emoji="💳", custom_id="twx_send_pix_v5")
    async def send_pix(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("Use em ticket.", ephemeral=True)
            return
        _, _, product = find_product(self.product_name)
        amount = product.get("preco") if product else None
        embed, qr_file = build_pix_embed(self.product_name, amount)
        await interaction.response.send_message(embed=embed, file=qr_file)

    @discord.ui.button(label="Confirmar Pagamento", style=discord.ButtonStyle.success, emoji="✅", custom_id="twx_confirm_payment_v5")
    async def confirm_payment(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
            await interaction.response.send_message("Só a equipe pode confirmar pagamento.", ephemeral=True)
            return
        guild = interaction.guild
        if guild is None or not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("Erro ao validar o ticket.", ephemeral=True)
            return

        _, _, product = find_product(self.product_name)
        if not product:
            await interaction.response.send_message("Produto não encontrado.", ephemeral=True)
            return

        buyer = guild.get_member(self.buyer_id)
        client_role = guild.get_role(CARGO_CLIENTE_ID)
        if buyer and client_role:
            try:
                await buyer.add_roles(client_role, reason="Compra confirmada")
            except discord.Forbidden:
                pass

        await interaction.response.send_message(embed=base_embed(
            "✅ Pagamento confirmado",
            "Pagamento aprovado. Vou tentar fazer a entrega automática agora.",
            discord.Color(COR_SUCESSO),
        ))

        await send_log(guild, "🛒 Compra confirmada", buyer, product["nome"], product["preco"], interaction.channel)
        ok, msg = await deliver_product(guild, buyer, interaction.channel, product["nome"])
        if not ok:
            await interaction.channel.send(f"⚠️ {msg}")

    @discord.ui.button(label="Abrir entrega manual", style=discord.ButtonStyle.primary, emoji="📦", custom_id="twx_manual_hint_v5")
    async def manual_hint(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_message(
            "Use `/entrega_manual mensagem:SEU_CONTEUDO` para enviar manualmente neste ticket.",
            ephemeral=True,
        )


class ProductSelect(discord.ui.Select):
    def __init__(self, category_id: str):
        self.category_id = category_id
        data = load_data()
        category = data["categorias"][category_id]

        options = []
        for product in category["produtos"][:25]:
            estoque = stock_count(product["estoque_arquivo"])
            stock_text = f"Estoque {estoque}" if estoque > 0 else "Sob consulta"
            options.append(
                discord.SelectOption(
                    label=product["nome"][:100],
                    description=f"{product['preco']} • {stock_text}"[:100],
                    emoji=category["emoji"],
                    value=product["nome"],
                )
            )

        super().__init__(
            placeholder="Selecione um produto para abrir ticket...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"twx_select_{category_id}_v5",
        )

    async def callback(self, interaction: discord.Interaction):
        if not isinstance(self.view, CategoryView):
            await interaction.response.send_message("Erro interno.", ephemeral=True)
            return
        await self.view.create_ticket(interaction, self.category_id, self.values[0])


class CategoryView(discord.ui.View):
    def __init__(self, category_id: str):
        super().__init__(timeout=None)
        self.category_id = category_id
        self.add_item(ProductSelect(category_id))

    async def create_ticket(self, interaction: discord.Interaction, category_id: str, product_name: str):
        guild = interaction.guild
        user = interaction.user

        if guild is None or not isinstance(user, discord.Member):
            await interaction.response.send_message("Erro ao criar ticket.", ephemeral=True)
            return

        data = load_data()
        if data["painel"].get("status") != "online":
            await interaction.response.send_message("A loja está offline agora.", ephemeral=True)
            return

        ticket_category = guild.get_channel(CATEGORY_TICKETS_ID)
        if not isinstance(ticket_category, discord.CategoryChannel):
            await interaction.response.send_message("Categoria de tickets não encontrada.", ephemeral=True)
            return

        for channel in ticket_category.text_channels:
            if channel.topic and f"comprador:{user.id}" in channel.topic:
                await interaction.response.send_message(f"Você já tem um ticket aberto: {channel.mention}", ephemeral=True)
                return

        _, category, product = find_product(product_name)
        if not category or not product:
            await interaction.response.send_message("Produto não encontrado.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        if guild.me:
            overwrites[guild.me] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, read_message_history=True)
        admin_role = guild.get_role(CARGO_ADMIN_ID)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel_name = f"ticket-{slugify(product_name)}-{slugify(user.name)}"[:90]
        ticket = await guild.create_text_channel(
            name=channel_name,
            category=ticket_category,
            overwrites=overwrites,
            topic=f"comprador:{user.id} | produto:{product_name}",
        )

        estoque = stock_count(product["estoque_arquivo"])
        stock_line = f"{estoque} unidade(s)" if estoque > 0 else "sob consulta"
        embed = base_embed(
            f"{category['emoji']} {product['nome']}",
            (
                f"**Descrição:** {product['descricao']}\n"
                f"**Preço:** {product['preco']}\n"
                f"**Estoque:** {stock_line}\n\n"
                "Use o botão **Enviar Pix** para receber o QR Code do pagamento."
            ),
            get_color(category.get("cor")),
        )
        if category.get("banner_url"):
            embed.set_image(url=category["banner_url"])

        await ticket.send(content=user.mention, embed=embed, view=TicketActionView(user.id, product["nome"]))
        await ticket.send(view=CloseTicketView())

        await send_log(guild, "🧾 Ticket criado", user, product["nome"], product["preco"], ticket)
        await interaction.response.send_message(f"Ticket criado com sucesso: {ticket.mention}", ephemeral=True)


class CalcTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir ticket de cálculo", style=discord.ButtonStyle.primary, emoji="🧮", custom_id="twx_calc_ticket_v5")
    async def open_calc_ticket(self, interaction: discord.Interaction, _: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        if guild is None or not isinstance(user, discord.Member):
            await interaction.response.send_message("Erro ao criar ticket.", ephemeral=True)
            return

        ticket_category = guild.get_channel(CATEGORY_TICKETS_ID)
        if not isinstance(ticket_category, discord.CategoryChannel):
            await interaction.response.send_message("Categoria de tickets não encontrada.", ephemeral=True)
            return

        for channel in ticket_category.text_channels:
            if channel.topic and f"comprador:{user.id}" in channel.topic and "produto:CÁLCULO PERSONALIZADO" in channel.topic:
                await interaction.response.send_message(f"Você já possui um ticket de cálculo: {channel.mention}", ephemeral=True)
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        if guild.me:
            overwrites[guild.me] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, read_message_history=True)
        admin_role = guild.get_role(CARGO_ADMIN_ID)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        ticket = await guild.create_text_channel(
            name=f"ticket-calc-{slugify(user.name)}"[:90],
            category=ticket_category,
            overwrites=overwrites,
            topic=f"comprador:{user.id} | produto:CÁLCULO PERSONALIZADO",
        )

        embed = base_embed(
            "🧮 Cálculo personalizado",
            "Envie aqui o item, quantidade e detalhes para a equipe calcular o valor.",
            discord.Color(COR_ALERTA),
        )
        await ticket.send(content=user.mention, embed=embed)
        await ticket.send(view=CloseTicketView())
        await send_log(guild, "📐 Ticket de cálculo criado", user, "CÁLCULO PERSONALIZADO", "A definir", ticket)
        await interaction.response.send_message(f"Ticket criado: {ticket.mention}", ephemeral=True)


class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.participants = set()

    @discord.ui.button(label="Participar", style=discord.ButtonStyle.success, emoji="🎉")
    async def participate(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.participants.add(interaction.user.id)
        await interaction.response.send_message("Você entrou no sorteio.", ephemeral=True)


# =========================
# PAINEL
# =========================
async def send_panel(guild: discord.Guild, clear_channel: bool = False):
    data = load_data()
    panel = data["painel"]
    panel_channel = guild.get_channel(CANAL_PAINEL_ID)
    if not isinstance(panel_channel, discord.TextChannel):
        raise ValueError("Canal do painel não encontrado.")

    if clear_channel:
        try:
            await panel_channel.purge(limit=100)
        except discord.Forbidden:
            pass

    if panel.get("status") == "offline":
        offline_embed = base_embed(
            "🔴 LOJA OFFLINE",
            f"**{panel['titulo']}**\n{panel.get('mensagem_offline', 'Loja offline.')}",
            discord.Color(COR_ERRO),
        )
        if panel.get("banner_offline_url"):
            offline_embed.set_image(url=panel["banner_offline_url"])
        elif panel.get("banner_online_url"):
            offline_embed.set_image(url=panel["banner_online_url"])
        await panel_channel.send(embed=offline_embed)
        return

    resumo = []
    if panel.get("mostrar_resumo_estoque", True):
        total_produtos = 0
        total_stock = 0
        for category in data["categorias"].values():
            total_produtos += len(category["produtos"])
            for p in category["produtos"]:
                total_stock += product_display_stock(p)
        resumo.append(f"**Categorias:** {len(data['categorias'])}")
        resumo.append(f"**Produtos:** {total_produtos}")
        resumo.append(f"**Estoque total:** {total_stock}")

    top_desc = [f"**{panel['titulo']}**", panel.get("mensagem_boas_vindas", "")] + resumo
    top_embed = base_embed("🟢 LOJA ONLINE", "\n".join([x for x in top_desc if x]), get_color(panel.get("cor")))
    if panel.get("banner_online_url"):
        top_embed.set_image(url=panel["banner_online_url"])
    await panel_channel.send(embed=top_embed)

    for category_id, category in data["categorias"].items():
        estoque_total = sum(product_display_stock(p) for p in category["produtos"])
        category_embed = base_embed(
            f"{category['emoji']} {category['nome']}",
            f"{category['descricao']}\n\n**Produtos:** {len(category['produtos'])}\n**Estoque da categoria:** {estoque_total}",
            get_color(category.get("cor")),
        )
        if category.get("banner_url"):
            category_embed.set_image(url=category["banner_url"])
        await panel_channel.send(embed=category_embed, view=CategoryView(category_id))

    if panel.get("mostrar_calc_no_painel", True):
        calc_embed = base_embed(
            "🎟️ Atendimento para item fora da loja",
            "Abra um ticket para pedir orçamento ou cálculo personalizado.",
            discord.Color(COR_ALERTA),
        )
        await panel_channel.send(embed=calc_embed, view=CalcTicketView())


# =========================
# EVENTOS
# =========================
@bot.event
async def on_ready():
    data = load_data()
    for category_id in data["categorias"].keys():
        bot.add_view(CategoryView(category_id))
    bot.add_view(CalcTicketView())
    bot.add_view(CloseTicketView())
    bot.add_view(TicketActionView(0, "dummy"))

    try:
        synced = await tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Bot online como {bot.user}")
        print(f"{len(synced)} comando(s) sincronizado(s).")
    except Exception as exc:
        print(f"Erro ao sincronizar comandos: {exc}")


# =========================
# COMANDOS - PAINEL / CONFIG
# =========================
@tree.command(name="painel", description="Envia ou atualiza o painel da loja", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(titulo="Título do painel", status="online ou offline", limpar_canal="Apagar mensagens antigas do canal")
async def painel(interaction: discord.Interaction, titulo: Optional[str] = None, status: Optional[str] = None, limpar_canal: bool = False):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    if titulo:
        data["painel"]["titulo"] = titulo
    if status:
        data["painel"]["status"] = status.strip().lower()
    save_data(data)
    await interaction.response.defer(ephemeral=True)
    await send_panel(interaction.guild, clear_channel=limpar_canal)
    await interaction.followup.send("Painel atualizado com sucesso.", ephemeral=True)


@tree.command(name="set_banner_online", description="Define o banner principal da loja online", guild=discord.Object(id=GUILD_ID))
async def set_banner_online(interaction: discord.Interaction, url: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    data["painel"]["banner_online_url"] = url
    save_data(data)
    await interaction.response.send_message("Banner online atualizado.", ephemeral=True)


@tree.command(name="set_logo", description="Define a logo pequena da loja", guild=discord.Object(id=GUILD_ID))
async def set_logo(interaction: discord.Interaction, url: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    data["painel"]["thumbnail_url"] = url
    save_data(data)
    await interaction.response.send_message("Logo atualizada.", ephemeral=True)


@tree.command(name="config_pix", description="Troca a chave Pix e dados do QR Code", guild=discord.Object(id=GUILD_ID))
async def config_pix(interaction: discord.Interaction, chave: str, tipo: str = "aleatoria", beneficiario: Optional[str] = None, cidade: Optional[str] = None):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    data["pix"]["chave"] = chave.strip()
    data["pix"]["tipo"] = tipo.strip().lower()
    if beneficiario:
        data["pix"]["beneficiario"] = beneficiario
    if cidade:
        data["pix"]["cidade"] = cidade
    save_data(data)
    await interaction.response.send_message("Configuração Pix atualizada.", ephemeral=True)


@tree.command(name="loja_on", description="Coloca a loja online", guild=discord.Object(id=GUILD_ID))
async def loja_on(interaction: discord.Interaction, limpar_canal: bool = True):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    data["painel"]["status"] = "online"
    save_data(data)
    await interaction.response.defer(ephemeral=True)
    await send_panel(interaction.guild, clear_channel=limpar_canal)
    await interaction.followup.send("Loja colocada como online.", ephemeral=True)


@tree.command(name="loja_off", description="Coloca a loja offline", guild=discord.Object(id=GUILD_ID))
async def loja_off(interaction: discord.Interaction, mensagem: str = "Loja offline no momento.", limpar_canal: bool = True):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    data["painel"]["status"] = "offline"
    data["painel"]["mensagem_offline"] = mensagem
    save_data(data)
    await interaction.response.defer(ephemeral=True)
    await send_panel(interaction.guild, clear_channel=limpar_canal)
    await interaction.followup.send("Loja colocada como offline.", ephemeral=True)


# =========================
# COMANDOS - CATEGORIAS / PRODUTOS / ESTOQUE
# =========================
@tree.command(name="categoria_add", description="Cria uma nova categoria", guild=discord.Object(id=GUILD_ID))
async def categoria_add(interaction: discord.Interaction, categoria_id: str, nome: str, emoji: str, descricao: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    categoria_id = slugify(categoria_id).replace("-", "_")
    if categoria_id in data["categorias"]:
        await interaction.response.send_message("Essa categoria já existe.", ephemeral=True)
        return
    data["categorias"][categoria_id] = {
        "nome": nome,
        "emoji": emoji,
        "descricao": descricao,
        "banner_url": "",
        "cor": COR_PADRAO,
        "produtos": [],
    }
    save_data(data)
    await interaction.response.send_message(f"Categoria `{categoria_id}` criada.", ephemeral=True)


@tree.command(name="categoria_banner", description="Define o banner de uma categoria", guild=discord.Object(id=GUILD_ID))
async def categoria_banner(interaction: discord.Interaction, categoria_id: str, url: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    if categoria_id not in data["categorias"]:
        await interaction.response.send_message("Categoria não encontrada.", ephemeral=True)
        return
    data["categorias"][categoria_id]["banner_url"] = url
    save_data(data)
    await interaction.response.send_message("Banner da categoria atualizado.", ephemeral=True)


@tree.command(name="produto_add", description="Adiciona produto em uma categoria", guild=discord.Object(id=GUILD_ID))
async def produto_add(interaction: discord.Interaction, categoria_id: str, nome: str, preco: str, descricao: str, estoque_arquivo: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    if categoria_id not in data["categorias"]:
        await interaction.response.send_message("Categoria não encontrada.", ephemeral=True)
        return
    data["categorias"][categoria_id]["produtos"].append({
        "nome": nome,
        "preco": preco,
        "descricao": descricao,
        "estoque_arquivo": estoque_arquivo,
        "stock_quantity": 0,
    })
    save_data(data)
    await interaction.response.send_message(f"Produto `{nome}` adicionado.", ephemeral=True)


@tree.command(name="produto_editar", description="Edita um produto", guild=discord.Object(id=GUILD_ID))
async def produto_editar(interaction: discord.Interaction, nome_atual: str, novo_nome: Optional[str] = None, novo_preco: Optional[str] = None, nova_descricao: Optional[str] = None, novo_estoque_arquivo: Optional[str] = None, novo_stock: Optional[int] = None):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    for category in data["categorias"].values():
        for product in category["produtos"]:
            if product["nome"].casefold() == nome_atual.casefold():
                if novo_nome:
                    product["nome"] = novo_nome
                if novo_preco:
                    product["preco"] = novo_preco
                if nova_descricao:
                    product["descricao"] = nova_descricao
                if novo_estoque_arquivo:
                    product["estoque_arquivo"] = novo_estoque_arquivo
                if novo_stock is not None:
                    product["stock_quantity"] = max(0, int(novo_stock))
                save_data(data)
                await interaction.response.send_message("Produto atualizado.", ephemeral=True)
                return
    await interaction.response.send_message("Produto não encontrado.", ephemeral=True)


@tree.command(name="produto_remover", description="Remove produto", guild=discord.Object(id=GUILD_ID))
async def produto_remover(interaction: discord.Interaction, categoria_id: str, nome: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    data = load_data()
    if categoria_id not in data["categorias"]:
        await interaction.response.send_message("Categoria não encontrada.", ephemeral=True)
        return
    before = len(data["categorias"][categoria_id]["produtos"])
    data["categorias"][categoria_id]["produtos"] = [p for p in data["categorias"][categoria_id]["produtos"] if p["nome"].casefold() != nome.casefold()]
    save_data(data)
    if before == len(data["categorias"][categoria_id]["produtos"]):
        await interaction.response.send_message("Produto não encontrado.", ephemeral=True)
        return
    await interaction.response.send_message("Produto removido.", ephemeral=True)




@tree.command(name="estoque_set", description="Define o estoque manual do produto", guild=discord.Object(id=GUILD_ID))
async def estoque_set_cmd(interaction: discord.Interaction, produto: str, quantidade: app_commands.Range[int, 0, 999999] = 0):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    ok, nome, total = set_product_stock_quantity(produto, quantidade)
    if not ok:
        await interaction.response.send_message("Produto não encontrado.", ephemeral=True)
        return
    await interaction.response.send_message(
        f"Estoque manual de `{nome}` definido para **{quantidade}**. Total visível agora: **{total}**.",
        ephemeral=True,
    )


@tree.command(name="estoque_add_qtd", description="Adiciona quantidade ao estoque manual", guild=discord.Object(id=GUILD_ID))
async def estoque_add_qtd_cmd(interaction: discord.Interaction, produto: str, quantidade: app_commands.Range[int, 1, 999999]):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    ok, nome, total = add_product_stock_quantity(produto, quantidade)
    if not ok:
        await interaction.response.send_message("Produto não encontrado.", ephemeral=True)
        return
    await interaction.response.send_message(
        f"Adicionado **{quantidade}** ao estoque manual de `{nome}`. Total visível agora: **{total}**.",
        ephemeral=True,
    )


@tree.command(name="estoque_rem_qtd", description="Remove quantidade do estoque manual", guild=discord.Object(id=GUILD_ID))
async def estoque_rem_qtd_cmd(interaction: discord.Interaction, produto: str, quantidade: app_commands.Range[int, 1, 999999]):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    ok, nome, total = remove_product_stock_quantity(produto, quantidade)
    if not ok:
        await interaction.response.send_message("Produto não encontrado.", ephemeral=True)
        return
    await interaction.response.send_message(
        f"Removido **{quantidade}** do estoque manual de `{nome}`. Total visível agora: **{total}**.",
        ephemeral=True,
    )

@tree.command(name="estoque_add", description="Adiciona linhas ao estoque", guild=discord.Object(id=GUILD_ID))
async def estoque_add_cmd(interaction: discord.Interaction, produto: str, conteudo: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    _, _, product = find_product(produto)
    if not product:
        await interaction.response.send_message("Produto não encontrado.", ephemeral=True)
        return
    lines = [line for line in conteudo.split("|") if line.strip()]
    qtd = add_stock(product["estoque_arquivo"], lines)
    await interaction.response.send_message(f"{qtd} item(ns) adicionados ao estoque.", ephemeral=True)


@tree.command(name="estoque_ver", description="Mostra o estoque do produto", guild=discord.Object(id=GUILD_ID))
async def estoque_ver(interaction: discord.Interaction, produto: str):
    _, _, product = find_product(produto)
    if not product:
        await interaction.response.send_message("Produto não encontrado.", ephemeral=True)
        return
    linhas = stock_count(product.get("estoque_arquivo", ""))
    manual = int(product.get("stock_quantity", 0) or 0)
    total = product_display_stock(product)
    texto = (
        f"**Produto:** `{product['nome']}`\n"
        f"**Estoque por linhas:** **{linhas}**\n"
        f"**Estoque manual:** **{manual}**\n"
        f"**Total visível:** **{total}**"
    )
    await interaction.response.send_message(embed=base_embed("📦 Estoque do produto", texto, discord.Color(COR_INFO)), ephemeral=True)


@tree.command(name="produtos", description="Lista produtos da loja", guild=discord.Object(id=GUILD_ID))
async def produtos(interaction: discord.Interaction):
    data = load_data()
    parts = []
    for category in data["categorias"].values():
        lines = [f"**{category['emoji']} {category['nome']}**"]
        if not category["produtos"]:
            lines.append("Sem produtos.")
        else:
            for product in category["produtos"][:20]:
                lines.append(f"• {product['nome']} — {product['preco']} — estoque {product_display_stock(product)}")
        parts.append("\n".join(lines))
    await interaction.response.send_message(embed=base_embed("📦 Produtos cadastrados", "\n\n".join(parts)[:4000], discord.Color(COR_INFO)), ephemeral=True)


# =========================
# COMANDOS - TICKETS / PIX / ENTREGA
# =========================
@tree.command(name="pix", description="Envia o Pix com QR Code", guild=discord.Object(id=GUILD_ID))
async def pix(interaction: discord.Interaction):
    product_name = None
    amount_text = None
    if isinstance(interaction.channel, discord.TextChannel):
        product_name = parse_product_name(interaction.channel)
        _, _, product = find_product(product_name or "")
        if product:
            amount_text = product.get("preco")

    embed, qr_file = build_pix_embed(product_name, amount_text)
    await interaction.response.send_message(embed=embed, file=qr_file, ephemeral=not isinstance(interaction.channel, discord.TextChannel))


@tree.command(name="entrega_manual", description="Envia a entrega manualmente", guild=discord.Object(id=GUILD_ID))
async def entrega_manual(interaction: discord.Interaction, mensagem: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Use dentro do ticket.", ephemeral=True)
        return
    buyer_id = parse_buyer_id(interaction.channel)
    product_name = parse_product_name(interaction.channel)
    buyer = interaction.guild.get_member(buyer_id) if interaction.guild and buyer_id else None
    if not product_name:
        await interaction.response.send_message("Produto do ticket não encontrado.", ephemeral=True)
        return
    ok, msg = await deliver_product(interaction.guild, buyer, interaction.channel, product_name, manual_content=mensagem)
    await interaction.response.send_message(msg, ephemeral=True)


@tree.command(name="entrega_auto", description="Tenta a entrega automática novamente", guild=discord.Object(id=GUILD_ID))
async def entrega_auto(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Use dentro do ticket.", ephemeral=True)
        return
    buyer_id = parse_buyer_id(interaction.channel)
    product_name = parse_product_name(interaction.channel)
    buyer = interaction.guild.get_member(buyer_id) if interaction.guild and buyer_id else None
    if not product_name:
        await interaction.response.send_message("Produto do ticket não encontrado.", ephemeral=True)
        return
    ok, msg = await deliver_product(interaction.guild, buyer, interaction.channel, product_name)
    await interaction.response.send_message(msg, ephemeral=True)


@tree.command(name="ticket_renomear", description="Renomeia o ticket", guild=discord.Object(id=GUILD_ID))
async def ticket_renomear(interaction: discord.Interaction, novo_nome: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Use em um ticket.", ephemeral=True)
        return
    await interaction.channel.edit(name=slugify(novo_nome))
    await interaction.response.send_message("Ticket renomeado.", ephemeral=True)


@tree.command(name="ticket_produto", description="Troca o produto vinculado ao ticket", guild=discord.Object(id=GUILD_ID))
async def ticket_produto(interaction: discord.Interaction, produto: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Use em um ticket.", ephemeral=True)
        return
    buyer_id = parse_buyer_id(interaction.channel)
    _, category, product = find_product(produto)
    if not category or not product:
        await interaction.response.send_message("Produto não encontrado.", ephemeral=True)
        return
    await interaction.channel.edit(topic=f"comprador:{buyer_id} | produto:{product['nome']}")
    embed = base_embed(
        f"{category['emoji']} Produto atualizado",
        f"**Produto:** {product['nome']}\n**Preço:** {product['preco']}\n**Descrição:** {product['descricao']}",
        get_color(category.get("cor")),
    )
    await interaction.channel.send(embed=embed, view=TicketActionView(buyer_id or 0, product["nome"]))
    await interaction.response.send_message("Produto do ticket atualizado.", ephemeral=True)


@tree.command(name="ticket_calc", description="Envia o painel de ticket de cálculo", guild=discord.Object(id=GUILD_ID))
async def ticket_calc(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    embed = base_embed(
        "🧮 Cálculo personalizado",
        "Abra um ticket para pedir orçamento de itens que não estão na loja.",
        discord.Color(COR_ALERTA),
    )
    await interaction.response.send_message(embed=embed, view=CalcTicketView())


# =========================
# COMANDOS - EXTRAS
# =========================
@tree.command(name="sorteio", description="Cria um sorteio com botão", guild=discord.Object(id=GUILD_ID))
async def sorteio(interaction: discord.Interaction, premio: str, minutos: app_commands.Range[int, 1, 1440] = 5):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Só a equipe pode usar este comando.", ephemeral=True)
        return

    view = GiveawayView()
    embed = base_embed(
        "🎉 Sorteio",
        f"**Prêmio:** {premio}\n**Duração:** {minutos} minuto(s)\n\nClique no botão abaixo para participar.",
        discord.Color.purple(),
    )
    await interaction.response.send_message("Sorteio criado.", ephemeral=True)
    if interaction.channel:
        await interaction.channel.send(embed=embed, view=view)

    await asyncio.sleep(minutos * 60)
    if not interaction.channel:
        return
    if not view.participants:
        await interaction.channel.send("Sorteio encerrado sem participantes.")
        return
    winner_id = random.choice(list(view.participants))
    winner = interaction.guild.get_member(winner_id) if interaction.guild else None
    if winner:
        await interaction.channel.send(f"🎉 Parabéns {winner.mention}, você venceu **{premio}**!")
    else:
        await interaction.channel.send(f"Sorteio encerrado. Vencedor ID: `{winner_id}`")


@tree.command(name="cupom", description="Calcula valor com desconto", guild=discord.Object(id=GUILD_ID))
async def cupom(interaction: discord.Interaction, valor: str, desconto_percentual: app_commands.Range[int, 1, 100]):
    base = money_to_float(valor)
    final = base * (1 - desconto_percentual / 100)
    await interaction.response.send_message(
        f"Valor original: **{format_money(base)}**\nDesconto: **{desconto_percentual}%**\nValor final: **{format_money(final)}**"
    )


@tree.command(name="calc_robux", description="Calcula valor por quantidade de robux", guild=discord.Object(id=GUILD_ID))
async def calc_robux(interaction: discord.Interaction, quantidade: int, preco_por_mil: str):
    mil = money_to_float(preco_por_mil)
    total = (quantidade / 1000) * mil
    await interaction.response.send_message(f"**{quantidade} robux** = **{format_money(total)}**")


@tree.command(name="anuncio", description="Envia um anúncio estilizado", guild=discord.Object(id=GUILD_ID))
async def anuncio(interaction: discord.Interaction, titulo: str, mensagem: str):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    await interaction.response.send_message(embed=base_embed(f"📢 {titulo}", mensagem, discord.Color(COR_INFO)))


@tree.command(name="cliente", description="Marca um membro como cliente", guild=discord.Object(id=GUILD_ID))
async def cliente(interaction: discord.Interaction, membro: discord.Member):
    if not isinstance(interaction.user, discord.Member) or not is_admin(interaction.user):
        await interaction.response.send_message("Sem permissão.", ephemeral=True)
        return
    cargo = interaction.guild.get_role(CARGO_CLIENTE_ID) if interaction.guild else None
    if not cargo:
        await interaction.response.send_message("Cargo cliente não encontrado.", ephemeral=True)
        return
    await membro.add_roles(cargo, reason="Compra confirmada")
    await interaction.response.send_message(f"{membro.mention} recebeu o cargo de cliente.", ephemeral=True)


@tree.command(name="comandos_loja", description="Mostra os comandos do bot", guild=discord.Object(id=GUILD_ID))
async def comandos_loja(interaction: discord.Interaction):
    texto = (
        "**Painel e visual**\n"
        "/painel, /loja_on, /loja_off, /set_banner_online, /set_logo, /config_pix\n\n"
        "**Categorias e produtos**\n"
        "/categoria_add, /categoria_banner, /produto_add, /produto_editar, /produto_remover, /produtos\n\n"
        "**Estoque e entrega**\n"
        "/estoque_set, /estoque_add_qtd, /estoque_rem_qtd, /estoque_add, /estoque_ver, /pix, /entrega_manual, /entrega_auto\n\n"
        "**Tickets e extras**\n"
        "/ticket_calc, /ticket_renomear, /ticket_produto, /sorteio, /cupom, /calc_robux, /anuncio, /cliente"
    )
    await interaction.response.send_message(embed=base_embed("📚 Comandos da loja", texto, discord.Color.dark_gold()), ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("Defina a variável de ambiente DISCORD_BOT_TOKEN antes de iniciar o bot.")
    bot.run(TOKEN)
