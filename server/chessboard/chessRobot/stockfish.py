import subprocess
import time
from pathlib import Path

curr_path = Path(__file__).parent

class Stockfish:
    def __init__(self):
        self.engineProcess = None
        self.processReader = None
        self.processWriter = None
        self.PATH = [curr_path / './engine/stockfish.exe']

    def startEngine(self):
        try:
            self.engineProcess = subprocess.Popen(self.PATH, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
            self.processReader = self.engineProcess.stdout
            self.processWriter = self.engineProcess.stdin
        except Exception as e:
            print(e)
            return False
        return True

    def sendCommand(self, command):
        try:
            self.processWriter.write(command + "\n")
            self.processWriter.flush()
        except Exception as e:
            print(e)

    def stopEngine(self):
        try:
            self.sendCommand("quit")
            self.processReader.close()
            self.processWriter.close()
        except Exception as e:
            print(e)

    def getOutput(self, waitTime, bestmove):
        buffer = ""
        check1 = not bestmove
        check2 = False

        try:
            time.sleep(waitTime / 1000)
            self.sendCommand("isready")
            while True:
                output = self.processReader.readline().rstrip()

                if "bestmove" in output:
                    check1 = True
                if "readyok" in output:
                    check2 = True

                buffer += output + " \n"
                if check1 and check2:
                    break
        except Exception as e:
            print(e)

        return buffer

    def getBestMove(self, waitTime):
        self.sendCommand("go movetime " + str(waitTime))
        output = self.getOutput(waitTime, True)
        return output.split("bestmove ")[1].split(" ")[0]

    def getFen(self):
        self.sendCommand("d")
        output = self.getOutput(0, False)
        return output.split("Fen: ")[1].split(" \n")[0]

    def moveAndGetFen(self, fen, move):
        self.sendCommand("position fen " + fen + " moves " + move)
        return self.getFen()
