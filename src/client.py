import os
import discord
import difflib
import itertools
import requests as rq

try:
    from local_settings import *
except ImportError:
    import keep_alive

    if os.getenv("TOKEN"):
        TOKEN = os.getenv("TOKEN")
        USER_AGENT = os.getenv("USER_AGENT")
        CONTENT_TYPE = os.getenv("CONTENT_TYPE")

    keep_alive.keep_alive()


# 接続に必要なオブジェクトを生成
client = discord.Client()
Prefix = "/"

headers = {
    "User-Agent": USER_AGENT,
    "Content-Type": CONTENT_TYPE,
}

CommandList = {
    "サーバ起動": ["RUNSERVER"],
    "サーバ停止": ["STOPSERVER"],
}


@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print("ログインしました")
    await client.change_presence(
        activity=discord.Game(name="ARK: Survival Evolved", type=1)
    )


# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    if message.author.bot:
        pass
    elif Prefix == message.content[0]:
        if message.content.upper() == f"{Prefix}RUNSERVER":
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
            return 0

        elif message.content.upper() == f"{Prefix}STOPSERVER":
            res = rq.get("http://27.91.71.82/commands/shutdown", headers=headers).json()
            if res["state"] == 1:
                await message.channel.send("終了処理が成功しました")
            else:
                if "error" in res:
                    await message.channel.send("リクエストに失敗しました。")
                else:
                    await message.channel.send("終了処理が失敗しました。")
            return 0

        elif message.content.upper() == f"{Prefix}HELP":
            Embed = discord.Embed(
                title="ヘルプ", description="ARK Bot使用可能コマンド一覧", color=0x2ECC69,
            )
            for Key, Values in CommandList.items():
                if type(Values) == list:
                    Text = ""
                    for Value in Values:
                        Text += f"{Prefix}{Value}\n"
                else:
                    Text = f"{Prefix}{Values}\n"
                Embed.add_field(name=f"{Key}コマンド", value=Text, inline=False)
                Embed.set_footer(text="コマンドは大文字小文字不問です。")
            await message.channel.send(embed=Embed)
            return 0

        hints = [
            Command
            for Command in list(itertools.chain.from_iterable(CommandList.values()))
            if difflib.SequenceMatcher(
                None, message.content.upper(), Prefix + Command
            ).ratio()
            >= 0.65
        ]

        if len(hints) > 0:
            Text = "Hint: もしかして以下のコマンドですか?\n"
            for n, hint in enumerate(hints):
                Text += f"{n+1}. {Prefix}{hint}\n"
            Text += "これ以外に使えるコマンドは /help で確認できます。"
            await message.channel.send(Text)
            return 0


client.run(TOKEN)
