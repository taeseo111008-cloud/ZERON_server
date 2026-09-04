import discord
from discord.ext import commands


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
# 권한 확인
# ==========================================

def is_admin(interaction):

    if not isinstance(
        interaction.user,
        discord.Member
    ):

        return False

    # Discord 관리자 권한

    if interaction.user.guild_permissions.administrator:

        return True

    # 역할 확인

    for role in interaction.user.roles:

        role_name = role.name

        # 소유자

        if "소유자" in role_name:

            return True

        # 경고 권한

        if role_name == "[권한]경고":

            return True

    return False


# ==========================================
# 경고 Cog
# ==========================================

class Caution(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    # ==========================================
    # /경고
    # ==========================================

    @discord.app_commands.command(
        name="경고",
        description="사용자에게 경고를 지급합니다."
    )

    async def warning(
        self,
        interaction: discord.Interaction,
        대상: discord.Member
    ):

        if not is_admin(interaction):

            await interaction.response.send_message(
                "❌ 관리자만 사용할 수 있는 명령어입니다.",
                ephemeral=True
            )

            return

        member = 대상

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ 서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return

        # 봇 방지

        if member.bot:

            await interaction.response.send_message(
                "❌ 봇에게는 경고를 지급할 수 없습니다.",
                ephemeral=True
            )

            return


        # ==========================================
        # 현재 경고 확인
        # ==========================================

        current_warning = 0

        current_role = None

        for i, role_name in enumerate(
            WARNING_ROLES
        ):

            role = discord.utils.get(
                guild.roles,
                name=role_name
            )

            if role in member.roles:

                current_warning = i + 1

                current_role = role

                break


        # ==========================================
        # 최대 경고 확인
        # ==========================================

        if current_warning >= 5:

            await interaction.response.send_message(
                f"⚠️ {member.mention} 님은 이미 "
                f"최대 경고 단계입니다. (경고 5)",
                ephemeral=True
            )

            return


        # ==========================================
        # 다음 경고 역할
        # ==========================================

        next_warning = current_warning + 1

        next_role_name = WARNING_ROLES[
            next_warning - 1
        ]

        next_role = discord.utils.get(
            guild.roles,
            name=next_role_name
        )


        # 역할 없음

        if next_role is None:

            await interaction.response.send_message(
                f"❌ `{next_role_name}` 역할을 찾을 수 없습니다.\n"
                f"먼저 서버에 해당 역할을 만들어주세요.",
                ephemeral=True
            )

            return


        # ==========================================
        # 기존 경고 제거
        # ==========================================

        if current_role:

            await member.remove_roles(
                current_role,
                reason=(
                    f"{interaction.user} 님이 "
                    f"경고 단계 변경"
                )
            )


        # ==========================================
        # 새로운 경고 지급
        # ==========================================

        await member.add_roles(
            next_role,
            reason=(
                f"{interaction.user} 님이 "
                f"경고 {next_warning} 지급"
            )
        )


        # ==========================================
        # 결과
        # ==========================================

        embed = discord.Embed(
            title="⚠️ 경고 지급",
            description=(
                f"대상: {member.mention}\n"
                f"현재 경고: **경고 {next_warning}**"
            ),
            color=discord.Color.orange()
        )

        embed.set_footer(
            text=f"처리자: {interaction.user}"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # ==========================================
    # /경고회수
    # ==========================================

    @discord.app_commands.command(
        name="경고회수",
        description="사용자의 경고를 1단계 회수합니다."
    )

    async def warning_remove(
        self,
        interaction: discord.Interaction,
        대상: discord.Member
    ):

        if not is_admin(interaction):

            await interaction.response.send_message(
                "❌ 관리자만 사용할 수 있는 명령어입니다.",
                ephemeral=True
            )

            return

        member = 대상

        guild = interaction.guild

        if guild is None:

            return


        # ==========================================
        # 현재 경고 확인
        # ==========================================

        current_warning = 0

        current_role = None

        for i, role_name in enumerate(
            WARNING_ROLES
        ):

            role = discord.utils.get(
                guild.roles,
                name=role_name
            )

            if role in member.roles:

                current_warning = i + 1

                current_role = role

                break


        # 경고 없음

        if current_warning == 0:

            await interaction.response.send_message(
                f"❌ {member.mention} 님은 "
                f"현재 경고가 없습니다.",
                ephemeral=True
            )

            return


        # ==========================================
        # 현재 역할 제거
        # ==========================================

        await member.remove_roles(
            current_role,
            reason=(
                f"{interaction.user} 님이 경고 회수"
            )
        )


        # ==========================================
        # 이전 경고 지급
        # ==========================================

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
                    previous_role,
                    reason="경고 단계 감소"
                )


        # 결과

        if new_warning == 0:

            result = "경고 없음"

        else:

            result = f"경고 {new_warning}"


        embed = discord.Embed(
            title="✅ 경고 회수",
            description=(
                f"대상: {member.mention}\n"
                f"변경 후: **{result}**"
            ),
            color=discord.Color.green()
        )

        embed.set_footer(
            text=f"처리자: {interaction.user}"
        )

        await interaction.response.send_message(
            embed=embed
        )


    # ==========================================
    # /경고확인
    # ==========================================

    @discord.app_commands.command(
        name="경고확인",
        description="사용자의 현재 경고 상태를 확인합니다."
    )

    async def warning_check(
        self,
        interaction: discord.Interaction,
        대상: discord.Member
    ):

        member = 대상

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ 서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )

            return


        # 현재 경고 확인

        current_warning = 0

        for i, role_name in enumerate(
            WARNING_ROLES
        ):

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
            ),
            color=discord.Color.blue()
        )

        await interaction.response.send_message(
            embed=embed
        )


# ==========================================
# Cog 등록
# ==========================================

async def setup(bot):

    await bot.add_cog(
        Caution(bot)
    )