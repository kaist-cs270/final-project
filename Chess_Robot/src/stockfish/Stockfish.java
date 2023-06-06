package stockfish;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;

public class Stockfish {

	private Process engineProcess;
	private BufferedReader processReader;
	private OutputStreamWriter processWriter;

	private static final String PATH = "./engine/stockfish.exe";

	public boolean startEngine() {
		try {
			engineProcess = Runtime.getRuntime().exec(PATH);
			processReader = new BufferedReader(new InputStreamReader(
					engineProcess.getInputStream()));
			processWriter = new OutputStreamWriter(
					engineProcess.getOutputStream());
		} catch (Exception e) {
			return false;
		}
		return true;
	}

	public void stopEngine() {
		try {
			sendCommand("quit");
			processReader.close();
			processWriter.close();
		} catch (Exception e) {
		}
	}

	public void sendCommand(String command) {
		try {
			processWriter.write(command + "\n");
			processWriter.flush();
		} catch (Exception e) {
		}
	}

	public String getOutput(int waitTime, boolean bestmove) {
		StringBuffer buffer = new StringBuffer();
		boolean check1 = !bestmove, check2 = false;

		try {
			Thread.sleep(waitTime);
			sendCommand("isready");
			while (true) {
				String output = processReader.readLine();

				if (output.contains("bestmove"))
					check1 = true;
				if (output.equals("readyok"))
					check2 = true;

				buffer.append(output + " \n");
				if (check1 && check2)
					break;
			}
		} catch (Exception e) {
		}

		return buffer.toString();
	}

	public String getBestMove(String fen, int waitTime) {
		sendCommand("go movetime " + waitTime);
		return getOutput(waitTime, true).split("bestmove ")[1].split(" ")[0];
	}

	public String getFen() {
		sendCommand("d");
		return getOutput(0, false).split("Fen: ")[1].split(" \n")[0];
	}

	public String moveAndGetFen(String fen, String move) {
		sendCommand("position fen " + fen + " moves " + move);
		return getFen();
	}
}
