import discord
from discord.ext import commands
import os
import asyncio
import random
from flask import Flask
from threading import Thread

# ==========================================
# 1. 防休眠網頁伺服器
# ==========================================
app = Flask(__name__)
@app.route('/')
def home(): return "霓虹派對機器人運行中！"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run_server).start()

# ==========================================
# 2. Discord 機器人主程式
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 用來紀錄哪些身分組正在「變色中」
rainbow_tasks = {}

# 彩虹顏色清單 (紅橙黃綠藍靛紫)
RAINBOW_COLORS = [
    0xFF0000, 0xFF7F00, 0xFFFF00, 0x00FF00, 0x0000FF, 0x4B0082, 0x9400D3
]

@bot.event
async def on_ready():
    print(f'機器人已上線！登入身分：{bot.user}')

# --- 指令：製造並啟動彩虹身分組 ---
@bot.command()
async def rainbow_role(ctx, name: str):
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ 你沒有管理身分組的權限！")
        return

    # 1. 創建身分組
    try:
        role = await ctx.guild.create_role(name=name, reason="彩虹模式")
        await ctx.send(f"🌈 身分組 `{name}` 已建立，開始閃爍！輸入 `!stop_rainbow` 停止。")
    except Exception as e:
        await ctx.send(f"⚠️ 建立失敗：{e}")
        return

    # 2. 啟動變色迴圈
    rainbow_tasks[ctx.guild.id] = True
    
    index = 0
    while rainbow_tasks.get(ctx.guild.id):
        try:
            # 修改顏色
            await role.edit(color=discord.Color(RAINBOW_COLORS[index]))
            index = (index + 1) % len(RAINBOW_COLORS)
            # 休息一秒，避免被 Discord 封鎖
            await asyncio.sleep(1.2) 
        except Exception as e:
            print(f"變色出錯：{e}")
            break

# --- 指令：停止變色 ---
@bot.command()
async def stop_rainbow(ctx):
    if ctx.guild.id in rainbow_tasks:
        rainbow_tasks[ctx.guild.id] = False
        await ctx.send("rainbow end。")
    else:
        await ctx.send("cant find it。")

# --- 之前的 Destroy 指令 (保留) ---
@bot.command()
async def destroy(ctx):
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.send('🚫 權限不足！')
        return
    await ctx.send('☢️ 正在清理文字頻道...')
    for channel in ctx.guild.text_channels:
        if channel != ctx.channel:
            try: await channel.delete()
            except: continue
    await ctx.send('🧹 清理完畢。')

# ==========================================
# 3. 啟動
# ==========================================
keep_alive()
TOKEN = os.environ.get("TOKEN")
if TOKEN:
    bot.run(TOKEN)
