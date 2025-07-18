//"""CONFIGURES ARDUINO FOR CUSTOM SERIAL PROTOCOL"""
// This code is designed to run on an ESP32 board and implements a custom serial protocol
// for communication with a slave device. It uses GPIO pins to send data in a specific sequence

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

const uint32_t half_period_us = 1000000 / (2 * clk_freq_khz * 1000);;

// Protocol control variables
bool reset_complete = false;
bool transmission_complete = false;

void setup()
{
  // Initialize serial for debugging
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Custom Protocol Controller");

  // Configure GPIO pins
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(CLOCK_PIN, OUTPUT);
  pinMode(DATA_PIN, OUTPUT);
  pinMode(SHIFT_PIN, OUTPUT);
  pinMode(RESET_PIN, OUTPUT);

  // Initialize pins to default state
  digitalWrite(CLOCK_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  digitalWrite(RESET_PIN, HIGH); // Reset high normally
  digitalWrite(LED_BUILTIN, HIGH);

  // Output configuration
  Serial.print("Clock frequency: ");
  Serial.print(clk_freq_khz);
  Serial.println(" kHz");
  Serial.print("Half period: ");
  Serial.print(half_period_us);
  Serial.println(" us");

  delay(1000); // Short delay for initialization

  // Perform reset sequence
  sendDataSequence();
  digitalWrite(LED_BUILTIN, LOW);

  Serial.println("Reset complete, system ready");
}

void loop()
{
  // Optional: implement command handling here
  // For now, just stay in idle state
}

void sendResetSequence()
{
  Serial.println("Starting reset sequence...");

  // Prepare for reset
  digitalWrite(LED_BUILTIN, HIGH);
  reset_complete = false;

  // Set initial state
  digitalWrite(RESET_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);
  digitalWrite(CLOCK_PIN, LOW);

  Serial.print("Half period: ");
  Serial.print(half_period_us);
  Serial.println(" us");

  // Generate 2 clock cycles (4 half periods) with RESET LOW
  for (int i = 0; i < 4; i++)
  {
    if (i % 2 == 0)
    {
      digitalWrite(CLOCK_PIN, HIGH);
    }
    else
    {
      digitalWrite(CLOCK_PIN, LOW);
    }
    delayMicroseconds(half_period_us);
  }

  // Ensure we end on falling edge, then set RESET HIGH
  digitalWrite(CLOCK_PIN, LOW);
  digitalWrite(RESET_PIN, HIGH);

  // Final state - keep clock low
  digitalWrite(CLOCK_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);

  reset_complete = true;
  Serial.println("Reset sequence completed successfully");
}

void sendDataSequence()
{
  Serial.println("Starting data transmission...");

  // Prepare for data transmission
  digitalWrite(LED_BUILTIN, HIGH);
  transmission_complete = false;

  // First do reset
  sendResetSequence();

  if (!reset_complete)
  {
    Serial.println("Reset failed, aborting data transmission");
    return;
  }

  Serial.println("Starting data transmission after reset");

  // Set SHIFT HIGH for data transmission
  digitalWrite(SHIFT_PIN, HIGH);

  // Transmit all 128 bits (16 bytes)
  for (int byte_idx = 0; byte_idx < lenData; byte_idx++)
  {
    for (int bit_idx = 0; bit_idx < 8; bit_idx++)
    {
      // Generate clock falling edge
      digitalWrite(CLOCK_PIN, LOW);

      // Set data bit (MSB first)
      uint8_t bit_value = (Data[byte_idx] >> (7 - bit_idx)) & 0x01;
      digitalWrite(DATA_PIN, bit_value);

      delayMicroseconds(half_period_us);

      // Generate clock rising edge
      digitalWrite(CLOCK_PIN, HIGH);
      delayMicroseconds(half_period_us);
    }
  }

  // Generate 2 clock cycles (4 half periods) with RESET LOW
  for (int i = 0; i < 4; i++)
  {
    if (i % 2 == 0)
    {
      digitalWrite(CLOCK_PIN, HIGH);
    }
    else
    {
      digitalWrite(CLOCK_PIN, LOW);
    }
    delayMicroseconds(half_period_us);
  }

  // End with clock low and shift low
  digitalWrite(CLOCK_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);

  transmission_complete = true;
  Serial.println("Data transmission completed successfully");

  // Turn off LED
  digitalWrite(LED_BUILTIN, LOW);
}