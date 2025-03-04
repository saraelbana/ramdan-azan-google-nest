import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
import datetime
import time
from config.Main import check_and_play, play_sound_on_nest, play_mesaharaty_on_all_devices, update_prayer_times
import pychromecast

# Disable the SSL warning
import warnings
warnings.filterwarnings("ignore", category=Warning)

# Mock prayer times for a full day simulation
test_prayer_times = {
    "FAJR": {"name": "FAJR", "time": datetime.time(5, 30)},      # 5:30 AM
    "SHUROOQ": {"name": "SHUROOQ", "time": datetime.time(6, 45)}, # 6:45 AM
    "DHUHR": {"name": "DHUHR", "time": datetime.time(12, 15)},    # 12:15 PM
    "ASR": {"name": "ASR", "time": datetime.time(15, 30)},        # 3:30 PM
    "MAGHRIB": {"name": "MAGHRIB", "time": datetime.time(18, 15)}, # 6:15 PM
    "ISHA": {"name": "ISHA", "time": datetime.time(19, 45)}       # 7:45 PM
}

def mock_update_prayer_times():
    global test_prayer_times
    return test_prayer_times

# Mock the sound playback
def mock_play_sound(*args, **kwargs):
    print(f"\n🔊 Would play sound on device: {kwargs.get('nest_name', 'unknown device')}")
    print(f"   URL: {kwargs.get('sound_url', 'unknown url')}")
    print(f"   Duration: {kwargs.get('sleep_duration', 0)} seconds")
    print(f"   Volume: {kwargs.get('preferred_volume', 0)}")
    return True

# Times to simulate (in 24-hour format)
simulation_times = [
    # Mesaharaty times
    (4, 0),   # First Mesaharaty (1h30m before Fajr)
    (4, 30),  # Second Mesaharaty (1h before Fajr)
    (5, 0),   # Third Mesaharaty (30m before Fajr)
    
    # Prayer times
    (5, 30),  # Fajr
    (6, 45),  # Shurooq
    (12, 15), # Dhuhr
    (15, 30), # Asr
    (18, 15), # Maghrib
    (19, 45), # Isha
    
    # Some times in between (no sounds should play)
    (3, 45),  # Before first Mesaharaty
    (7, 0),   # Between prayers
    (14, 0),  # Between prayers
    (23, 0),  # Late night
]

def run_simulation():
    print("\n🕌 Starting Prayer Times Simulation 🕌")
    print("=" * 50)
    
    # Sort times for chronological simulation
    simulation_times.sort()
    
    # Set up all our mocks
    with patch('config.Main.update_prayer_times', side_effect=mock_update_prayer_times), \
         patch('config.Main.get_times_from_webpage') as mock_get_times, \
         patch('requests.get') as mock_requests:
        
        # Update prayer times at start
        update_prayer_times()
        
        for hour, minute in simulation_times:
            # Create the simulated current time
            current_time = datetime.datetime(2025, 3, 4, hour, minute)
            
            print(f"\n⏰ Simulating Time: {current_time.strftime('%I:%M %p')}")
            print("-" * 30)
            
            # Set up time-specific mocks
            with patch('datetime.datetime') as mock_datetime, \
                 patch('config.Main.parsed_times', test_prayer_times), \
                 patch('config.Main.play_sound_on_nest', side_effect=mock_play_sound), \
                 patch('config.Main.play_mesaharaty_on_all_devices') as mock_mesaharaty:
                
                # Configure datetime mock
                mock_datetime.now.return_value = current_time
                mock_datetime.combine = datetime.datetime.combine
                
                # Configure mesaharaty mock
                def mock_mesaharaty_play(*args, **kwargs):
                    print(f"\n🌙 Playing Mesaharaty")
                    mock_play_sound(sound_url=args[0], sleep_duration=args[1], preferred_volume=args[2])
                mock_mesaharaty.side_effect = mock_mesaharaty_play
                
                try:
                    # Run the check_and_play function
                    check_and_play()
                    # Small delay for readability
                    time.sleep(0.5)
                except Exception as e:
                    print(f"❌ Error during simulation: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Simulation Complete!")

if __name__ == "__main__":
    run_simulation()
