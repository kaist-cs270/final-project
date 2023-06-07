package ttest;
import lejos.ev3.*;
import lejos.hardware.*;
import lejos.hardware.ev3.EV3;
import lejos.hardware.motor.EV3LargeRegulatedMotor;
import lejos.hardware.port.MotorPort;
import lejos.utility.Delay;
public class zaxis {
public static void main(String[] args){
	EV3 ev3brick= (EV3) BrickFinder.getDefault();
	EV3LargeRegulatedMotor motorc = new EV3LargeRegulatedMotor(MotorPort.C);
	motorc.setSpeed(600);
	motorc.forward();
	Delay.msDelay(3000);
	motorc.backward();
	Delay.msDelay(3000);
	motorc.stop();
	motorc.close();
}
}
