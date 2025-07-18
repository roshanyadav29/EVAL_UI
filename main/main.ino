//"""CONFIGURES ARDUINO FOR CUSTOM SERIAL PROTOCOL"""
// This code is designed to run on an ESP32 board and implements a custom serial protocol
// for communication with a slave device. It uses GPIO pins to send data in a specific sequence

#include <SPI.h>

#define DEBUG_STATEMENT false

// Note: SPI uses default pins (CLK=18, MOSI=23 for VSPI) unless custom pins are specified
/*MODIFY GPIO PINS HERE*/ 
const int CLOCK_PIN = 27;     // Clock GPIO pin
const int DATA_PIN = 25;      // Data GPIO pin  
const int SHIFT_PIN = 26;      // Shift GPIO pin (high during data transmission)
const int RESET_PIN = 33;     // Reset GPIO pin (low during transmission, high normally)
const int LED_BUILTIN = 2;    // Built-in LED pin (usually GPIO 2 on ESP32)

// Value to be sent by the MASTER (128 bits = 16 bytes)
/*MODIFY DATA HERE*/ byte Data[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};

const int lenData = 16; // Number of bytes in Data array (128 bits total)

/*MODIFY CLK_FREQ HERE*/ int clk_freq_khz = 100;

void setup()
{
#if (DEBUG_STATEMENT)
  Serial.begin(115200);
  while (!Serial)
    delay(10);
  Serial.println("ESP32 Custom Protocol Controller (SPI)");
#endif

  // Configure GPIO pins
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SHIFT_PIN, OUTPUT);
  pinMode(RESET_PIN, OUTPUT);

  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(SHIFT_PIN, LOW);
  digitalWrite(RESET_PIN, HIGH);

  // Initialize SPI
  SPI.begin();
  SPI.setFrequency(clk_freq_khz * 1000); // Set frequency in Hz
  SPI.setDataMode(SPI_MODE0);            // Mode 0: CPOL=0, CPHA=0
  SPI.setBitOrder(MSBFIRST);             // MSB first

  // Perform reset sequence and send data
  sendDataSequence();
}

void loop()
{
  // do nothing
}

void sendResetSequence()
{
#if (DEBUG_STATEMENT)
  Serial.println("Starting reset sequence...");
#endif
  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(RESET_PIN, LOW); // Active low reset

  // Generate few clock cycles with dummy data
  SPI.transfer(0x00); // 8 cycles per transfer

  digitalWrite(RESET_PIN, HIGH); // End reset
  digitalWrite(LED_BUILTIN, LOW);
#if (DEBUG_STATEMENT)
  Serial.println("Reset sequence completed");
#endif
}

void sendDataSequence()
{
#if (DEBUG_STATEMENT)
  Serial.println("Starting data transmission...");
#endif
  sendResetSequence();
  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(SHIFT_PIN, HIGH); // SHIFT high during transmission

  // Transmit 128 bits (16 bytes) in one call
  uint8_t dummy[lenData]; // Dummy buffer for receive (not used)

  SPI.transferBytes(Data, dummy, lenData); // Send all 16 bytes at once

  digitalWrite(SHIFT_PIN, LOW); // End SHIFT
  
  // Extra few cycles to save shift status
  SPI.transfer(0x00);           // Dummy bytes for extra cycles

  digitalWrite(LED_BUILTIN, LOW);
#if (DEBUG_STATEMENT)
  Serial.println("Data transmission completed");
#endif
}