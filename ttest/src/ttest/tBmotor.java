package ttest;
import lejos.ev3.*;
import lejos.hardware.*;
import lejos.hardware.ev3.EV3;
import lejos.hardware.motor.EV3LargeRegulatedMotor;
import lejos.hardware.port.MotorPort;
import lejos.utility.Delay;
public class tBmotor {
public static void main(String[] args){
	EV3 ev3brick= (EV3) BrickFinder.getDefault();
	EV3LargeRegulatedMotor motorB = new EV3LargeRegulatedMotor(MotorPort.B);
	motorB.setSpeed(600);
	motorB.forward();
	Delay.msDelay(3000);
	motorB.backward();
	Delay.msDelay(3000);
	motorB.stop();
	motorB.close();
}
}
