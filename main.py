import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# ==========================================
# 1. 防休眠網頁伺服器
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "機器人正在雲端快樂運作中！"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# ==========================================
# 2. Discord 機器人主程式
# ==========================================
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'機器人已上線！登入身分：{bot.user}')

# --- 指令 A：原本的 hello 指令 ---
@bot.command()
async def hello(ctx):
    if ctx.author.guild_permissions.manage_channels:
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.text_channels, name='hello')
        if existing_channel:
            await ctx.send('已經有一個叫做 `hello` 的頻道囉！')
        else:
            await guild.create_text_channel('hello')
            await ctx.send('成功幫你創建 `hello` 文字頻道！')
    else:
        await ctx.send('你沒有權限使用這個指令喔！')

# --- 指令 B：【新功能】批量創建頻道 ---
# 使用方法：!create 10
@bot.command()
async def create(ctx, count: int):
    # 權限檢查
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send('你沒有管理頻道的權限喔！')
        return

    # 數量檢查 (Discord 上限 500)
    current_count = len(ctx.guild.channels)
    if count + current_count > 500:
        await ctx.send(f'❌ 太多了！目前已有 {current_count} 個頻道，再加 {count} 個會超過 Discord 上限 (500)。')
        return

    await ctx.send(f'⚙️ 開始批量生產 {count} 個頻道，請稍候...')

    for i in range(1, count + 1):
        try:
            # 這裡執行創建動作
            await ctx.guild.create_text_channel(f'自動頻道-{i}')
            
            # 每 5 個回報一次進度，避免洗版
            if i % 5 == 0:
                await ctx.send(f'🏗️ 已完成 {i}/{count}...')
        except Exception as e:
            await ctx.send(f'⚠️ 發生錯誤：{e}')
            break

    await ctx.send(f'✅ 報告主人，{count} 個頻道已全數完工！')

# ==========================================
# 3. 啟動機器人
# ==========================================
keep_alive()
TOKEN = os.environ.get("TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("找不到 Token！")
