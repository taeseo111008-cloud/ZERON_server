import discord
from discord.ext import commands


# ==========================================
# 기본 설정
# ==========================================

TOKEN = input("봇 토큰 입력: ").strip()

GUILD_ID = 1518416294326833192

GUILD = discord.Object(id=GUILD_ID)


# ==========================================
# Discord 봇 설정
# ==========================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================================
# 기능 파일 목록
# ==========================================

EXTENSIONS = [
    "info",
    "caution",
    "ban"
]


# ==========================================
# 봇 시작 준비
# ==========================================

@bot.event
async def setup_hook():

    print("=" * 40)
    print("기능 파일 불러오는 중...")
    print("=" * 40)

    # 기능 파일 불러오기
    for extension in EXTENSIONS:

        try:

            await bot.load_extension(extension)

            print(
                f"✅ {extension}.py 로드 완료"
            )

        except Exception as e:

            print(
                f"❌ {extension}.py 로드 실패"
            )

            print(
                f"오류 내용: {type(e).__name__}: {e}"
            )


    # ==========================================
    # 슬래시 명령어 동기화
    # ==========================================

    try:

        # 모든 명령어를 이 서버에 등록
        bot.tree.copy_global_to(
            guild=GUILD
        )

        # Discord 서버와 동기화
        synced = await bot.tree.sync(
            guild=GUILD
        )

        print("=" * 40)

        print(
            f"✅ 슬래시 명령어 "
            f"{len(synced)}개 동기화 완료"
        )

        print("=" * 40)


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
    print("🤖 통합 봇 실행 완료")
    print(f"로그인 성공: {bot.user}")
    print(f"봇 ID: {bot.user.id}")
    print(f"서버 수: {len(bot.guilds)}")
    print("=" * 40)


# ==========================================
# 봇 실행
# ==========================================

bot.run(TOKEN)