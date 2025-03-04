import datetime
import time

# Mock prayer times
PRAYER_TIMES = {
    "FAJR": {"name": "FAJR", "time": datetime.time(5, 30)},      # 5:30 AM
    "SHUROOQ": {"name": "SHUROOQ", "time": datetime.time(6, 45)}, # 6:45 AM
    "DHUHR": {"name": "DHUHR", "time": datetime.time(12, 15)},    # 12:15 PM
    "ASR": {"name": "ASR", "time": datetime.time(15, 30)},        # 3:30 PM
    "MAGHRIB": {"name": "MAGHRIB", "time": datetime.time(18, 15)}, # 6:15 PM
    "ISHA": {"name": "ISHA", "time": datetime.time(19, 45)}       # 7:45 PM
}

def check_mesaharaty(current_time):
    """Check if it's time for Mesaharaty"""
    fajr_time = PRAYER_TIMES["FAJR"]["time"]
    fajr_datetime = datetime.datetime.combine(current_time.date(), fajr_time)
    
    # Calculate Mesaharaty times
    mesaharaty_time_1 = fajr_datetime - datetime.timedelta(hours=1, minutes=30)
    mesaharaty_time_2 = fajr_datetime - datetime.timedelta(hours=1)
    mesaharaty_time_3 = fajr_datetime - datetime.timedelta(minutes=30)
    
    # Adjust times if Fajr is after midnight
    if fajr_datetime < datetime.datetime.combine(current_time.date(), datetime.time(hour=3)):
        mesaharaty_time_1 += datetime.timedelta(days=1)
        mesaharaty_time_2 += datetime.timedelta(days=1)
        mesaharaty_time_3 += datetime.timedelta(days=1)
    
    # Check each Mesaharaty time with 2-minute window
    time_diff_1 = (current_time - mesaharaty_time_1).total_seconds() / 60
    time_diff_2 = (current_time - mesaharaty_time_2).total_seconds() / 60
    time_diff_3 = (current_time - mesaharaty_time_3).total_seconds() / 60
    
    if 0 <= time_diff_1 <= 2:
        return "MESAHARATY_1", "1 hour 30 minutes before Fajr"
    elif 0 <= time_diff_2 <= 2:
        return "MESAHARATY_2", "1 hour before Fajr"
    elif 0 <= time_diff_3 <= 2:
        return "MESAHARATY_3", "30 minutes before Fajr"
    return None, None

def check_prayer_time(current_time):
    """Check if it's time for any prayer"""
    for prayer, data in PRAYER_TIMES.items():
        prayer_time = data["time"]
        prayer_datetime = datetime.datetime.combine(current_time.date(), prayer_time)
        
        # Check if within 2-minute window
        time_diff = (current_time - prayer_datetime).total_seconds() / 60
        if 0 <= time_diff <= 2:
            return prayer
    return None

def run_simulation():
    print("\n🕌 Prayer Times Simulation 🕌")
    print("=" * 50)
    
    # Times to simulate
    simulation_times = [
        (4, 0),   # First Mesaharaty (1h30m before Fajr)
        (4, 30),  # Second Mesaharaty (1h before Fajr)
        (5, 0),   # Third Mesaharaty (30m before Fajr)
        (5, 30),  # Fajr
        (6, 45),  # Shurooq
        (12, 15), # Dhuhr
        (15, 30), # Asr
        (18, 15), # Maghrib
        (19, 45), # Isha
        (3, 45),  # Before first Mesaharaty
        (7, 0),   # Between prayers
        (14, 0),  # Between prayers
        (23, 0),  # Late night
    ]
    
    # Sort times chronologically
    simulation_times.sort()
    
    for hour, minute in simulation_times:
        current_time = datetime.datetime(2025, 3, 4, hour, minute)
        print(f"\n⏰ Time: {current_time.strftime('%I:%M %p')}")
        print("-" * 30)
        
        # Check for Mesaharaty
        mesaharaty_type, mesaharaty_desc = check_mesaharaty(current_time)
        if mesaharaty_type:
            print(f"🌙 {mesaharaty_type}: {mesaharaty_desc}")
            print("🔊 Playing Mesaharaty on:")
            print("   - Living Room Display")
            print("   - Bedroom speaker")
        
        # Check for prayer times
        prayer = check_prayer_time(current_time)
        if prayer:
            print(f"🕌 Prayer Time: {prayer}")
            print("🔊 Playing Azan on:")
            if prayer in ["FAJR", "SHUROOQ"]:
                print("   - Bedroom speaker")
            else:
                print("   - Living Room Display")
                print("   - Bedroom speaker")
        
        if not mesaharaty_type and not prayer:
            print("No scheduled sounds at this time")
        
        time.sleep(0.5)  # Small delay for readability
    
    print("\n" + "=" * 50)
    print("🎉 Simulation Complete!")

if __name__ == "__main__":
    run_simulation()
