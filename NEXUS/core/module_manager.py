import importlib


class ModuleManager:
    def __init__(self, nexus):
        self.nexus = nexus
        self.modules = {}

    def load(self, module_path, class_name):
        try:
            module = importlib.import_module(module_path)
            module_class = getattr(module, class_name)

            instance = module_class()

            self.modules[instance.name] = {
                "instance": instance,
                "status": "OFFLINE"
            }

            self.nexus.log(
                f"MODULE LOADED: {instance.name}"
            )

        except Exception as error:
            self.nexus.log(
                f"MODULE LOAD FAILED: {module_path} - {error}"
            )

    def start_all(self):
        for name, data in self.modules.items():
            try:
                data["instance"].start(self.nexus)
                data["status"] = "ONLINE"

                self.nexus.log(
                    f"MODULE ONLINE: {name}"
                )

            except Exception as error:
                data["status"] = "ERROR"

                self.nexus.log(
                    f"MODULE START FAILED: {name} - {error}"
                )

    def stop_all(self):
        for name, data in self.modules.items():
            try:
                data["instance"].stop(self.nexus)
                data["status"] = "OFFLINE"

                self.nexus.log(
                    f"MODULE OFFLINE: {name}"
                )

            except Exception as error:
                data["status"] = "ERROR"

                self.nexus.log(
                    f"MODULE STOP FAILED: {name} - {error}"
                )

    def get_status(self):
        result = {}

        for name, data in self.modules.items():
            result[name] = data["status"]

        return result

    def show_modules(self):
        print()
        print("=" * 45)
        print(" NEXUS MODULE STATUS")
        print("=" * 45)

        for name, data in self.modules.items():
            print(f" {name:<15} {data['status']}")

        print("=" * 45)
        print()