package stockfish;

import java.io.BufferedReader;
import java.io.IOException;
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
			e.printStackTrace();
			return false;
		}
		return true;
	}

	public void stopEngine() {
		try {
			sendCommand("quit");
			processReader.close();
			processWriter.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public void sendCommand(String command) {
		try {
			processWriter.write(command + "\n");
			processWriter.flush();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public String getOutput(int waitTime) {
		StringBuffer buffer = new StringBuffer();

		try {
			Thread.sleep(waitTime);
			sendCommand("isready");
			while (true) {
				String output = processReader.readLine();
				if (output.equals("readyok"))
					break;
				else
					buffer.append(output + "\n");
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return buffer.toString();
	}

	public String getBestMove(String fen, int waitTime) {
		sendCommand("position fen " + fen);
		sendCommand("go movetime " + waitTime);
		return getOutput(waitTime).split("bestmove ")[1].split(" ")[0];
	}

	public String getLegalMoves(String fen) {
		sendCommand("position fen " + fen);
		sendCommand("d");
		return getOutput(0).split("Legal moves: ")[1];
	}

	public void drawBoard(String fen) {
		sendCommand("position fen " + fen);
		sendCommand("d");
		String[] rows = getOutput(0).split("\n");

		for (int i = 1; i < 18; i++) {
			System.out.println(rows[i]);
		}
	}
}
