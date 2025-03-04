import unittest
from unittest.mock import patch, MagicMock
import datetime
from config.Main import schedule_next_prayer, check_and_play, play_mesaharaty_on_all_devices, play_sound_on_nest

class TestPrayerTimes(unittest.TestCase):
    def setUp(self):
        # Mock prayer times for testing
        self.test_prayer_times = {
            "FAJR": {"name": "FAJR", "time": datetime.time(5, 30)},  # 5:30 AM
            "SHUROOQ": {"name": "SHUROOQ", "time": datetime.time(6, 45)},  # 6:45 AM
            "DHUHR": {"name": "DHUHR", "time": datetime.time(12, 15)},  # 12:15 PM
            "ASR": {"name": "ASR", "time": datetime.time(15, 30)},  # 3:30 PM
            "MAGHRIB": {"name": "MAGHRIB", "time": datetime.time(18, 15)},  # 6:15 PM
            "ISHA": {"name": "ISHA", "time": datetime.time(19, 45)}  # 7:45 PM
        }
        
    def test_mesaharaty_scheduling(self):
        test_cases = [
            # Test case 1: Current time is 2 AM (should schedule first Mesaharaty at 4:00 AM)
            (datetime.datetime(2025, 3, 4, 2, 0), "MESAHARATY_1", "04:00"),
            
            # Test case 2: Current time is 3:45 AM (should schedule second Mesaharaty at 4:30 AM)
            (datetime.datetime(2025, 3, 4, 3, 45), "MESAHARATY_2", "04:30"),
            
            # Test case 3: Current time is 4:45 AM (should schedule third Mesaharaty at 5:00 AM)
            (datetime.datetime(2025, 3, 4, 4, 45), "MESAHARATY_3", "05:00"),
            
            # Test case 4: Current time is 5:15 AM (should schedule Fajr at 5:30 AM)
            (datetime.datetime(2025, 3, 4, 5, 15), "FAJR", "05:30"),
            
            # Test case 5: Current time is 11:00 PM (should schedule next day's first Mesaharaty)
            (datetime.datetime(2025, 3, 4, 23, 0), "MESAHARATY_1", "04:00")
        ]
        
        for current_time, expected_name, expected_time in test_cases:
            with patch('datetime.datetime') as mock_datetime:
                mock_datetime.now.return_value = current_time
                mock_datetime.combine = datetime.datetime.combine
                
                with patch('config.Main.parsed_times', self.test_prayer_times):
                    with patch('schedule.every') as mock_schedule:
                        mock_schedule.day = MagicMock()
                        schedule_next_prayer()
                        
                        # Extract the scheduled time from the mock calls
                        scheduled_time = None
                        scheduled_name = None
                        
                        # Print debug information
                        print(f"\nTest case - Current time: {current_time.strftime('%H:%M')}")
                        print(f"Expected next prayer: {expected_name} at {expected_time}")
                        
                        self.assertTrue(mock_schedule.day.at.called)
                        called_time = mock_schedule.day.at.call_args[0][0]
                        self.assertEqual(called_time, expected_time)

    def test_mesaharaty_playback(self):
        test_cases = [
            # Test case 1: Exactly at first Mesaharaty time (1h30m before Fajr)
            (datetime.datetime(2025, 3, 4, 4, 0), True, "first Mesaharaty"),
            
            # Test case 2: Exactly at second Mesaharaty time (1h before Fajr)
            (datetime.datetime(2025, 3, 4, 4, 30), True, "second Mesaharaty"),
            
            # Test case 3: Exactly at third Mesaharaty time (30m before Fajr)
            (datetime.datetime(2025, 3, 4, 5, 0), True, "third Mesaharaty"),
            
            # Test case 4: 3 minutes after scheduled time (should not play)
            (datetime.datetime(2025, 3, 4, 4, 3), False, None),
            
            # Test case 5: 1 minute before scheduled time (should not play)
            (datetime.datetime(2025, 3, 4, 3, 59), False, None)
        ]
        
        for current_time, should_play, mesaharaty_type in test_cases:
            with patch('datetime.datetime') as mock_datetime:
                mock_datetime.now.return_value = current_time
                mock_datetime.combine = datetime.datetime.combine
                
                with patch('config.Main.parsed_times', self.test_prayer_times):
                    with patch('config.Main.play_mesaharaty_on_all_devices') as mock_play:
                        check_and_play()
                        
                        print(f"\nTest case - Current time: {current_time.strftime('%H:%M')}")
                        print(f"Should play: {should_play}, Type: {mesaharaty_type}")
                        
                        if should_play:
                            mock_play.assert_called_once()
                        else:
                            mock_play.assert_not_called()

    def test_prayer_times_scheduling(self):
        test_cases = [
            # Test regular prayer times throughout the day
            (datetime.datetime(2025, 3, 4, 5, 0), "FAJR", "05:30"),
            (datetime.datetime(2025, 3, 4, 6, 0), "SHUROOQ", "06:45"),
            (datetime.datetime(2025, 3, 4, 11, 0), "DHUHR", "12:15"),
            (datetime.datetime(2025, 3, 4, 14, 0), "ASR", "15:30"),
            (datetime.datetime(2025, 3, 4, 17, 0), "MAGHRIB", "18:15"),
            (datetime.datetime(2025, 3, 4, 19, 0), "ISHA", "19:45")
        ]
        
        for current_time, expected_name, expected_time in test_cases:
            with patch('datetime.datetime') as mock_datetime:
                mock_datetime.now.return_value = current_time
                mock_datetime.combine = datetime.datetime.combine
                
                with patch('config.Main.parsed_times', self.test_prayer_times):
                    with patch('schedule.every') as mock_schedule:
                        mock_schedule.day = MagicMock()
                        schedule_next_prayer()
                        
                        print(f"\nTest case - Current time: {current_time.strftime('%H:%M')}")
                        print(f"Expected prayer: {expected_name} at {expected_time}")
                        
                        self.assertTrue(mock_schedule.day.at.called)
                        called_time = mock_schedule.day.at.call_args[0][0]
                        self.assertEqual(called_time, expected_time)

if __name__ == '__main__':
    unittest.main()
