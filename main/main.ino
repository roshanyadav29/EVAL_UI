//"""CONFIGURES ARDUINO FOR CUSTOM SERIAL PROTOCOL"""
/*MODIFY GPIO PINS HERE*/ 
const int CLOCK_PIN = 13;     // Clock GPIO pin
const int DATA_PIN = 14;      // Data GPIO pin (changed from 11 - flash pin)
const int SHIFT_PIN = 12;     // Shift GPIO pin (changed from 9 - flash pin)
const int RESET_PIN = 27;     // Reset GPIO pin (changed from 12 - boot-sensitive pin)

// Value to be sent by the MASTER (128 bits = 16 bytes)
/*MODIFY DATA HERE*/ byte Data[16] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

const int lenData = 16;  // Number of bytes in Data array (128 bits total)

/*MODIFY CLK_FREQ HERE*/ int clk_freq_khz = 100;

// Calculate delay based on frequency (half period in microseconds)
int clk_half_period_us;

void setup() {
  // Initialize serial for debugging
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Starting...");

  // Calculate clock half period based on frequency
  // Formula: half_period = 1 / (2 * frequency)
  // Convert kHz to Hz: clk_freq_khz * 1000
  // Convert to microseconds: * 1000000
  clk_half_period_us = 1000000 / (2 * clk_freq_khz * 1000);
  
  // Ensure minimum delay for ESP32 timing constraints
  if (clk_half_period_us < 1) {
    clk_half_period_us = 1;  // Minimum 1 microsecond
    Serial.println("Warning: Clock frequency too high, limited to 1us half-period");
  }

  Serial.print("Clock frequency: ");
  Serial.print(clk_freq_khz);
  Serial.println(" kHz");
  Serial.print("Half period: ");
  Serial.print(clk_half_period_us);
  Serial.println(" microseconds");
  Serial.print("Actual frequency: ");
  Serial.print(1000000.0 / (2.0 * clk_half_period_us * 1000.0));
  Serial.println(" kHz");

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

  Serial.println("GPIO pins configured successfully!");
  delay(1000);  // Short delay for initialization

  // Send data using custom protocol
  sendSerialData();

  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  // Stay in idle state - transmission completed in setup()
}

void sendSerialData() {
  // 1. RESET low for a few clock cycles (preparation)
  digitalWrite(RESET_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  for (int i = 0; i < 2; i++) {
    digitalWrite(CLOCK_PIN, LOW);
    delayMicroseconds(clk_half_period_us);
    digitalWrite(CLOCK_PIN, HIGH);
    delayMicroseconds(clk_half_period_us);
  }

  // 2. SHIFT high for one clock cycle (start transmission)
  digitalWrite(SHIFT_PIN, HIGH);
  digitalWrite(CLOCK_PIN, LOW);
  delayMicroseconds(clk_half_period_us);
  digitalWrite(CLOCK_PIN, HIGH);
  delayMicroseconds(clk_half_period_us);

  // 3. RESET high, SHIFT remains high for 128 cycles (data transmission)
  digitalWrite(RESET_PIN, HIGH);
  // SHIFT stays HIGH during entire data transmission
  // Send 128 bits (16 bytes) MSB first (bit 127 to bit 0)
  for (int byte_index = 0; byte_index < lenData; byte_index++) {
    byte current_byte = Data[byte_index];
    for (int bit_index = 7; bit_index >= 0; bit_index--) {
      // Set DATA on falling edge (before clock rises)
      digitalWrite(CLOCK_PIN, LOW);
      digitalWrite(DATA_PIN, (current_byte >> bit_index) & 0x01);
      delayMicroseconds(clk_half_period_us);
      // CLOCK rising edge: device samples DATA
      digitalWrite(CLOCK_PIN, HIGH);
      delayMicroseconds(clk_half_period_us);
    }
  }

  // 4. SHIFT low after data transmission (end of transmission)
  digitalWrite(SHIFT_PIN, LOW);
  // 5. Post-transmission: a few clock cycles to save shift status
  for (int i = 0; i < 2; i++) {
    digitalWrite(CLOCK_PIN, LOW);
    delayMicroseconds(clk_half_period_us);
    digitalWrite(CLOCK_PIN, HIGH);
    delayMicroseconds(clk_half_period_us);
  }

  // 6. Ensure DATA and CLOCK are low
  digitalWrite(DATA_PIN, LOW);
  digitalWrite(CLOCK_PIN, LOW);
}

void sendResetOnly() {
  // RESET-only operation: just send RESET low for a few clock cycles
  Serial.println("Starting RESET-only operation...");

  Serial.println("Setting pins to initial state...");
  digitalWrite(RESET_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);

  Serial.println("Starting reset pulse sequence...");
  // Send reset pulse for a few clock cycles
  for (int i = 0; i < 2; i++) {
    Serial.print("Reset pulse cycle ");
    Serial.println(i + 1);

    digitalWrite(CLOCK_PIN, LOW);
    delayMicroseconds(clk_half_period_us);
    digitalWrite(CLOCK_PIN, HIGH);
    delayMicroseconds(clk_half_period_us);

    // Feed the watchdog every cycle to prevent reset
    yield();
    Serial.print("Completed cycle ");
    Serial.println(i + 1);
  }

  Serial.println("Returning RESET to high state...");
  // Return RESET to high state
  digitalWrite(RESET_PIN, HIGH);

  // Ensure all pins are in idle state
  digitalWrite(CLOCK_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);

  Serial.println("RESET-only operation completed!");
}
