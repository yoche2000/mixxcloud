import subprocess

class Commands:
    @staticmethod
    def run_command(command):
        try:
            process = subprocess.run(command, capture_output=True, text=True)
            print(process.stdout)
            if process.stderr:
                print("Error:", process.stderr)
        except Exception as error:
            raise Exception(f"Issue in Command Run: {error}")
