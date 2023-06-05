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

	// 1, 3, ... , 13: piece / 0, 2, ... , 16: gap
	boolean valid() {
		return 0 <= x && x <= 16 && 0 <= y && y <= 16;
	}

	// a1 -> 14, 0
	void set(String name) {
		x = (8 - Character.digit(name.charAt(1), 10)) * 2 + 1;
		y = (Character.digit(name.charAt(0), 18) - 10) * 2 + 1;
	}

	String name() {
		if (x % 2 == 0 || y % 2 == 0) return "";
		return String.format("%c%c\n", Character.forDigit((y / 2 + 10), 18),
				Character.forDigit((8 - x / 2), 10));
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
		System.out.println("wrong input");
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

	// extra space for piece captured
	static char[][] board = new char[15 + 2][15 + 2];
	static boolean whiteTurn = true;

	static void initBoard() {
		for (int i = 0; i < 15; i++)
			for (int j = 0; j < 15; j++)
					board[i][j] = ' ';
		board[1] = "r n b q k b n r".toCharArray();
		board[3] = "p p p p p p p p".toCharArray();
		board[13] = "P P P P P P P P".toCharArray();
		board[15] = "R N B Q K B N R".toCharArray();
	}

	static void printBoard() {
		System.out.println("\n    a b c d e f g h");
		System.out.println("    ---------------");
		for (int i = 0; i < 15; i += 2) {
			System.out.printf("%d | ", 8 - i / 2);
			System.out.println(board[i]);
		}
		System.out.println(fen());
		System.out.println();
	}
	
	static String fen() {
		String fen = "";
		int count;
		for (int i = 0; i < 15; i += 2) {
			count = 0;
			for (int j = 0; j < 15; j += 2) {
				if (board[i][j] == ' ') count++;
				else {
					if (count != 0) {
						fen += count;
						count = 0;
					}
					fen += board[i][j];
				}
			}
			if (count != 0) fen += count;
			if (i != 14) fen += '/';
		}
		return fen;
	}

	static boolean canGo(chessPos pos) {
		if (!pos.valid())
			return false;
		if (board[pos.x][pos.y] != ' ')
			return false;
		return true;
	}

	static void movePiece(chessPos startPos, chessPos endPos) {
		boolean visited[][] = new boolean[15][15];
		dir direction[][] = new dir[15][15];
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

	static boolean isIllegalMove() {
		return false;
	}

	static boolean isMoveCompleted() {
		return true;
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

			// sc.nextInt(arg0);

			while (true) {
				chessPos startPos = new chessPos(), endPos = new chessPos();

				startPos.input(sc, "from: ");
				endPos.input(sc, "to: ");

				if (isIllegalMove())
					break;

				do {
					movePiece(startPos, endPos);
				} while (!isMoveCompleted());

				printBoard();
			}

			client.stopEngine();
		} else
			System.out.println("can't start Engine");
	}
}
