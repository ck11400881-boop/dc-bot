import discord
from discord.ext import commands
import os
import random
import string
from flask import Flask
from threading import Thread

# ==========================================
# 1. 防休眠網頁伺服器
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "機器人運作中：亂碼與毀滅模式已就緒！"

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

# 產生隨機亂碼的工具函數
def generate_random_name(length=8):
    # 包含小寫字母與數字
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@bot.event
async def on_ready():
    print(f'機器人已上線！登入身分：{bot.user}')

# --- 指令 A：批量創建隨機亂碼頻道 ---
# 使用方法：!create 10
@bot.command()
async def create(ctx, count: int):
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send('❌ 你沒有權限玩亂碼喔！')
        return

    current_count = len(ctx.guild.channels)
    if count + current_count > 500:
        await ctx.send(f'❌ 太多了！會超過上限。')
        return

    await ctx.send(f'🎲 正在生成 {count} 個隨機亂碼頻道...')

    for i in range(1, count + 1):
        try:
            random_name = generate_random_name(10) # 產生 10 位數亂碼
            await ctx.guild.create_text_channel(random_name)
            
            if i % 5 == 0:
                await ctx.send(f'🏗️ 已完成 {i}/{count}...')
        except Exception as e:
            await ctx.send(f'⚠️ 出錯：{e}')
            break

    await ctx.send(f'✨ {count} 個亂碼頻道已撒滿伺服器！')

# --- 指令 B：【毀滅模式】刪除所有文字頻道 ---
# 使用方法：!destroy
@bot.command()
async def destroy(ctx):
    # 極其重要：只有擁有「管理伺服器」權限的人才能用
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.send('🚫 權限不足！這不是你能觸發的按鈕。')
        return

    await ctx.send('☢️ 毀滅程序啟動... 正在清理所有文字頻道...')

    # 取得所有的文字頻道
    channels = ctx.guild.text_channels
    
    for channel in channels:
        # 為了保證機器人還能說話，我們不刪除目前發指令的這個頻道（可選）
        if channel == ctx.channel:
            continue
            
        try:
            await channel.delete()
        except:
            continue

    await ctx.send('🧹 除此之外的文字頻道已全數清理完畢。')

# ==========================================
# 3. 啟動機器人
# ==========================================
keep_alive()
TOKEN = os.environ.get("TOKEN")

if TOKEN:
    bot.run(TOKEN)
