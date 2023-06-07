import subprocess
from pathlib import Path

stockfish = Path(__file__).parent / "Stockfish" / "src" / "stockfish"


class Stockfish:
    def __init__(self):
        self.engineProcess = None
        self.processReader = None
        self.processWriter = None

    def start_engine(self):
        try:
            self.engineProcess = subprocess.Popen(
                stockfish,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            self.processReader = self.engineProcess.stdout
            self.processWriter = self.engineProcess.stdin
        except Exception as e:
            return False
        return True

    def stop_engine(self):
        try:
            self.send_command("quit")
            self.processReader.close()
            self.processWriter.close()
        except Exception as e:
            pass

    def send_command(self, command):
        try:
            self.processWriter.write(command + "\n")
            self.processWriter.flush()
        except Exception as e:
            pass

    def get_output(self, waitTime, bestmove):
        buffer = []
        check1 = not bestmove
        check2 = False

        try:
            import time

            time.sleep(waitTime / 1000.0)
            self.send_command("isready")
            while True:
                output = self.processReader.readline().strip()

                if "bestmove" in output:
                    check1 = True
                if output == "readyok":
                    check2 = True

                buffer.append(output)
                if check1 and check2:
                    break
        except Exception as e:
            pass

        return "\n".join(buffer)

    def get_best_move(self, waitTime):
        self.send_command("go movetime " + str(waitTime))
        output = self.get_output(waitTime, True)
        return output.split("bestmove ")[1].split(" ")[0]

    def get_fen(self):
        self.send_command("d")
        output = self.get_output(0, False)
        return output.split("Fen: ")[1]

    def move_and_get_fen(self, fen, move):
        self.send_command("position fen " + fen + " moves " + move)
        return self.get_fen()
