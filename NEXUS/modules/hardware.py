class HardwareModule:
    name = "HARDWARE"

    def start(self, nexus):
        nexus.log("HARDWARE MODULE STARTED")

    def stop(self, nexus):
        nexus.log("HARDWARE MODULE STOPPED")