import discord
from discord.ext import commands

import json
import os
import random

from datetime import datetime


# ==========================================
# 기본 설정
# ==========================================

ADMIN_ROLE_NAME = "정보 관리자"

DATA_FILE = "info_data.json"


# ==========================================
# 기본 정보 데이터
# ==========================================

def create_default_data():

    return {

        "last_id": 3,

        "infos": {

            "1": {
                "title": "드론",
                "description": "무선 조종 또는 자동 비행이 가능한 무인 항공기입니다.",
                "related_tech": "GPS, RTK, 비행제어장치",
                "category": "항공, 촬영, 측량",
                "author_id": 0,
                "author_name": "시스템",
                "created_at": "2026-08-31"
            },

            "2": {
                "title": "RTK",
                "description": "위성 위치 정보를 실시간으로 보정하여 높은 정밀도의 위치 측정을 가능하게 하는 기술입니다.",
                "related_tech": "GPS, GNSS, 기준국",
                "category": "드론, 측량, 자율주행",
                "author_id": 0,
                "author_name": "시스템",
                "created_at": "2026-08-31"
            },

            "3": {
                "title": "GPS",
                "description": "위성을 이용하여 위치 정보를 확인하는 위성 항법 시스템입니다.",
                "related_tech": "GNSS, RTK",
                "category": "드론, 자동차, 스마트폰",
                "author_id": 0,
                "author_name": "시스템",
                "created_at": "2026-08-31"
            }
        },

        "deleted_infos": {}
    }


# ==========================================
# 전체 데이터 불러오기
# ==========================================

def load_all_data():

    if not os.path.exists(DATA_FILE):

        return {
            "guilds": {}
        }

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if "guilds" not in data:

            return {
                "guilds": {}
            }

        return data

    except Exception as e:

        print(f"데이터 불러오기 오류: {e}")

        return {
            "guilds": {}
        }


# ==========================================
# 전체 데이터 저장
# ==========================================

def save_all_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


# ==========================================
# 데이터 로드
# ==========================================

ALL_DATA = load_all_data()


# ==========================================
# 서버별 데이터 가져오기
# ==========================================

def get_guild_data(guild_id):

    guild_id = str(guild_id)

    if guild_id not in ALL_DATA["guilds"]:

        ALL_DATA["guilds"][guild_id] = (
            create_default_data()
        )

        save_all_data(ALL_DATA)

    return ALL_DATA["guilds"][guild_id]


# ==========================================
# 관리자 확인
# ==========================================

def is_admin(member):

    if not isinstance(member, discord.Member):

        return False

    # Discord 관리자 권한

    if member.guild_permissions.administrator:

        return True

    # 역할 확인

    for role in member.roles:

        role_name = role.name

        if role_name == ADMIN_ROLE_NAME:

            return True

        if "소유자" in role_name:

            return True

    return False


# ==========================================
# 정보 Embed 생성
# ==========================================

def create_info_embed(info_id, info):

    embed = discord.Embed(
        title=f"📌 {info['title']}",
        description=info["description"],
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🆔 정보 ID",
        value=f"#{info_id}",
        inline=True
    )

    embed.add_field(
        name="✍️ 작성자",
        value=info["author_name"],
        inline=True
    )

    embed.add_field(
        name="🔧 관련 기술",
        value=info["related_tech"],
        inline=False
    )

    embed.add_field(
        name="📚 관련 분야",
        value=info["category"],
        inline=False
    )

    embed.add_field(
        name="📅 등록일",
        value=info["created_at"],
        inline=False
    )

    return embed


# ==========================================
# 인포리 Cog
# ==========================================

class Info(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    # ==========================================
    # /정보검색
    # ==========================================

    @discord.app_commands.command(
        name="정보검색",
        description="등록된 정보를 검색합니다."
    )

    @discord.app_commands.describe(
        keyword="검색할 키워드를 입력하세요."
    )

    @discord.app_commands.rename(
        keyword="검색어"
    )

    async def info_search(
        self,
        interaction: discord.Interaction,
        keyword: str
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ 서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return

        data = get_guild_data(
            interaction.guild.id
        )

        keyword = keyword.strip().lower()

        results = []

        for info_id, info in data["infos"].items():

            if (
                keyword in info["title"].lower()
                or keyword in info["description"].lower()
                or keyword in info["related_tech"].lower()
                or keyword in info["category"].lower()
            ):

                results.append(
                    (info_id, info)
                )

        if not results:

            await interaction.response.send_message(
                f"❌ `{keyword}`에 대한 정보를 찾지 못했습니다."
            )

            return

        if len(results) == 1:

            info_id, info = results[0]

            await interaction.response.send_message(
                embed=create_info_embed(
                    info_id,
                    info
                )
            )

            return

        result_text = ""

        for info_id, info in results[:10]:

            result_text += (
                f"**#{info_id} | {info['title']}**\n"
                f"작성자: {info['author_name']}\n\n"
            )

        embed = discord.Embed(
            title=f"🔎 '{keyword}' 검색 결과",
            description=result_text,
            color=discord.Color.blue()
        )

        embed.set_footer(
            text=f"총 {len(results)}개의 정보를 찾았습니다."
        )

        await interaction.response.send_message(
            embed=embed
        )


    # ==========================================
    # /오늘의정보
    # ==========================================

    @discord.app_commands.command(
        name="오늘의정보",
        description="등록된 정보 중 랜덤으로 하나를 보여줍니다."
    )

    async def today_info(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ 서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return

        data = get_guild_data(
            interaction.guild.id
        )

        if not data["infos"]:

            await interaction.response.send_message(
                "📭 등록된 정보가 없습니다."
            )

            return

        info_id = random.choice(
            list(data["infos"].keys())
        )

        info = data["infos"][info_id]

        embed = create_info_embed(
            info_id,
            info
        )

        embed.title = (
            f"📌 오늘의 정보 | {info['title']}"
        )

        embed.color = discord.Color.green()

        await interaction.response.send_message(
            embed=embed
        )


    # ==========================================
    # /정보목록
    # ==========================================

    @discord.app_commands.command(
        name="정보목록",
        description="등록된 정보 목록을 확인합니다."
    )

    async def info_list(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ 서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return

        data = get_guild_data(
            interaction.guild.id
        )

        if not data["infos"]:

            await interaction.response.send_message(
                "📭 등록된 정보가 없습니다."
            )

            return

        result_text = ""

        for info_id, info in data["infos"].items():

            result_text += (
                f"**#{info_id} | {info['title']}**\n"
                f"작성자: {info['author_name']}\n\n"
            )

        embed = discord.Embed(
            title="📚 등록된 정보 목록",
            description=result_text,
            color=discord.Color.purple()
        )

        embed.set_footer(
            text=f"총 {len(data['infos'])}개의 정보"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # ==========================================
    # /정보등록
    # ==========================================

    @discord.app_commands.command(
        name="정보등록",
        description="새로운 정보를 등록합니다."
    )

    @discord.app_commands.describe(
        topic="등록할 정보의 제목",
        info_description="정보에 대한 설명",
        related_tech="관련 기술 또는 키워드",
        category="관련 분야"
    )

    @discord.app_commands.rename(
        topic="주제",
        info_description="설명",
        related_tech="관련기술",
        category="분야"
    )

    async def info_add(
        self,
        interaction: discord.Interaction,
        topic: str,
        info_description: str,
        related_tech: str,
        category: str
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ 서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return

        data = get_guild_data(
            interaction.guild.id
        )

        data["last_id"] += 1

        new_id = str(
            data["last_id"]
        )

        data["infos"][new_id] = {

            "title": topic.strip(),

            "description": (
                info_description.strip()
            ),

            "related_tech": (
                related_tech.strip()
            ),

            "category": (
                category.strip()
            ),

            "author_id": interaction.user.id,

            "author_name": (
                interaction.user.display_name
            ),

            "created_at": (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            )
        }

        save_all_data(ALL_DATA)

        await interaction.response.send_message(
            f"✅ 새로운 정보가 등록되었습니다!\n\n"
            f"🆔 정보 ID: **#{new_id}**\n"
            f"📌 주제: **{topic}**"
        )


    # ==========================================
    # /정보수정
    # ==========================================

    @discord.app_commands.command(
        name="정보수정",
        description="자신이 등록한 정보를 수정합니다."
    )

    @discord.app_commands.describe(
        info_id="수정할 정보의 ID",
        new_description="새로운 정보 설명"
    )

    @discord.app_commands.rename(
        info_id="정보아이디",
        new_description="새로운설명"
    )

    async def info_edit(
        self,
        interaction: discord.Interaction,
        info_id: int,
        new_description: str
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ 서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return

        data = get_guild_data(
            interaction.guild.id
        )

        info_id = str(info_id)

        if info_id not in data["infos"]:

            await interaction.response.send_message(
                "❌ 해당 정보 ID를 찾을 수 없습니다.",
                ephemeral=True
            )

            return

        info = data["infos"][info_id]

        if (
            info["author_id"] != interaction.user.id
            and not is_admin(interaction.user)
        ):

            await interaction.response.send_message(
                "❌ 자신의 정보만 수정할 수 있습니다.",
                ephemeral=True
            )

            return

        info["description"] = (
            new_description.strip()
        )

        save_all_data(ALL_DATA)

        await interaction.response.send_message(
            f"✏️ 정보 **#{info_id} | {info['title']}** 수정 완료!"
        )


    # ==========================================
    # /정보삭제
    # ==========================================

    @discord.app_commands.command(
        name="정보삭제",
        description="정보를 삭제하고 휴지통으로 이동합니다."
    )

    @discord.app_commands.describe(
        info_id="삭제할 정보의 ID"
    )

    @discord.app_commands.rename(
        info_id="정보아이디"
    )

    async def info_delete(
        self,
        interaction: discord.Interaction,
        info_id: int
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ 서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return

        data = get_guild_data(
            interaction.guild.id
        )

        info_id = str(info_id)

        if info_id not in data["infos"]:

            await interaction.response.send_message(
                "❌ 해당 정보 ID를 찾을 수 없습니다.",
                ephemeral=True
            )

            return

        info = data["infos"][info_id]

        if (
            info["author_id"] != interaction.user.id
            and not is_admin(interaction.user)
        ):

            await interaction.response.send_message(
                "❌ 자신의 정보만 삭제할 수 있습니다.",
                ephemeral=True
            )

            return

        info["deleted_by"] = (
            interaction.user.display_name
        )

        info["deleted_at"] = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        )

        data["deleted_infos"][info_id] = info

        del data["infos"][info_id]

        save_all_data(ALL_DATA)

        await interaction.response.send_message(
            f"🗑️ 정보 **#{info_id} | {info['title']}**가 "
            f"휴지통으로 이동했습니다."
        )


    # ==========================================
    # /삭제정보목록
    # ==========================================

    @discord.app_commands.command(
        name="삭제정보목록",
        description="휴지통에 있는 정보를 확인합니다."
    )

    async def deleted_info_list(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ 서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return

        if not is_admin(interaction.user):

            await interaction.response.send_message(
                "❌ 관리자만 사용할 수 있습니다.",
                ephemeral=True
            )

            return

        data = get_guild_data(
            interaction.guild.id
        )

        if not data["deleted_infos"]:

            await interaction.response.send_message(
                "🗑️ 휴지통이 비어있습니다."
            )

            return

        result_text = ""

        for info_id, info in data[
            "deleted_infos"
        ].items():

            result_text += (
                f"**#{info_id} | {info['title']}**\n"
                f"원래 작성자: {info['author_name']}\n"
                f"삭제한 사람: "
                f"{info.get('deleted_by', '알 수 없음')}\n\n"
            )

        embed = discord.Embed(
            title="🗑️ 삭제된 정보 목록",
            description=result_text,
            color=discord.Color.red()
        )

        embed.set_footer(
            text=(
                f"총 {len(data['deleted_infos'])}개의 "
                f"삭제된 정보"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )


    # ==========================================
    # /정보복구
    # ==========================================

    @discord.app_commands.command(
        name="정보복구",
        description="휴지통의 정보를 복구합니다."
    )

    @discord.app_commands.describe(
        info_id="복구할 정보의 ID"
    )

    @discord.app_commands.rename(
        info_id="정보아이디"
    )

    async def info_restore(
        self,
        interaction: discord.Interaction,
        info_id: int
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ 서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return

        if not is_admin(interaction.user):

            await interaction.response.send_message(
                "❌ 관리자만 정보를 복구할 수 있습니다.",
                ephemeral=True
            )

            return

        data = get_guild_data(
            interaction.guild.id
        )

        info_id = str(info_id)

        if info_id not in data["deleted_infos"]:

            await interaction.response.send_message(
                "❌ 휴지통에서 해당 정보를 찾을 수 없습니다.",
                ephemeral=True
            )

            return

        info = data["deleted_infos"][info_id]

        info.pop("deleted_by", None)

        info.pop("deleted_at", None)

        data["infos"][info_id] = info

        del data["deleted_infos"][info_id]

        save_all_data(ALL_DATA)

        await interaction.response.send_message(
            f"♻️ 정보 **#{info_id} | {info['title']}** 복구 완료!"
        )


# ==========================================
# Cog 등록
# ==========================================

async def setup(bot):

    await bot.add_cog(
        Info(bot)
    )