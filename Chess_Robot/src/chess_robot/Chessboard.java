package chess_robot;

import java.util.Scanner;
import java.util.LinkedList;

import stockfish.Stockfish;

class chessPos {

	int x, y;

	chessPos() {
		x = 0;
		y = 0;
	}

	chessPos(int x, int y) {
		this.x = x;
		this.y = y;
	}

	chessPos(chessPos pos) {
		set(pos);
	}

	void set(chessPos pos) {
		x = pos.x;
		y = pos.y;
	}

	// 1, 3, ... , 17: gap / 0, 2, ... , 18: piece
	boolean valid() {
		return 0 <= x && x <= 18 && 0 <= y && y <= 18;
	}

	// a1 -> 16, 2
	void set(String name) {
		x = (9 - Character.digit(name.charAt(1), 10)) * 2;
		y = (Character.digit(name.charAt(0), 18) - 9) * 2;
	}

	String name() {
		if (x % 2 != 0 || y % 2 != 0 || x == 0 || x == 18 || y == 0 || y == 18)
			return "";
		return String.format("%c%c", Character.forDigit((y / 2 + 9), 18),
				Character.forDigit((9 - x / 2), 10));
	}

	void input(Scanner sc, String msg) {
		System.out.print(msg);
		try {
			String name = sc.nextLine();
			if (name.length() != 2)
				throw new Exception();
			set(name);
			if (valid())
				return;
		} catch (Exception e) {
		}
		System.out.println("wrong input; wrong format");
		input(sc, msg);
	}

	void print() {
		System.out.printf("(%d, %d)", x, y);
	}

	void move(dir dir, boolean forward) {
		x += dir.dx * (forward ? 1 : -1);
		y += dir.dy * (forward ? 1 : -1);
	}

	boolean isSame(chessPos pos) {
		return x == pos.x && y == pos.y;
	}
}

enum dir {
	up(-1, 0), right(0, 1), down(1, 0), left(0, -1);

	int dx, dy;

	dir(int dx, int dy) {
		this.dx = dx;
		this.dy = dy;
	};
};

public class Chessboard {

	// lower case: black, upper case: white
	// King, Queen, Rook, Bishop, kNight, Pawn
	static final String PIECE = " rnbqkpRNBQKP";

	// 4 = extra space for piece captured
	static char[][] board = new char[15 + 4][15 + 4];
	static String fen = "";
	static boolean isUserTurn, isOver = false;

	static void initBoard() {
		for (int i = 0; i < 19; i++)
			for (int j = 0; j < 19; j++)
				board[i][j] = ' ';
		board[2] = "  r n b q k b n r  ".toCharArray();
		board[4] = "  p p p p p p p p  ".toCharArray();
		board[14] = "  P P P P P P P P  ".toCharArray();
		board[16] = "  R N B Q K B N R  ".toCharArray();
	}

	/*
	 * static String fen() { String fen = ""; int count; for (int i = 2; i < 17;
	 * i += 2) { count = 0; for (int j = 2; j < 17; j += 2) { if (board[i][j] ==
	 * ' ') count++; else { if (count != 0) { fen += count; count = 0; } fen +=
	 * board[i][j]; } } if (count != 0) fen += count; if (i != 16) fen += '/'; }
	 * return fen; }
	 */

	static void printBoard() {
		System.out.println("\n      a b c d e f g h");
		System.out.println("      ---------------");
		System.out.println("    " + String.valueOf(board[0]));
		for (int i = 2; i < 17; i += 2) {
			System.out.printf("%d | ", 9 - i / 2);
			System.out.println(board[i]);
		}
		System.out.println("    " + String.valueOf(board[18]));
		System.out.println("Fen: " + fen + "\n");
	}

	static boolean canGo(chessPos pos) {
		if (!pos.valid())
			return false;
		if (board[pos.x][pos.y] != ' ')
			return false;
		return true;
	}

	static boolean isWhiteTurn() {
		return fen.contains("w");
	}

	static chessPos findBlank() {
		int i;
		if (isWhiteTurn()) {
			for (i = 0; i < 19; i += 2)
				if (board[0][i] == ' ')
					return new chessPos(0, i);
			for (i = 2; i < 9; i += 2) {
				if (board[i][0] == ' ')
					return new chessPos(i, 0);
				if (board[i][18] == ' ')
					return new chessPos(i, 18);
			}
		} else {
			for (i = 0; i < 19; i += 2)
				if (board[18][i] == ' ')
					return new chessPos(18, i);
			for (i = 16; i > 9; i -= 2) {
				if (board[i][0] == ' ')
					return new chessPos(i, 0);
				if (board[i][18] == ' ')
					return new chessPos(i, 18);
			}
		}
		// no case for this
		return new chessPos();
	}

	static void movePiece(chessPos startPos, chessPos endPos) {
		if (!canGo(endPos))
			movePiece(endPos, findBlank());

		boolean visited[][] = new boolean[15 + 4][15 + 4];
		dir direction[][] = new dir[15 + 4][15 + 4];
		LinkedList<chessPos> queue = new LinkedList<chessPos>();
		LinkedList<dir> path = new LinkedList<dir>();
		chessPos pos = new chessPos(startPos);

		visited[pos.x][pos.y] = true;
		queue.add(pos);

		while (queue.size() != 0) {
			pos = queue.poll();

			for (int i = 0; i < 4; i++) {
				chessPos nextPos = new chessPos(pos);
				dir nextDir = dir.values()[i];

				nextPos.move(nextDir, true);
				if (canGo(nextPos) && !visited[nextPos.x][nextPos.y]) {
					visited[nextPos.x][nextPos.y] = true;
					direction[nextPos.x][nextPos.y] = nextDir;
					queue.add(nextPos);
				}
			}
		}

		pos.set(endPos);
		while (!pos.isSame(startPos)) {
			path.addFirst(direction[pos.x][pos.y]);
			pos.move(direction[pos.x][pos.y], false);
		}

		System.out.print("path for " + startPos.name() + " -> " + endPos.name()
				+ ": ");
		pos.set(startPos);
		for (dir dir : path) {
			pos.print();
			System.out.print(" -> " + dir + " -> ");
			pos.move(dir, true);
		}
		pos.print();
		System.out.println();

		board[endPos.x][endPos.y] = board[startPos.x][startPos.y];
		board[startPos.x][startPos.y] = ' ';
	}

	static boolean isMoveCompleted() {
		return true;
	}

	static boolean setTurn(Scanner sc) {
		System.out.println("who will go first; user(0) / AI(1)");
		try {
			String turn = sc.nextLine();
			if (turn.equals("0")) {
				return true;
			} else if (turn.equals("1")) {
				return false;
			}
		} catch (Exception e) {
		}
		System.out.println("wrong input; choose between 0 and 1");
		return setTurn(sc);
	}

	public static void main(String[] args) {
		initBoard();
		printBoard();

		Stockfish client = new Stockfish();
		if (client.startEngine()) {
			System.out.println("start Engine");

			client.sendCommand("uci");
			client.getOutput(0, false);

			client.sendCommand("position startPos");
			fen = client.getFen();

			Scanner sc = new Scanner(System.in);

			isUserTurn = setTurn(sc);

			while (!isOver) {
				chessPos startPos = new chessPos(), endPos = new chessPos();
				String move, nextFen;

				if (isUserTurn) {
					startPos.input(sc, "from: ");
					endPos.input(sc, "to: ");

					// quit game
					if (startPos.isSame(endPos))
						break;

					move = startPos.name() + endPos.name();
					nextFen = client.moveAndGetFen(fen, move);

					if (fen.equals(nextFen)) {
						System.out.println("wrong input; can't move");
					} else {
						fen = nextFen;
						isUserTurn = false;
						movePiece(startPos, endPos);
					}

				} else {
					move = client.getBestMove(fen, 100);

					fen = client.moveAndGetFen(fen, move);
					isUserTurn = true;

					startPos.set(move.substring(0, 2));
					endPos.set(move.substring(2));

					movePiece(startPos, endPos);
				}

				printBoard();
				
				move = client.getBestMove(fen, 100);

				if (move.equals("(none)")) {
					isOver = true;
					System.out.println("checkmate; game over");
				} 
			}

			client.stopEngine();
		} else
			System.out.println("can't start Engine");
	}
}
