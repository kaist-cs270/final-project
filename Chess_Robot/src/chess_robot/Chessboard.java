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
		return String.format("%c%c\n", Character.forDigit((y / 2 + 9), 18),
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
	static boolean whiteTurn = true;

	static void initBoard() {
		for (int i = 0; i < 19; i++)
			for (int j = 0; j < 19; j++)
				board[i][j] = ' ';
		board[2] = "  r n b q k b n r  ".toCharArray();
		board[4] = "  p p p p p p p p  ".toCharArray();
		board[14] = "  P P P P P P P P  ".toCharArray();
		board[16] = "  R N B Q K B N R  ".toCharArray();
	}

	static String fen() {
		String fen = "";
		int count;
		for (int i = 2; i < 17; i += 2) {
			count = 0;
			for (int j = 2; j < 17; j += 2) {
				if (board[i][j] == ' ')
					count++;
				else {
					if (count != 0) {
						fen += count;
						count = 0;
					}
					fen += board[i][j];
				}
			}
			if (count != 0)
				fen += count;
			if (i != 16)
				fen += '/';
		}
		return fen;
	}

	static void printBoard() {
		System.out.println("\n      a b c d e f g h");
		System.out.println("      ---------------");
		System.out.println("    " + String.valueOf(board[0]));
		for (int i = 2; i < 17; i += 2) {
			System.out.printf("%d | ", 9 - i / 2);
			System.out.println(board[i]);
		}
		System.out.println("    " + String.valueOf(board[18]));
		System.out.println("Fen: " + fen() + "\n");
	}

	static boolean canGo(chessPos pos) {
		if (!pos.valid())
			return false;
		if (board[pos.x][pos.y] != ' ')
			return false;
		return true;
	}

	static void movePiece(chessPos startPos, chessPos endPos) {
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

		System.out.print("path: ");
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
	
	static void removePiece(chessPos pos) {
		
	}

	static boolean isIllegalMove(chessPos startPos, chessPos endPos) {
		// isIllegalMove <-> f == [d]
		if (!canGo(endPos)) return true;
		return false;
	}

	static boolean isMoveCompleted() {
		return true;
	}
	
	static boolean isOver() {
		return false;
	}

	public static void main(String[] args) {
		initBoard();
		printBoard();

		Stockfish client = new Stockfish();
		if (client.startEngine()) {
			System.out.println("start Engine");

			client.sendCommand("uci");
			client.getOutput(0);

			Scanner sc = new Scanner(System.in);

			// who will be first

			while (!isOver()) {
				// 1. position startpos -> f = [d]
				// 2.
				// 	2-1. user = white: input -> position fen <f> moves <input> -> f = [d] -> move = [go movetime <waitTime>] -> position fen <f> moves <move> -> f = [d]
				//  2-2. user = black: move = [go movetime <waitTime>] -> position fen <f> moves <move> -> f = [d] -> input -> position fen <f> moves <input> -> f = [d]
				
				chessPos startPos = new chessPos(), endPos = new chessPos();

				startPos.input(sc, "from: ");
				endPos.input(sc, "to: ");

				if (isIllegalMove(startPos, endPos)) {
					System.out.println("wrong input; illegal move");
					continue;
				}

				do {
					movePiece(startPos, endPos);
				} while (!isMoveCompleted());

				printBoard();
				
				break; // for test
			}

			client.stopEngine();
		} else
			System.out.println("can't start Engine");
	}
}
