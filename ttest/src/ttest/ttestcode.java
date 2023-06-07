package ttest;
import lejos.ev3.*;
import lejos.hardware.*;
import lejos.hardware.ev3.EV3;
import lejos.hardware.motor.EV3LargeRegulatedMotor;
import lejos.hardware.port.MotorPort;
import lejos.utility.Delay;
public class ttestcode {
public static void main(String[] args){
	EV3 ev3brick= (EV3) BrickFinder.getDefault();
	EV3LargeRegulatedMotor motorA = new EV3LargeRegulatedMotor(MotorPort.A);
	motorA.setSpeed(600);
	motorA.forward();
	Delay.msDelay(3000);
	motorA.forward();
	Delay.msDelay(3000);
	motorA.forward();
	motorA.stop();
	motorA.close();
	
}
}
