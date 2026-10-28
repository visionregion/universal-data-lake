// wavemaker.ino - sinusoidal wave maker for the water-channel horizon experiment
//
// A hobby servo moves a plunger (a wedge or a flat paddle) up and down at the
// downstream end of the channel. Frequency and amplitude are set over the
// serial monitor (115200 baud):
//
//   f 2.0     set frequency to 2.0 Hz
//   a 15      set amplitude to 15 degrees of servo travel (around the centre)
//   c 90      set centre position in degrees
//   s         stop (hold at centre)
//   g         go (start oscillating)
//   ?         print current settings
//
// Wiring: servo signal -> pin 9. Power the servo from its own 5-6 V supply
// (NOT from the Arduino's 5 V pin) and connect the grounds together.
// Keep all electronics above and away from the water.

#include <Servo.h>

const int SERVO_PIN = 9;
const unsigned long UPDATE_US = 5000;   // 200 Hz position updates

Servo servo;
float freqHz = 2.0;
float ampDeg = 10.0;
float centreDeg = 90.0;
bool running = false;
float phase = 0.0;                      // radians, kept continuous across changes
unsigned long lastUs = 0;

void printSettings() {
  Serial.print(F("freq ")); Serial.print(freqHz, 3);
  Serial.print(F(" Hz, amp ")); Serial.print(ampDeg, 1);
  Serial.print(F(" deg, centre ")); Serial.print(centreDeg, 1);
  Serial.println(running ? F(" deg, RUNNING") : F(" deg, stopped"));
}

void handleSerial() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;
  char cmd = line.charAt(0);
  float val = line.substring(1).toFloat();
  switch (cmd) {
    case 'f': if (val > 0 && val <= 10) freqHz = val; break;   // phase stays continuous
    case 'a': if (val >= 0 && val <= 45) ampDeg = val; break;
    case 'c': if (val >= 20 && val <= 160) centreDeg = val; break;
    case 's': running = false; servo.write((int)centreDeg); break;
    case 'g': running = true; break;
    case '?': break;
    default: Serial.println(F("commands: f <Hz>, a <deg>, c <deg>, s, g, ?"));
  }
  printSettings();
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);
  servo.attach(SERVO_PIN);
  servo.write((int)centreDeg);
  lastUs = micros();
  Serial.println(F("wavemaker ready"));
  printSettings();
}

void loop() {
  handleSerial();
  unsigned long now = micros();
  if (now - lastUs < UPDATE_US) return;
  float dt = (now - lastUs) * 1e-6;
  lastUs = now;
  if (!running) return;

  phase += 2.0 * PI * freqHz * dt;
  if (phase > 2.0 * PI) phase -= 2.0 * PI;
  // writeMicroseconds gives finer steps than whole degrees
  float deg = centreDeg + ampDeg * sin(phase);
  int us = map((long)(deg * 10), 0, 1800, 544, 2400);
  servo.writeMicroseconds(us);
}
