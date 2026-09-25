class DroneModule:
    name = "DRONE"

    def start(self, nexus):
        nexus.log("DRONE MODULE STARTED")

    def stop(self, nexus):
        nexus.log("DRONE MODULE STOPPED")