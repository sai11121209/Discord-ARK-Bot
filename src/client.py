import os
import discord
import requests as rq

try:
    from local_settings import *
except ImportError:
    import keep_alive

    if os.getenv("TOKEN"):
        TOKEN = os.getenv("TOKEN")

    keep_alive.keep_alive()


# 接続に必要なオブジェクトを生成
client = discord.Client()
Prefix = "/"

headers = {
    "User-Agent": "Discord.py",
    "Content-Type": "application/json",
}


@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print("ログインしました")
    await client.change_presence(activity=discord.Game(name="ARK", type=1))


# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    if message.author.bot:
        pass
    elif Prefix == message.content[0]:
        if message.content.upper() == f"{Prefix}STARTSERVER":
            res = rq.get(
                "http://27.91.71.82/commands/wake_on_lan", headers=headers
            ).json()
            if res["state"] == 1:
                await message.channel.send("起動処理が成功しました")
            else:
                if "error" in res:
                    await message.channel.send("リクエストに失敗しました。")
                else:
                    await message.channel.send("起動処理が失敗しました。")
        elif message.content.upper() == f"{Prefix}STOPSERVER":
            res = rq.get("http://27.91.71.82/commands/shutdown", headers=headers).json()
            if res["state"] == 1:
                await message.channel.send("終了処理が成功しました")
            else:
                if "error" in res:
                    await message.channel.send("リクエストに失敗しました。")
                else:
                    await message.channel.send("終了処理が失敗しました。")


client.run(TOKEN)
