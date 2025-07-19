//"""CONFIGURES ARDUINO FOR CUSTOM SERIAL PROTOCOL"""
// This code is designed to run on an ESP32 board and implements a custom serial protocol
// for communication with a slave device. It uses GPIO pins to send data in a specific sequence

#include <SPI.h>

#define DEBUG_STATEMENT false

// Serial communication settings
#define SERIAL_BAUD 115200
#define DATA_START_MARKER '<'
#define DATA_END_MARKER '>'
#define RESET_COMMAND 'R'
#define EXPECTED_DATA_SIZE 16

// Note: SPI uses default pins (CLK=18, MOSI=23 for VSPI) unless custom pins are specified
/*MODIFY GPIO PINS HERE*/ 
const int CLOCK_PIN = 18;     // Clock GPIO pin
const int DATA_PIN = 23;      // Data GPIO pin  
const int SHIFT_PIN = 26;      // Shift GPIO pin (high during data transmission)
const int RESET_PIN = 33;     // Reset GPIO pin (low during transmission, high normally)
const int LED_BUILTIN = 2;    // Built-in LED pin (usually GPIO 2 on ESP32)
#ifndef LED_BUILTIN
#endif
// Value to be sent by the MASTER (128 bits = 16 bytes)
/*MODIFY DATA HERE*/ byte Data[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};

const int lenData = 16; // Number of bytes in Data array (128 bits total)

/*MODIFY CLK_FREQ HERE*/ int clk_freq_khz = 2000;

void setup()
{
  // Always initialize Serial for data transfer functionality
  Serial.begin(SERIAL_BAUD);
  while (!Serial)
    delay(10);

#if (DEBUG_STATEMENT)
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

#if (DEBUG_STATEMENT)
  Serial.println("Ready for serial data transfer commands");
#endif
}

void loop()
{
  // Check for incoming serial data transfer commands
  if (Serial.available()) {
    handleSerialCommand();
  }

  // Small delay to prevent excessive CPU usage
  delay(10);
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
  SPI.writeBytes(Data, lenData); // Send all 16 bytes at once (write-only)

  digitalWrite(SHIFT_PIN, LOW); // End SHIFT

  // Extra few cycles to save shift status
  SPI.transfer(0x00);           // Dummy bytes for extra cycles

  digitalWrite(LED_BUILTIN, LOW);
#if (DEBUG_STATEMENT)
  Serial.println("Data transmission completed");
#endif
}

// Handle incoming serial commands for data transfer
void handleSerialCommand()
{
  static byte receivedData[EXPECTED_DATA_SIZE];
  static int dataIndex = 0;
  static bool receivingData = false;

  while (Serial.available() > 0) {
    char receivedChar = Serial.read();

    if (receivedChar == DATA_START_MARKER) {
      // Start of new data packet
      receivingData = true;
      dataIndex = 0;
#if (DEBUG_STATEMENT)
      Serial.println("Start receiving data...");
#endif
    }
    else if (receivedChar == DATA_END_MARKER) {
      // End of data packet
      if (receivingData && dataIndex == EXPECTED_DATA_SIZE) {
        // Update the Data array with received values
        for (int i = 0; i < EXPECTED_DATA_SIZE; i++) {
          Data[i] = receivedData[i];
        }

        // Send confirmation and execute data sequence
        Serial.println("DATA_UPDATED");
        sendDataSequence();
        Serial.println("TRANSFER_COMPLETE");

#if (DEBUG_STATEMENT)
        Serial.print("Updated data: ");
        for (int i = 0; i < EXPECTED_DATA_SIZE; i++) {
          Serial.print(Data[i]);
          if (i < EXPECTED_DATA_SIZE - 1) Serial.print(",");
        }
        Serial.println();
#endif
      } else {
        Serial.println("ERROR_INVALID_DATA_SIZE");
      }
      receivingData = false;
      dataIndex = 0;
    }
    else if (receivedChar == RESET_COMMAND && !receivingData) {
      // Handle reset command (single character 'R')
#if (DEBUG_STATEMENT)
      Serial.println("Reset command received");
#endif
      Serial.println("RESET_STARTED");
      sendResetSequence();
      Serial.println("RESET_COMPLETE");
    }
    else if (receivingData) {
      // Receiving data bytes
      if (dataIndex < EXPECTED_DATA_SIZE) {
        receivedData[dataIndex] = (byte)receivedChar;
        dataIndex++;
      }
    }
  }
}