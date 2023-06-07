package ttest;

import lejos.hardware.BrickFinder;
import lejos.hardware.Keys;
import lejos.hardware.ev3.EV3;

public class Runtime {
	private static int state = 0;
	
	private Runtime() {
		
	}
	
	public static void init() {
		if (state == 0) {
			state = 1;
			
			new Thread(new Runnable() {
				public void run() {
					while (true) {
						EV3 ev3 = (EV3) BrickFinder.getLocal();
						Keys keys = ev3.getKeys();
						if (keys.waitForAnyEvent() == Keys.ID_ESCAPE) {
							System.exit(0);
						}
					}
				}
			}).start();
		} else {
			// TODO
		}
	}
}
