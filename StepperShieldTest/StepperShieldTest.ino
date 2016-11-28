    #include <AFMotor.h>
     
     
    AF_Stepper motor(48, 1);
    
    AF_DCMotor dispenser(3, MOTOR12_64KHZ); // create motor #3, 64KHz pwm
     
     
    void setup() {
      Serial.begin(9600);           // set up Serial library at 9600 bps
      Serial.println("Stepper test!");
     
      motor.setSpeed(10);  // 10 rpm   
      dispenser.setSpeed(255);
     
      //motor.step(100, FORWARD, SINGLE); 
      //motor.release();
      //delay(1000);
    }
     
    void loop() {
      if( Serial.available() ) {
        char ser = Serial.read();
        if( ser == 'f' ) {
          motor.step(4, FORWARD, SINGLE); 
        }
        if( ser == 'F' ) {
          motor.step(8, FORWARD, SINGLE); 
        }
        
        if( ser == 'b' ) {
          motor.step(4, BACKWARD, SINGLE); 
        }
        if( ser == 'B' ) {
          motor.step(8, BACKWARD, SINGLE); 
        }
        
        if( ser == 'd' ) {
          dispenser.run( FORWARD );
          delay(400);
          dispenser.run( RELEASE );
          
          dispenser.run( FORWARD );
          delay(400);
          dispenser.run( RELEASE );
          
          dispenser.run( FORWARD );
          delay(400);
          dispenser.run( RELEASE );
        }
      }
      motor.release(); //Or else it gets warm.
      
      /*Serial.write("DBL");
     
      motor.step(10, FORWARD, DOUBLE); 
      motor.step(10, BACKWARD, DOUBLE);
     
      delay(1000);
     Serial.write("ILEAV");
      motor.step(10, FORWARD, INTERLEAVE); 
      motor.step(10, BACKWARD, INTERLEAVE); 
     
      delay(1000);
     Serial.write("MICRO");
      motor.step(100, FORWARD, MICROSTEP); 
      motor.step(100, BACKWARD, MICROSTEP); */
    }
