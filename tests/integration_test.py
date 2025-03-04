import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import logging
from datetime import datetime, timedelta
from config.Main import play_sound_on_nest, get_times_from_webpage, update_prayer_times, check_and_play
from constants.ChromeCastNamesConsttants import device_names
from constants.PrayersURLConstants import mosqueUrl
from constants.PrayersTimesCSSSelectorsConstants import css_selectors

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('prayer_times_test.log'),
        logging.StreamHandler()
    ]
)

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting integration test")

    def test_web_scraping(self):
        """Test that we can successfully scrape prayer times from the mosque website"""
        self.logger.info("Testing web scraping functionality")
        
        # Test getting times from webpage
        times = get_times_from_webpage(mosqueUrl["PRAYERS_TIMES_URL"], [
            css_selectors["FAJR_PRAYER_TIME_CSS_SELECTOR"],
            css_selectors["SHUROOQ_PRAYER_TIME_CSS_SELECTOR"]
        ])
        
        self.assertTrue(len(times) > 0, "Should get prayer times from website")
        self.logger.info(f"Successfully retrieved {len(times)} prayer times")

    def test_device_discovery(self):
        """Test that we can discover Google Cast devices"""
        self.logger.info("Testing Google Cast device discovery")
        
        import pychromecast
        chromecasts, browser = pychromecast.get_chromecasts()
        
        # Log found devices
        self.logger.info(f"Found {len(chromecasts)} Google Cast devices:")
        for cc in chromecasts:
            self.logger.info(f"  - {cc.name} ({cc.model_name})")
        
        # Check if our configured devices exist
        device_names_list = [
            device_names["livingRoomDisplay"],
            device_names["bedroomSpeaker"]
        ]
        
        found_devices = [cc.name for cc in chromecasts]
        for device in device_names_list:
            self.logger.info(f"Checking for device: {device}")
            self.assertIn(device, found_devices, f"Device {device} should be available")

    def test_sound_playback(self):
        """Test sound playback on devices"""
        self.logger.info("Testing sound playback")
        
        # Test URL that's guaranteed to work
        test_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        test_duration = 5  # Only play for 5 seconds
        
        for device_name in [device_names["livingRoomDisplay"], device_names["bedroomSpeaker"]]:
            try:
                self.logger.info(f"Testing playback on {device_name}")
                play_sound_on_nest(test_url, test_duration, device_name, 0.3)
                self.logger.info(f"Successfully played sound on {device_name}")
            except Exception as e:
                self.logger.error(f"Error playing sound on {device_name}: {str(e)}")
                raise

def run_extended_test(duration_hours=24):
    """
    Run an extended test of the prayer times system
    
    Args:
        duration_hours (int): How many hours to run the test for
    """
    logger = logging.getLogger("extended_test")
    logger.info(f"Starting {duration_hours}-hour extended test")
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=duration_hours)
    
    try:
        # Initial update of prayer times
        update_prayer_times()
        
        while datetime.now() < end_time:
            try:
                check_and_play()
                logger.info(f"Check completed at {datetime.now().strftime('%H:%M:%S')}")
            except Exception as e:
                logger.error(f"Error during check_and_play: {str(e)}")
            
            # Wait for 1 minute before next check
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error during extended test: {str(e)}")
    finally:
        logger.info("Extended test complete")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run prayer times integration tests')
    parser.add_argument('--extended', type=int, help='Run extended test for specified hours')
    args = parser.parse_args()
    
    if args.extended:
        run_extended_test(args.extended)
    else:
        unittest.main()
