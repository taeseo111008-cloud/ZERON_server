import discord
from discord.ext import commands
from discord import app_commands

import os
import json
import random


# ==========================================
# 기본 설정
# ==========================================

TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1518416294326833192

GUILD = discord.Object(id=GUILD_ID)


# ==========================================
# 토큰 확인
# ==========================================

if not TOKEN:

    print("=" * 50)
    print("❌ DISCORD_TOKEN 환경 변수가 없습니다.")
    print("배포 사이트 환경 변수에 토큰을 등록해주세요.")
    print("=" * 50)

    raise ValueError(
        "DISCORD_TOKEN 환경 변수가 설정되지 않았습니다."
    )


# ==========================================
# 봇 설정
# ==========================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================================
# 정보 데이터 설정
# ==========================================

DATA_FILE = "info_data.json"


def load_data():

    if not os.path.exists(DATA_FILE):
        return []

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except:

        return []


def save_data(data):

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
# 명언 목록
# ==========================================

QUOTES = [

    "성공은 작은 노력이 매일 반복되는 결과다.",

    "시작하지 않으면 아무것도 변하지 않는다.",

    "느리더라도 멈추지 않는 것이 중요하다.",

    "오늘의 작은 행동이 미래를 만든다.",

    "실패는 끝이 아니라 다음 시도를 위한 경험이다.",

    "할 수 있다고 생각하면 방법을 찾게 된다.",

    "계획만 하지 말고 작은 것부터 시작하자."

]


# ==========================================
# 경고 역할 설정
# ==========================================

WARNING_ROLES = [

    "경고 1",
    "경고 2",
    "경고 3",
    "경고 4",
    "경고 5"

]


# ==========================================
# 추방 역할 설정
# ==========================================

COMMAND_ROLE = "[권한]추방"

TARGET_ROLE = "추방 예정 인물"


# ==========================================
# 정보 관리자 권한 확인
# ==========================================

def has_info_permission(interaction):

    if not isinstance(
        interaction.user,
        discord.Member
    ):

        return False


    for role in interaction.user.roles:

        role_name = role.name.strip()


        if "소유자" in role_name:
            return True


        if "부소유자" in role_name:
            return True


        if role_name == "정보 관리자":
            return True


    return False


# ==========================================
# 경고 권한 확인
# ==========================================

def has_warning_permission(interaction):

    if not isinstance(
        interaction.user,
        discord.Member
    ):

        return False


    for role in interaction.user.roles:

        role_name = role.name.strip()


        if "소유자" in role_name:
            return True


        if "부소유자" in role_name:
            return True


        if role_name == "[권한]경고":
            return True


    return False


# ==========================================
# 추방 권한 확인
# ==========================================

def has_ban_permission(member):

    for role in member.roles:

        role_name = role.name.strip()


        if role_name == COMMAND_ROLE:
            return True


        if "소유자" in role_name:
            return True


        if "부소유자" in role_name:
            return True


    return False


# ==========================================
# 정보등록
# ==========================================

@bot.tree.command(
    name="정보등록",
    description="새로운 정보를 등록합니다."
)

@app_commands.describe(
    제목="정보 제목",
    내용="등록할 정보 내용"
)

async def info_add(

    interaction: discord.Interaction,

    제목: str,

    내용: str

):

    if not has_info_permission(interaction):

        await interaction.response.send_message(

            "❌ 정보 관리자 권한이 없습니다.",

            ephemeral=True

        )

        return


    data = load_data()


    # 중복 제목 확인
    for info in data:

        if info["title"] == 제목:

            await interaction.response.send_message(

                "❌ 이미 같은 제목의 정보가 존재합니다.",

                ephemeral=True

            )

            return


    # 새 ID 생성
    if not data:

        new_id = 1

    else:

        new_id = max(
            info["id"]
            for info in data
        ) + 1


    new_info = {

        "id": new_id,

        "title": 제목,

        "content": 내용,

        "author": interaction.user.id

    }


    data.append(new_info)

    save_data(data)


    embed = discord.Embed(

        title="📚 정보 등록 완료",

        description=(

            f"**ID:** {new_id}\n"
            f"**제목:** {제목}\n\n"
            f"{내용}"

        )

    )


    embed.set_footer(
        text=f"등록자: {interaction.user}"
    )


    await interaction.response.send_message(
        embed=embed
    )


# ==========================================
# 정보검색
# ==========================================

@bot.tree.command(
    name="정보검색",
    description="등록된 정보를 검색합니다."
)

@app_commands.describe(
    검색어="검색할 제목 또는 단어"
)

async def info_search(

    interaction: discord.Interaction,

    검색어: str

):

    data = load_data()

    results = []


    for info in data:

        if (

            검색어.lower()
            in info["title"].lower()

            or

            검색어.lower()
            in info["content"].lower()

        ):

            results.append(info)


    if not results:

        await interaction.response.send_message(

            "❌ 검색 결과가 없습니다.",

            ephemeral=True

        )

        return


    embed = discord.Embed(

        title=f"🔎 '{검색어}' 검색 결과"

    )


    for info in results[:10]:

        content = info["content"]


        if len(content) > 150:

            content = content[:150] + "..."


        embed.add_field(

            name=(
                f"[ID {info['id']}] "
                f"{info['title']}"
            ),

            value=content,

            inline=False

        )


    await interaction.response.send_message(
        embed=embed
    )


# ==========================================
# 정보목록
# ==========================================

@bot.tree.command(
    name="정보목록",
    description="등록된 정보 목록을 확인합니다."
)

async def info_list(
    interaction: discord.Interaction
):

    data = load_data()


    if not data:

        await interaction.response.send_message(

            "📭 등록된 정보가 없습니다."

        )

        return


    embed = discord.Embed(

        title="📚 등록된 정보 목록"

    )


    text = ""


    for info in data[:25]:

        text += (
            f"**{info['id']}.** "
            f"{info['title']}\n"
        )


    embed.description = text


    embed.set_footer(

        text=f"총 {len(data)}개의 정보"

    )


    await interaction.response.send_message(
        embed=embed
    )


# ==========================================
# 정보삭제
# ==========================================

@bot.tree.command(
    name="정보삭제",
    description="등록된 정보를 삭제합니다."
)

@app_commands.describe(
    정보id="삭제할 정보 ID"
)

async def info_delete(

    interaction: discord.Interaction,

    정보id: int

):

    if not has_info_permission(interaction):

        await interaction.response.send_message(

            "❌ 정보 관리자 권한이 없습니다.",

            ephemeral=True

        )

        return


    data = load_data()

    target = None


    for info in data:

        if info["id"] == 정보id:

            target = info

            break


    if target is None:

        await interaction.response.send_message(

            "❌ 해당 ID의 정보를 찾을 수 없습니다.",

            ephemeral=True

        )

        return


    data.remove(target)

    save_data(data)


    await interaction.response.send_message(

        f"🗑️ 정보 삭제 완료\n"
        f"삭제된 정보: **{target['title']}**"

    )


# ==========================================
# 오늘의 명언
# ==========================================

@bot.tree.command(
    name="오늘의명언",
    description="랜덤 명언을 보여줍니다."
)

async def today_quote(
    interaction: discord.Interaction
):

    quote = random.choice(QUOTES)


    embed = discord.Embed(

        title="💬 오늘의 명언",

        description=f"> {quote}"

    )


    embed.set_footer(
        text="오늘도 좋은 하루 보내세요!"
    )


    await interaction.response.send_message(
        embed=embed
    )


# ==========================================
# 정보퀴즈
# ==========================================

@bot.tree.command(
    name="정보퀴즈",
    description="등록된 정보에서 랜덤 퀴즈를 생성합니다."
)

async def info_quiz(
    interaction: discord.Interaction
):

    data = load_data()


    if not data:

        await interaction.response.send_message(

            "❌ 퀴즈를 만들 정보가 없습니다."

        )

        return


    info = random.choice(data)


    embed = discord.Embed(

        title="🧠 정보 퀴즈",

        description=(

            "다음 내용에 해당하는 정보의 "
            "제목은 무엇일까요?\n\n"

            f"```{info['content']}```"

        )

    )


    await interaction.response.send_message(
        embed=embed
    )


    await interaction.followup.send(

        f"💡 정답: **{info['title']}**"

    )


# ==========================================
# 경고 지급
# ==========================================

@bot.tree.command(
    name="경고",
    description="사용자에게 경고를 지급합니다."
)

async def warning(

    interaction: discord.Interaction,

    대상: discord.Member

):

    if not has_warning_permission(interaction):

        await interaction.response.send_message(

            "❌ 명령어 실행 권한이 없습니다.",

            ephemeral=True

        )

        return


    member = 대상
    guild = interaction.guild


    if member.bot:

        await interaction.response.send_message(

            "❌ 봇에게는 경고를 지급할 수 없습니다.",

            ephemeral=True

        )

        return


    current_warning = 0
    current_role = None


    for i, role_name in enumerate(WARNING_ROLES):

        role = discord.utils.get(
            guild.roles,
            name=role_name
        )


        if role in member.roles:

            current_warning = i + 1
            current_role = role

            break


    if current_warning >= 5:

        await interaction.response.send_message(

            f"⚠️ {member.mention} 님은 "
            f"이미 최대 경고 단계입니다. (경고 5)",

            ephemeral=True

        )

        return


    next_warning = current_warning + 1

    next_role_name = WARNING_ROLES[
        next_warning - 1
    ]


    next_role = discord.utils.get(

        guild.roles,

        name=next_role_name

    )


    if next_role is None:

        await interaction.response.send_message(

            f"❌ `{next_role_name}` 역할을 "
            f"찾을 수 없습니다.",

            ephemeral=True

        )

        return


    try:

        if current_role:

            await member.remove_roles(
                current_role
            )


        await member.add_roles(

            next_role,

            reason=(
                f"{interaction.user} 님이 "
                f"경고 {next_warning} 지급"
            )

        )


        embed = discord.Embed(

            title="⚠️ 경고 지급",

            description=(

                f"대상: {member.mention}\n"
                f"현재 경고: **경고 {next_warning}**"

            )

        )


        embed.set_footer(
            text=f"처리자: {interaction.user}"
        )


        await interaction.response.send_message(
            embed=embed
        )


    except discord.Forbidden:

        await interaction.response.send_message(

            "❌ 역할 지급에 실패했습니다.\n"
            "봇 역할 위치와 권한을 확인해주세요.",

            ephemeral=True

        )


# ==========================================
# 경고 회수
# ==========================================

@bot.tree.command(
    name="경고회수",
    description="사용자의 경고를 1단계 회수합니다."
)

async def warning_remove(

    interaction: discord.Interaction,

    대상: discord.Member

):

    if not has_warning_permission(interaction):

        await interaction.response.send_message(

            "❌ 명령어 실행 권한이 없습니다.",

            ephemeral=True

        )

        return


    member = 대상
    guild = interaction.guild


    current_warning = 0
    current_role = None


    for i, role_name in enumerate(WARNING_ROLES):

        role = discord.utils.get(
            guild.roles,
            name=role_name
        )


        if role in member.roles:

            current_warning = i + 1
            current_role = role

            break


    if current_warning == 0:

        await interaction.response.send_message(

            f"❌ {member.mention} 님은 "
            f"현재 경고가 없습니다.",

            ephemeral=True

        )

        return


    try:

        await member.remove_roles(
            current_role
        )


        new_warning = current_warning - 1


        if new_warning > 0:

            previous_role_name = WARNING_ROLES[
                new_warning - 1
            ]


            previous_role = discord.utils.get(

                guild.roles,

                name=previous_role_name

            )


            if previous_role:

                await member.add_roles(
                    previous_role
                )


        if new_warning == 0:

            result = "경고 없음"

        else:

            result = f"경고 {new_warning}"


        embed = discord.Embed(

            title="✅ 경고 회수",

            description=(

                f"대상: {member.mention}\n"
                f"변경 후: **{result}**"

            )

        )


        embed.set_footer(
            text=f"처리자: {interaction.user}"
        )


        await interaction.response.send_message(
            embed=embed
        )


    except discord.Forbidden:

        await interaction.response.send_message(

            "❌ 역할 변경에 실패했습니다.",

            ephemeral=True

        )


# ==========================================
# 경고 확인
# ==========================================

@bot.tree.command(
    name="경고확인",
    description="사용자의 현재 경고 상태를 확인합니다."
)

async def warning_check(

    interaction: discord.Interaction,

    대상: discord.Member

):

    member = 대상
    guild = interaction.guild

    current_warning = 0


    for i, role_name in enumerate(WARNING_ROLES):

        role = discord.utils.get(
            guild.roles,
            name=role_name
        )


        if role in member.roles:

            current_warning = i + 1

            break


    if current_warning == 0:

        result = "경고 없음"

    else:

        result = f"경고 {current_warning}"


    embed = discord.Embed(

        title="📋 경고 확인",

        description=(

            f"대상: {member.mention}\n"
            f"현재 상태: **{result}**"

        )

    )


    await interaction.response.send_message(
        embed=embed
    )


# ==========================================
# 인물 추방
# ==========================================

@bot.tree.command(
    name="인물추방",
    description="추방 예정 인물을 킥 또는 밴합니다."
)

@app_commands.describe(
    방식="킥 또는 밴 선택",
    사용자="대상 사용자 선택"
)

@app_commands.choices(

    방식=[

        app_commands.Choice(
            name="킥",
            value="kick"
        ),

        app_commands.Choice(
            name="밴",
            value="ban"
        )

    ]

)

async def ban_member(

    interaction: discord.Interaction,

    방식: app_commands.Choice[str],

    사용자: discord.Member

):

    실행자 = interaction.user


    if not isinstance(
        실행자,
        discord.Member
    ):

        await interaction.response.send_message(

            "❌ 서버 내부에서만 사용할 수 있습니다.",

            ephemeral=True

        )

        return


    if not has_ban_permission(실행자):

        await interaction.response.send_message(

            "❌ 명령어 실행 권한이 없습니다.\n"
            "필요 권한: [권한]추방 / 소유자 / 부소유자",

            ephemeral=True

        )

        return


    if not any(

        role.name == TARGET_ROLE

        for role in 사용자.roles

    ):

        await interaction.response.send_message(

            f"❌ 대상에게 "
            f"'{TARGET_ROLE}' 역할이 없습니다.",

            ephemeral=True

        )

        return


    if 사용자.id == 실행자.id:

        await interaction.response.send_message(

            "❌ 자기 자신에게 사용할 수 없습니다.",

            ephemeral=True

        )

        return


    if 사용자.bot:

        await interaction.response.send_message(

            "❌ 봇에게 사용할 수 없습니다.",

            ephemeral=True

        )

        return


    # 킥
    if 방식.value == "kick":

        try:

            await 사용자.kick(

                reason=(
                    f"추방 명령 | "
                    f"실행자: {실행자}"
                )

            )


            await interaction.response.send_message(

                f"👢 {사용자.mention} "
                f"사용자를 킥했습니다."

            )


        except discord.Forbidden:

            await interaction.response.send_message(

                "❌ 킥에 실패했습니다.\n"
                "봇 권한과 역할 순서를 확인해주세요.",

                ephemeral=True

            )


    # 밴
    elif 방식.value == "ban":

        try:

            await 사용자.ban(

                reason=(
                    f"추방 명령 | "
                    f"실행자: {실행자}"
                )

            )


            await interaction.response.send_message(

                f"🔨 {사용자.mention} "
                f"사용자를 밴했습니다."

            )


        except discord.Forbidden:

            await interaction.response.send_message(

                "❌ 밴에 실패했습니다.\n"
                "봇 권한과 역할 순서를 확인해주세요.",

                ephemeral=True

            )


# ==========================================
# 봇 시작 준비
# ==========================================

@bot.event
async def setup_hook():

    print("=" * 40)
    print("슬래시 명령어 동기화 중...")
    print("=" * 40)


    try:

        bot.tree.copy_global_to(
            guild=GUILD
        )


        synced = await bot.tree.sync(
            guild=GUILD
        )


        print(
            f"✅ 슬래시 명령어 "
            f"{len(synced)}개 동기화 완료"
        )


    except Exception as e:

        print(
            f"❌ 명령어 동기화 오류: {e}"
        )


# ==========================================
# 봇 준비 완료
# ==========================================

@bot.event
async def on_ready():

    await bot.change_presence(

        status=discord.Status.online,

        activity=discord.Game(
            name="정보와 서버를 관리하는 중"
        )

    )


    print("=" * 40)
    print("🤖 연결이 배포 서버 실행 완료")
    print(f"로그인 성공: {bot.user}")
    print(f"봇 ID: {bot.user.id}")
    print(f"서버 수: {len(bot.guilds)}")
    print("=" * 40)


# ==========================================
# 봇 실행
# ==========================================

bot.run(TOKEN)