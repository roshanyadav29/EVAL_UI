//"""CONFIGURES ARDUINO FOR CUSTOM SERIAL PROTOCOL"""
// This code is designed to run on an ESP32 board and implements a custom serial protocol
// for communication with a slave device. It uses GPIO pins to send data in a specific sequence

/*MODIFY GPIO PINS HERE*/ 
const int CLOCK_PIN = 27;
const int DATA_PIN = 25;
const int SHIFT_PIN = 26;
const int RESET_PIN = 33;
const int LED_BUILTIN = 2;    // Built-in LED pin (usually GPIO 2 on ESP32)

// Value to be sent by the MASTER (128 bits = 16 bytes)
/*MODIFY DATA HERE*/ byte Data[16] = {56,112,21,0,0,6,240,0,0,0,0,4,1,128,0,0};

const int lenData = 16;  // Number of bytes in Data array (128 bits total)

/*MODIFY CLK_FREQ HERE*/ int clk_freq_khz = 100;

// Calculate delay based on frequency (half period in microseconds)
int clk_half_period_us;

void setup() {
  // Initialize serial for debugging
  Serial.begin(115200);
  delay(1000);

  // Calculate clock half period based on frequency
  // Formula: half_period = 1 / (2 * frequency)
  // Convert kHz to Hz: clk_freq_khz * 1000
  // Convert to microseconds: * 1000000
  clk_half_period_us = 1000000 / (2 * clk_freq_khz * 1000);

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
  digitalWrite(RESET_PIN, HIGH);  // Reset high normally
  digitalWrite(LED_BUILTIN, HIGH);

  delay(1000);  // Short delay for initialization

  // Send data using custom protocol
  sendSerialData();

  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  // Stay in idle state - transmission completed in setup()
}

void sendSerialData() {
  // 1. RESET low for exactly 2 clock cycles
  digitalWrite(RESET_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  for (int i = 0; i < 2; i++) {
    digitalWrite(CLOCK_PIN, LOW);
    delayMicroseconds(clk_half_period_us);
    digitalWrite(CLOCK_PIN, HIGH);
    delayMicroseconds(clk_half_period_us);
  }

  // 2. RESET goes high at falling edge, then one complete clock cycle
  digitalWrite(CLOCK_PIN, LOW);  // Falling edge
  digitalWrite(RESET_PIN, HIGH); // RESET changes on falling edge
  delayMicroseconds(clk_half_period_us);
  digitalWrite(CLOCK_PIN, HIGH);
  delayMicroseconds(clk_half_period_us);

  // 3. SHIFT goes high on falling edge, starting data transmission
  digitalWrite(CLOCK_PIN, LOW);  // Falling edge
  digitalWrite(SHIFT_PIN, HIGH); // SHIFT changes on falling edge
  
  // 4. Begin data transmission (all data changes on falling edges)
  for (int byte_index = 0; byte_index < lenData; byte_index++) {
    byte current_byte = Data[byte_index];
    
    for (int bit_index = 7; bit_index >= 0; bit_index--) {   
      // Set DATA on falling edge
      digitalWrite(DATA_PIN, (current_byte >> bit_index) & 0x01);
      delayMicroseconds(clk_half_period_us);
      
      // Rising edge - device samples DATA
      digitalWrite(CLOCK_PIN, HIGH);
      delayMicroseconds(clk_half_period_us);
      
      // Prepare falling edge for next bit (except for last bit)
      if (!(byte_index == lenData-1 && bit_index == 0)) {
        digitalWrite(CLOCK_PIN, LOW);
      }
    }
  }

  // 5. SHIFT low after data transmission (end of transmission)
  digitalWrite(SHIFT_PIN, LOW);
  
  // 6. Post-transmission: a few clock cycles to register shift status
  for (int i = 0; i < 2; i++) {
    digitalWrite(CLOCK_PIN, LOW);
    delayMicroseconds(clk_half_period_us);
    digitalWrite(CLOCK_PIN, HIGH);
    delayMicroseconds(clk_half_period_us);
  }

  // 7. Return to idle state with CLOCK and DATA low
  digitalWrite(CLOCK_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);
}

void sendResetOnly() {
  // RESET-only operation: just send RESET low for a few clock cycles
  digitalWrite(RESET_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);

  // Send reset pulse for a few clock cycles
  for (int i = 0; i < 2; i++) {
    digitalWrite(CLOCK_PIN, LOW);
    delayMicroseconds(clk_half_period_us);
    digitalWrite(CLOCK_PIN, HIGH);
    delayMicroseconds(clk_half_period_us);
  }

  // Return RESET to high state
  digitalWrite(RESET_PIN, HIGH);

  // Ensure all pins are in idle state
  digitalWrite(CLOCK_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
}
