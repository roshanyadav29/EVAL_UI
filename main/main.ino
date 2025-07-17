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
/*MODIFY DATA HERE*/ byte Data[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};

const int lenData = 16;  // Number of bytes in Data array (128 bits total)

/*MODIFY CLK_FREQ HERE*/ int clk_freq_khz = 100;

// Calculate delay based on frequency (half period in microseconds) - for legacy functions
int clk_half_period_us;

// High-precision timing using ESP32 hardware timer
hw_timer_t * timer = NULL;
volatile bool timer_flag = false;
volatile bool clock_state = false;

// Forward declarations
void IRAM_ATTR onTimer();
void IRAM_ATTR waitForTimerTicks(int ticks);
void IRAM_ATTR waitForFallingEdge();
void IRAM_ATTR waitForRisingEdge();
void sendTimerBasedData();
void sendTimerBasedResetOnly();

void setup() {
  // Initialize serial for debugging
  Serial.begin(115200);
  delay(1000);

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

  // Setup hardware timer for precise clock generation
  // ESP32 Arduino Core 3.x timer API
  // Calculate timer frequency: for 100kHz clock, we need 200kHz timer (2 ticks per cycle)
  uint32_t timer_frequency = clk_freq_khz * 2 * 1000;  // Timer frequency in Hz
  
  // Calculate legacy delay variable for compatibility
  clk_half_period_us = 1000000 / (2 * clk_freq_khz * 1000);
  
  timer = timerBegin(timer_frequency);  // Initialize timer with frequency
  timerAttachInterrupt(timer, &onTimer);  // Attach interrupt function
  timerStart(timer);  // Start the timer
  
  Serial.print("Clock frequency: ");
  Serial.print(clk_freq_khz);
  Serial.println(" kHz");
  Serial.print("Timer frequency: ");
  Serial.print(timer_frequency);
  Serial.println(" Hz");

  delay(1000);  // Short delay for initialization

  // Send data using custom protocol
  sendTimerBasedResetOnly();

  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  // Stay in idle state - transmission completed in setup()
}

// Timer interrupt service routine - optimized for precision
void IRAM_ATTR onTimer() {
  timer_flag = true;
  clock_state = !clock_state;
  // Use digitalWrite for compatibility
  digitalWrite(CLOCK_PIN, clock_state);
}

void sendTimerBasedData() {
  Serial.println("Starting timer-based data transmission...");
  
  // 1. Setup initial state - stop timer first
  timerStop(timer);
  digitalWrite(RESET_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);
  digitalWrite(CLOCK_PIN, LOW);
  clock_state = false;
  timer_flag = false;
  
  // Start timer for precise timing
  timerStart(timer);
  
  // 2. RESET low for exactly 2 clock cycles (4 timer half-periods)
  waitForTimerTicks(4);
  
  // 3. RESET goes high on next falling edge
  waitForFallingEdge();
  digitalWrite(RESET_PIN, HIGH);
  
  // Wait for one complete clock cycle (2 half-periods)
  waitForTimerTicks(2);
  
  // 4. SHIFT goes high on next falling edge
  waitForFallingEdge();
  digitalWrite(SHIFT_PIN, HIGH);
  
  // 5. Begin data transmission
  for (int byte_index = 0; byte_index < lenData; byte_index++) {
    byte current_byte = Data[byte_index];
    
    for (int bit_index = 7; bit_index >= 0; bit_index--) {
      // Set DATA on falling edge
      waitForFallingEdge();
      digitalWrite(DATA_PIN, (current_byte >> bit_index) & 0x01);
      
      // Wait for rising edge (device samples DATA)
      waitForRisingEdge();
    }
  }
  
  // 6. SHIFT low after data transmission on falling edge
  waitForFallingEdge();
  digitalWrite(SHIFT_PIN, LOW);
  
  // 7. Post-transmission: 2 complete clock cycles (4 half-periods)
  waitForTimerTicks(4);
  
  // Stop timer and set idle state
  timerStop(timer);
  digitalWrite(CLOCK_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  
  Serial.println("Timer-based transmission completed");
}

void sendTimerBasedResetOnly() {
  Serial.println("Starting timer-based reset...");
  
  // Stop timer first
  timerStop(timer);
  digitalWrite(RESET_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);
  digitalWrite(CLOCK_PIN, LOW);
  clock_state = false;
  timer_flag = false;
  
  // Start timer for precise timing
  timerStart(timer);
  
  // RESET low for exactly 2 clock cycles (4 timer half-periods)
  waitForTimerTicks(4);
  
  // Return RESET to high state on falling edge
  waitForFallingEdge();
  digitalWrite(RESET_PIN, HIGH);
  
  // Stop timer and ensure idle state
  timerStop(timer);
  digitalWrite(CLOCK_PIN, LOW);
  digitalWrite(DATA_PIN, LOW);
  digitalWrite(SHIFT_PIN, LOW);
  
  Serial.println("Timer-based reset completed");
}

// Helper functions for precise timer synchronization
void IRAM_ATTR waitForTimerTicks(int ticks) {
  int tick_count = 0;
  timer_flag = false;
  while (tick_count < ticks) {
    if (timer_flag) {
      timer_flag = false;
      tick_count++;
    }
  }
}

void IRAM_ATTR waitForFallingEdge() {
  // Wait for next timer tick when clock goes low
  while (!timer_flag) { /* wait */ }
  timer_flag = false;
  while (clock_state) {  // Wait until we're on falling edge
    while (!timer_flag) { /* wait */ }
    timer_flag = false;
  }
}

void IRAM_ATTR waitForRisingEdge() {
  // Wait for next timer tick when clock goes high
  while (!timer_flag) { /* wait */ }
  timer_flag = false;
  while (!clock_state) {  // Wait until we're on rising edge
    while (!timer_flag) { /* wait */ }
    timer_flag = false;
  }
}