"""
Simulation and demonstration script for crash detection system
This can be run on regular Python (not MicroPython) to demonstrate the logic
"""

import time
import math
import random

class SimulatedMPU6050:
    """Simulated MPU6050 sensor for testing without hardware"""
    
    def __init__(self):
        self.base_acceleration = 1.0  # 1g gravity
        
    def get_acceleration_g(self):
        """Simulate random accelerometer readings"""
        # Add small random noise
        noise = random.uniform(-0.1, 0.1)
        ax = random.uniform(-0.2, 0.2) + noise
        ay = random.uniform(-0.2, 0.2) + noise
        az = self.base_acceleration + noise
        return ax, ay, az
    
    def get_total_acceleration(self):
        """Get total acceleration magnitude"""
        ax, ay, az = self.get_acceleration_g()
        magnitude = math.sqrt(ax*ax + ay*ay + az*az)
        return magnitude
    
    def simulate_impact(self, severity="moderate"):
        """Simulate an impact event"""
        if severity == "light":
            return random.uniform(1.5, 2.0)
        elif severity == "moderate":
            return random.uniform(2.5, 3.2)
        elif severity == "severe":
            return random.uniform(3.5, 5.0)
        else:
            return self.get_total_acceleration()

class CrashDetectorDemo:
    """Demonstration version of crash detector"""
    
    def __init__(self):
        self.sensor = SimulatedMPU6050()
        self.impact_threshold = 2.5
        self.crash_threshold = 3.5
        self.impact_count = 0
        self.crash_count = 0
        
    def check_impact(self, magnitude=None):
        """Check for impact/crash events"""
        if magnitude is None:
            magnitude = self.sensor.get_total_acceleration()
        
        if magnitude > self.crash_threshold:
            self.crash_count += 1
            print(f"🚨 CRASH DETECTED! Magnitude: {magnitude:.2f}g | Count: {self.crash_count}")
            return "crash"
        elif magnitude > self.impact_threshold:
            self.impact_count += 1
            print(f"⚠️  IMPACT DETECTED! Magnitude: {magnitude:.2f}g | Count: {self.impact_count}")
            return "impact"
        else:
            print(f"✓  Normal: {magnitude:.2f}g")
            return "normal"
    
    def demonstrate(self):
        """Run a demonstration sequence"""
        print("\n" + "="*60)
        print("CRASH DETECTION SYSTEM - SIMULATION DEMO")
        print("="*60 + "\n")
        
        print("Configuration:")
        print(f"  Impact Threshold: {self.impact_threshold}g")
        print(f"  Crash Threshold: {self.crash_threshold}g")
        print()
        
        # Simulate normal readings
        print("Phase 1: Normal Operation (5 readings)")
        print("-" * 60)
        for i in range(5):
            magnitude = self.sensor.get_total_acceleration()
            self.check_impact(magnitude)
            time.sleep(0.5)
        
        print("\nPhase 2: Light Impacts (3 readings)")
        print("-" * 60)
        for i in range(3):
            magnitude = self.sensor.simulate_impact("light")
            self.check_impact(magnitude)
            time.sleep(0.5)
        
        print("\nPhase 3: Moderate Impacts (3 readings)")
        print("-" * 60)
        for i in range(3):
            magnitude = self.sensor.simulate_impact("moderate")
            self.check_impact(magnitude)
            time.sleep(0.5)
        
        print("\nPhase 4: Severe Crashes (2 readings)")
        print("-" * 60)
        for i in range(2):
            magnitude = self.sensor.simulate_impact("severe")
            self.check_impact(magnitude)
            time.sleep(0.5)
        
        print("\nPhase 5: Return to Normal (3 readings)")
        print("-" * 60)
        for i in range(3):
            magnitude = self.sensor.get_total_acceleration()
            self.check_impact(magnitude)
            time.sleep(0.5)
        
        # Summary
        print("\n" + "="*60)
        print("DEMO COMPLETE - Summary:")
        print("="*60)
        print(f"Total Impacts Detected: {self.impact_count}")
        print(f"Total Crashes Detected: {self.crash_count}")
        print("\nThis demonstrates how the system would respond to different")
        print("levels of acceleration on actual hardware.")
        print("\nIn real deployment:")
        print("  - LED would blink for impacts")
        print("  - Buzzer would sound for crashes")
        print("  - Messages would be sent via UART")
        print("="*60 + "\n")

def run_interactive_demo():
    """Run an interactive demonstration"""
    detector = CrashDetectorDemo()
    
    print("\nInteractive Mode:")
    print("1. Run full demo")
    print("2. Simulate custom event")
    print("3. Adjust thresholds")
    print("4. Exit")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            detector.demonstrate()
        elif choice == "2":
            print("\nEvent types: light, moderate, severe, normal")
            event = input("Enter event type: ").strip().lower()
            if event in ["light", "moderate", "severe"]:
                magnitude = detector.sensor.simulate_impact(event)
            else:
                magnitude = detector.sensor.get_total_acceleration()
            detector.check_impact(magnitude)
        elif choice == "3":
            try:
                impact = float(input(f"Impact threshold (current {detector.impact_threshold}): "))
                crash = float(input(f"Crash threshold (current {detector.crash_threshold}): "))
                detector.impact_threshold = impact
                detector.crash_threshold = crash
                print(f"Thresholds updated: Impact={impact}g, Crash={crash}g")
            except ValueError:
                print("Invalid input. Thresholds unchanged.")
        elif choice == "4":
            print("Exiting...")
            return
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\nDemo interrupted")

if __name__ == "__main__":
    # Run the automated demo by default
    detector = CrashDetectorDemo()
    detector.demonstrate()
    
    # Optionally run interactive mode
    # Uncomment the next line to enable interactive mode
    # run_interactive_demo()
