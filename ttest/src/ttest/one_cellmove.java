package ttest;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import lejos.hardware.motor.Motor;
import lejos.robotics.RegulatedMotor;

public class one_cellmove {
	public final static int xDegree = 210;
	public final static int yDegree = 200;
	public final static int zUpDegree = 0;
	public final static int zDownDegree = 180;

	public static void init() {
		Motor.A.synchronizeWith(new RegulatedMotor[] { Motor.B });
	}

	private static void waitDone() {
		while (Motor.A.isMoving())
			Thread.yield();
		while (Motor.D.isMoving())
			Thread.yield();
	}

	private static void X_frontmove() {
		Motor.A.startSynchronization();
		Motor.A.setSpeed(100);
		Motor.B.setSpeed(100);
		Motor.A.forward();
		Motor.B.forward();
		Motor.A.rotate(xDegree, true);
		Motor.B.rotate(xDegree, true);
		Motor.A.endSynchronization();
		waitDone();
	}

	private static void X_backmove() {
		Motor.A.startSynchronization();
		Motor.A.setSpeed(100);
		Motor.B.setSpeed(100);
		Motor.A.rotate(-xDegree, true);
		Motor.B.rotate(-xDegree, true);
		Motor.A.endSynchronization();
		waitDone();
	}

	private static void Y_frontmove() {
		Motor.C.setSpeed(100);
		Motor.C.forward();
		Motor.C.rotate(yDegree, true);
		Motor.C.stop();
	}

	private static void Y_backmove() {
		Motor.C.setSpeed(100);
		Motor.C.backward();
		Motor.C.rotate(-1 * yDegree, true);
		Motor.C.stop();
	}

	private static void Z_up() {
		Motor.D.setSpeed(100);
		Motor.D.forward();
		Motor.D.rotateTo(zUpDegree);
		Motor.D.stop();
	}

	private static void Z_down() {
		Motor.D.setSpeed(100);
		Motor.D.backward();
		Motor.D.rotateTo(zDownDegree);
		Motor.D.stop();
	}

	public static void X_totalmove(int n) {
		if (n == 0) {
			return;
		} else if (n > 0) {
			for (int i = 0; i < n; i++) {
				X_frontmove();
			}
		} else if (n < 0) {
			for (int i = 0; i < -1 * n; i++) {
				X_backmove();
			}

		}
	}

	public static void Y_totalmove(int n) {
		if (n == 0) {
			return;
		} else if (n > 0) {
			for (int i = 0; i < n; i++) {
				Y_frontmove();
			}
		} else if (n < 0) {
			for (int i = 0; i < -1 * n; i++) {
				Y_backmove();
			}

		}
	}

	public static String getMove() {
		BufferedReader br = null;
		try {
			URL url = new URL("https://cs270.buttercrab.net/get-move");
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setRequestMethod("GET");
			conn.setRequestProperty("Accept",
					"application/x-www-form-urlencoded");
			conn.connect();

			br = new BufferedReader(
					new InputStreamReader(conn.getInputStream()));
			StringBuffer sb = new StringBuffer();

			String res = "";
			while ((res = br.readLine()) != null) {
				sb.append(res);
			}

			return sb.toString();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			try {
				if (br != null) {
					br.close();
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		return "";
	}

	public static void doneMove() {
		try {
			URL url = new URL("https://cs270.buttercrab.net/done-move");
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setRequestMethod("GET");
			conn.setRequestProperty("Accept",
					"application/x-www-form-urlencoded");
			conn.connect();
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	public static void main(String[] args) {
		Runtime.init();
		init();
		while (true) {
			String moveString = getMove();
			for (int i = 0; i < moveString.length(); i++) {
				switch (moveString.charAt(i)) {
				case 'u':
					X_frontmove();
					break;
				case 'd':
					X_backmove();
					break;
				case 'l':
					Y_backmove();
					break;
				case 'r':
					Y_frontmove();
					break;
				case 'z':
					Z_up();
					break;
				case 'Z':
					Z_down();
					break;
				}
			}
			doneMove();
		}
	}

}