import os
from datetime import datetime


class NexusSystem:

    def __init__(self):

        self.name = "NEXUS"
        self.version = "0.8.0"

        self.start_time = None
        self.status = "OFFLINE"

        self.log_directory = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "logs"
        )

        self.log_file = os.path.join(
            self.log_directory,
            "system.log"
        )

        self.recent_logs = []
        self.max_recent_logs = 100

        os.makedirs(
            self.log_directory,
            exist_ok=True
        )

    # ==============================
    # SYSTEM
    # ==============================

    def start(self):

        self.start_time = datetime.now()
        self.status = "ONLINE"

        self.system_log("SYSTEM STARTED")
        self.system_log("CORE INITIALIZED")

    def stop(self):

        self.system_log("SYSTEM SHUTDOWN")

        self.status = "OFFLINE"

    # ==============================
    # LOGGER
    # ==============================

    def log(self, message, level="INFO"):

        now = datetime.now()

        timestamp = now.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        line = (
            f"[{timestamp}] "
            f"[NEXUS] "
            f"[{level}] "
            f"{message}"
        )

        print(line)

        self.recent_logs.append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })

        if len(self.recent_logs) > self.max_recent_logs:

            self.recent_logs.pop(0)

        try:

            with open(
                self.log_file,
                "a",
                encoding="utf-8"
            ) as file:

                file.write(line + "\n")

        except Exception as error:

            print(
                f"[NEXUS] "
                f"[ERROR] "
                f"LOG WRITE FAILED: {error}"
            )

    def info(self, message):

        self.log(message, "INFO")

    def warning(self, message):

        self.log(message, "WARNING")

    def error(self, message):

        self.log(message, "ERROR")

    def system_log(self, message):

        self.log(message, "SYSTEM")

    # ==============================
    # UPTIME
    # ==============================

    def get_uptime(self):

        if self.start_time is None:
            return 0

        return int(
            (
                datetime.now()
                - self.start_time
            ).total_seconds()
        )

    # ==============================
    # LOG
    # ==============================

    def get_recent_logs(self, limit=20):

        return self.recent_logs[-limit:]

    def get_log_count(self):

        return len(self.recent_logs)

    # ==============================
    # STATUS
    # ==============================

    def get_status(self):

        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "uptime": self.get_uptime(),
            "log_count": self.get_log_count()
        }

    # ==============================
    # CONSOLE STATUS
    # ==============================

    def show_status(self):

        print()

        print("=" * 45)

        print(
            f" {self.name} "
            f"SYSTEM v{self.version}"
        )

        print("=" * 45)

        print(
            f" STATUS : {self.status}"
        )

        print(
            f" START  : {self.start_time}"
        )

        print(
            f" UPTIME : {self.get_uptime()} sec"
        )

        print(
            f" LOGS   : {self.get_log_count()}"
        )

        print(
            f" LOG    : {self.log_file}"
        )

        print("=" * 45)

        print()