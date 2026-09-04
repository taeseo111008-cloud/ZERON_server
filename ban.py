import discord
from discord.ext import commands


# ==========================================
# 역할 설정
# ==========================================

COMMAND_ROLE = "[권한]추방"

TARGET_ROLE = "추방 예정 인물"


# ==========================================
# 권한 확인
# ==========================================

def has_permission(member):

    if not isinstance(
        member,
        discord.Member
    ):

        return False


    # Discord 관리자 권한

    if member.guild_permissions.administrator:

        return True


    for role in member.roles:

        role_name = role.name.strip()


        # [권한]추방

        if role_name == COMMAND_ROLE:

            return True


        # 소유자

        if "소유자" in role_name:

            return True


    return False


# ==========================================
# 단속 Cog
# ==========================================

class Ban(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    # ==========================================
    # /인물추방
    # ==========================================

    @discord.app_commands.command(
        name="인물추방",
        description="추방 예정 인물을 킥 또는 밴합니다."
    )

    @discord.app_commands.describe(
        방식="킥 또는 밴 선택",
        사용자="대상 사용자 선택"
    )

    @discord.app_commands.choices(
        방식=[
            discord.app_commands.Choice(
                name="킥",
                value="kick"
            ),

            discord.app_commands.Choice(
                name="밴",
                value="ban"
            )
        ]
    )

    async def person_ban(

        self,

        interaction: discord.Interaction,

        방식: discord.app_commands.Choice[str],

        사용자: discord.Member

    ):


        실행자 = interaction.user


        # ==========================================
        # 서버 확인
        # ==========================================

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ 서버 내부에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return


        # ==========================================
        # 권한 확인
        # ==========================================

        if not has_permission(실행자):

            await interaction.response.send_message(
                "❌ 명령어 실행 권한이 없습니다.\n"
                "필요 권한: [권한]추방 / 소유자 / 부소유자",
                ephemeral=True
            )

            return


        # ==========================================
        # 대상 역할 확인
        # ==========================================

        if not any(
            role.name == TARGET_ROLE
            for role in 사용자.roles
        ):

            await interaction.response.send_message(
                f"❌ 대상에게 '{TARGET_ROLE}' 역할이 없습니다.",
                ephemeral=True
            )

            return


        # ==========================================
        # 자기 자신 방지
        # ==========================================

        if 사용자.id == 실행자.id:

            await interaction.response.send_message(
                "❌ 자기 자신에게 사용할 수 없습니다.",
                ephemeral=True
            )

            return


        # ==========================================
        # 봇 자신 방지
        # ==========================================

        if self.bot.user and 사용자.id == self.bot.user.id:

            await interaction.response.send_message(
                "❌ 봇 자신에게 사용할 수 없습니다.",
                ephemeral=True
            )

            return


        # ==========================================
        # 킥
        # ==========================================

        if 방식.value == "kick":

            try:

                await 사용자.kick(
                    reason=(
                        f"추방 명령 | 실행자: {실행자}"
                    )
                )

                await interaction.response.send_message(
                    f"👢 {사용자.mention} 사용자를 킥했습니다."
                )


            except discord.Forbidden:

                await interaction.response.send_message(
                    "❌ 킥에 실패했습니다.\n"
                    "봇에게 '멤버 추방' 권한이 있는지,\n"
                    "봇 역할이 대상보다 높은지 확인해주세요.",
                    ephemeral=True
                )


            except Exception as e:

                await interaction.response.send_message(
                    f"❌ 오류 발생: {e}",
                    ephemeral=True
                )


        # ==========================================
        # 밴
        # ==========================================

        elif 방식.value == "ban":

            try:

                await 사용자.ban(
                    reason=(
                        f"추방 명령 | 실행자: {실행자}"
                    )
                )

                await interaction.response.send_message(
                    f"🔨 {사용자.mention} 사용자를 밴했습니다."
                )


            except discord.Forbidden:

                await interaction.response.send_message(
                    "❌ 밴에 실패했습니다.\n"
                    "봇에게 '멤버 차단' 권한이 있는지,\n"
                    "봇 역할이 대상보다 높은지 확인해주세요.",
                    ephemeral=True
                )


            except Exception as e:

                await interaction.response.send_message(
                    f"❌ 오류 발생: {e}",
                    ephemeral=True
                )


# ==========================================
# Cog 등록
# ==========================================

async def setup(bot):

    await bot.add_cog(
        Ban(bot)
    )