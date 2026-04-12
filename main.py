import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# ==========================================
# 1. 防休眠網頁伺服器 (給 Render 和 UptimeRobot 用的)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "機器人正在雲端快樂運作中！"

def run_server():
    # Render 會自動分配 Port，我們負責讀取它
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# ==========================================
# 2. Discord 機器人主程式
# ==========================================
# 啟用需要讀取訊息的權限
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'機器人已上線！登入身分：{bot.user}')

# 指令：輸入 !hello 來創建頻道
@bot.command()
async def hello(ctx):
    # 檢查輸入指令的人有沒有「管理頻道」的權限
    if ctx.author.guild_permissions.manage_channels:
        guild = ctx.guild
        
        # 檢查伺服器是不是已經有叫做 hello 的頻道了
        existing_channel = discord.utils.get(guild.text_channels, name='hello')
        
        if existing_channel:
            await ctx.send('已經有一個叫做 `hello` 的頻道囉！')
        else:
            # 創建文字頻道
            await guild.create_text_channel('hello')
            await ctx.send('成功幫你創建 `hello` 文字頻道！')
    else:
        await ctx.send('你沒有權限使用這個指令喔！')

# ==========================================
# 3. 啟動機器人
# ==========================================
# 啟動防休眠網頁
keep_alive()

# 從 Render 的環境變數讀取 Token (保護密碼不外洩)
TOKEN = os.environ.get("TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("找不到 Token！請確認你在 Render 後台有設定 TOKEN 環境變數。")