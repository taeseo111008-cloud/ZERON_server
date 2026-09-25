import os
import asyncio
import threading

import discord
from dotenv import load_dotenv


class DiscordModule:

    name = "DISCORD"

    def __init__(self):
        self.nexus = None
        self.bot = None
        self.thread = None
        self.loop = None
        self.running = False
        self.connected = False

        load_dotenv()

        self.token = os.getenv("DISCORD_TOKEN")

        intents = discord.Intents.default()
        intents.message_content = True

        self.bot = discord.Client(intents=intents)

        @self.bot.event
        async def on_ready():
            self.connected = True

            if self.nexus:
                self.nexus.info(
                    f"DISCORD CONNECTED: {self.bot.user}"
                )

                await self.send_message(
                    "🟢 **NEXUS ONLINE**\n"
                    f"`{self.nexus.version}` 시스템이 시작되었습니다."
                )

    def start(self, nexus):
        self.nexus = nexus

        if not self.token:
            self.nexus.error(
                "DISCORD TOKEN NOT FOUND"
            )
            self.nexus.warning(
                "Create a .env file and set DISCORD_TOKEN"
            )
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._run_bot,
            daemon=True
        )

        self.thread.start()

        self.nexus.info(
            "DISCORD MODULE STARTING"
        )

    def _run_bot(self):
        try:
            asyncio.run(
                self._bot_main()
            )

        except Exception as error:
            if self.nexus:
                self.nexus.error(
                    f"DISCORD BOT ERROR: {error}"
                )

    async def _bot_main(self):
        self.loop = asyncio.get_running_loop()

        try:
            await self.bot.start(
                self.token
            )

        except Exception as error:
            if self.nexus:
                self.nexus.error(
                    f"DISCORD CONNECTION FAILED: {error}"
                )

    async def send_message(self, message):
        if not self.connected:
            return False

        for guild in self.bot.guilds:
            for channel in guild.text_channels:

                permissions = channel.permissions_for(
                    guild.me
                )

                if permissions.send_messages:
                    try:
                        await channel.send(message)
                        return True

                    except Exception:
                        continue

        return False

    def send(self, message):
        if not self.loop:
            return False

        try:
            future = asyncio.run_coroutine_threadsafe(
                self.send_message(message),
                self.loop
            )

            return future.result(
                timeout=5
            )

        except Exception as error:
            if self.nexus:
                self.nexus.error(
                    f"DISCORD SEND FAILED: {error}"
                )

            return False

    def stop(self, nexus):
        self.running = False

        if self.bot and self.loop:
            try:
                future = asyncio.run_coroutine_threadsafe(
                    self.bot.close(),
                    self.loop
                )

                future.result(
                    timeout=5
                )

            except Exception as error:
                nexus.error(
                    f"DISCORD SHUTDOWN FAILED: {error}"
                )

        self.connected = False

        nexus.info(
            "DISCORD MODULE STOPPED"
        )