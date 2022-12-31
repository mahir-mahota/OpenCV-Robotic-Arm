#include <Servo.h>
Servo claw, rotate, adjust, turn;

const int CLOSE_CLAW = 90, OPEN_CLAW = 10, ROTATE_RIGHT = 140, ROTATE_LEFT = 0, 
          CLAW_START = 10, ROTATE_START = 50, ADJUST_START = 70, TURN_START = 90,
          ADJUST_UP = 180, ADJUST_DOWN = 40,
          CLAW_PIN = 11, ROTATE_PIN = 10, ADJUST_PIN = 9, TURN_PIN = 5;

int command, close_claw = 'A', open_claw = 'B', turn_right = 'C', turn_left = 'D',
    rotate_right = 'E', rotate_left = 'F', adjust_up = 'G', adjust_down = 'H', reset = 'I',
    rotate_reset = 'J';

int turn_pos = TURN_START, adjust_pos = ADJUST_START;

void setup()
{
  Serial.begin(9600);
  
  claw.attach(CLAW_PIN);
  rotate.attach(ROTATE_PIN);
  adjust.attach(ADJUST_PIN);
  turn.attach(TURN_PIN);

  claw.write(CLAW_START);
  rotate.write(ROTATE_START);
  adjust.write(ADJUST_START);
  turn.write(TURN_START);
}

void loop()
{
  if(Serial.available() > 0)
  {
    command = Serial.read();
    //command = command.substring(0,command.length()-1);
    
    if(command == close_claw)
    {
      claw.write(CLOSE_CLAW);
    }
    if(command == open_claw)
    {
      claw.write(OPEN_CLAW);
    }  

    if(command == turn_right && turn_pos < 180)
    {
      turn_pos += 5;
      turn.write(turn_pos);
    }
    if(command == turn_left && turn_pos > 0)
    {
      turn_pos -= 5;
      turn.write(turn_pos);
    }

    if(command == rotate_right)
    {
      rotate.write(ROTATE_RIGHT);
    }
    if(command == rotate_left)
    {
      rotate.write(ROTATE_LEFT);
    }
    if(command == rotate_reset)
    {
      rotate.write(ROTATE_START);
    }

    if(command == adjust_up)
    {
      adjust.write(ADJUST_UP);
    }
    if(command == adjust_down)
    {
      adjust.write(ADJUST_DOWN);
    }

    if(command == reset)
    {
      claw.write(CLAW_START);
      rotate.write(ROTATE_START);
      adjust.write(ADJUST_START);
      turn.write(TURN_START);
      turn_pos = TURN_START;
    }
  }
}