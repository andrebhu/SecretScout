#!/usr/bin/env python3
import os
import json
import time
import flask
import asyncio
import discord
import requests
import subprocess

from flask import Flask
from discord import Embed
from itertools import cycle
from threading import Thread
from dotenv import load_dotenv
from discord.ext import commands, tasks


from scanner import scan_org

load_dotenv()

# Set client's prefix
client = commands.Bot(command_prefix="/")
client.remove_command('help')


class Scanner:    
    def __init__(self):
        self.ready = True
        self.current = ""

    async def scan(self, name, ctx):
        if self.ready:
            self.ready = False
            self.current = name

            await ctx.send(f"> Starting to scan {name}!")

            # Conduct scan here
            await scan_org(name, ctx)


            print(f"Finished {name}!")
            await ctx.send(f"> Finished scanning {name}!")

            self.ready = True
            self.current = ""
        else:
            return False

    async def getStatus(self):
        return self.ready



scanner = Scanner()
orgs = []  # acting as a queue



@tasks.loop(seconds=15)
async def task():
    try:
        if await scanner.getStatus():
            r = orgs.pop(0)
            await scanner.scan(r[0], r[1])
        else:
            # Scanner is still scanning
            print(f"Scanner is still scanning {scanner.current}")
            pass

    except:
        # If orgs is empty
        print("Queue is empty.")
        pass


@client.command(name="scan")
async def scan(ctx, arg):
    url = "https://github.com/"

    with requests.get(url + str(arg)) as r:
        if int(r.status_code) == 404:
            await ctx.send(f"> Invalid org name")
            return

    orgs.append((arg, ctx))
    await ctx.send(f"> Added {arg} to the queue")



@client.command(name="list")
async def list(ctx):
    
    data = '\n'.join([o[0] for o in orgs])
    message = '**Queue:**\n>>> {}'.format(data)

    await ctx.send(message)
    # await ctx.send([r[0] for r in orgs])



@client.command(name="status")
async def current(ctx):
    if scanner.ready:
        await ctx.send(f"**Status:**\n> Ready!")
    else:
        await ctx.send(f"> **Status:**\n> Scanning **{scanner.current}**")


@client.command(name="help")
async def help(ctx):
    embed = Embed(
        title="Commands",
        description="List of commands",
    )
    embed.add_field(name="/scan", value="Add org name to queue", inline=False)
    embed.add_field(name="/list", value="Lists queue", inline=False)
    embed.add_field(name="/status", value="Scanner status", inline=False)
    await ctx.send(embed=embed)



@client.event
async def on_ready():
    task.start()
    print(f"Logged in as {client.user}!")


app = Flask(__name__)


@app.route("/")
def index():
    return "Hello, World!"


def server():
    app.run(host='0.0.0.0', port=8080)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(client.start(os.getenv("DISCORD_TOKEN")))

    Thread(target=loop.run_forever).start()

    t = Thread(target=server)
    t.start()
    t.join()