import datetime
from unittest.mock import patch
from config.Main import (
    parsed_times,
    check_and_play,
    play_sound_on_nest,
    azan_sound_urls,
    BEDROOM_DEVICE_NAME
)

def test_check_and_play():
    with patch('config.Main.datetime') as mock_datetime:
        # Mock current time for testing (e.g., 05:33)
        test_time = datetime.datetime.now().replace(hour=5, minute=33)
        mock_datetime.now.return_value = test_time
        mock_datetime.datetime = datetime.datetime
        mock_datetime.combine = datetime.datetime.combine

        # Create a test prayer entry
        test_prayer = {
            "name": "FAJR",
            "time": test_time.time()
        }

        # Clear and set up parsed_times with test data
        parsed_times.clear()
        parsed_times["FAJR"] = test_prayer

        print(f"\nTest setup:")
        print(f"Current time: {test_time.strftime('%H:%M')}")
        print(f"Prayer time: {test_prayer['time'].strftime('%H:%M')}")

        # Mock play_sound_on_nest
        with patch('config.Main.play_sound_on_nest') as mock_play:
            # Run check_and_play
            check_and_play()

            # Verify playback
            assert mock_play.called, "Azan should have played"
            args = mock_play.call_args[0]
            assert args[2] == BEDROOM_DEVICE_NAME, "Wrong device used"
            print("\n✅ Test passed: Azan played on correct device")

if __name__ == "__main__":
    try:
        test_check_and_play()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:  # Added missing colon here
        print(f"\n❌ Error occurred: {e}")