from core.system import NexusSystem
from core.module_manager import ModuleManager


def main():

    print()
    print("=" * 44)
    print("              NEXUS BOOT")
    print("=" * 44)

    nexus = NexusSystem()
    nexus.start()

    print("[✓] Core")
    print("[✓] Logger")

    manager = ModuleManager(nexus)
    nexus.module_manager = manager

    nexus.log("MODULE MANAGER INITIALIZED")

    # 모듈 로드
    manager.load("modules.web", "WebModule")
    manager.load("modules.discord", "DiscordModule")
    manager.load("modules.drone", "DroneModule")
    manager.load("modules.hardware", "HardwareModule")

    # 모듈 시작
    manager.start_all()

    # 상태 출력
    manager.show_modules()
    nexus.show_status()

    try:
        input("Press Enter to shutdown...")

    except KeyboardInterrupt:
        print()

    print()

    nexus.log("NEXUS SHUTDOWN SEQUENCE")

    manager.stop_all()

    nexus.stop()

    print()
    print("=" * 44)
    print("              NEXUS OFFLINE")
    print("=" * 44)
    print()


if __name__ == "__main__":
    main()