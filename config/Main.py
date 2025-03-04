import requests
from bs4 import BeautifulSoup
import datetime
import pychromecast
import time
import schedule
from constants.ChromeCastNamesConsttants import device_names
from constants.PrayersAzanSoundsURLConstants import azan_sound_urls
from constants.PrayersTimesCSSSelectorsConstants import css_selectors
from constants.PrayersURLConstants import mosqueUrl
from constants.DuaaVideosURLs import DUAAS
from constants.MesaharatyAudioURL import MESAHARATY

# --- Configuration ---
# --- Configuration ---
TARGET_WEBPAGE_URL = mosqueUrl["PRAYERS_TIMES_URL"]
CSS_SELECTOR_FOR_TIMES = [
    css_selectors["FAJR_PRAYER_TIME_CSS_SELECTOR"],
    css_selectors["SHUROOQ_PRAYER_TIME_CSS_SELECTOR"],
    css_selectors["DHUHR_PRAYER_TIME_CSS_SELECTOR"],
    css_selectors["ASR_PRAYER_TIME_CSS_SELECTOR"],
    css_selectors["MAGHRIB_PRAYER_TIME_CSS_SELECTOR"],
    css_selectors["ISHA_PRAYER_TIME_CSS_SELECTOR"]
]

LIVINGROOM_DEVICE_NAME = device_names["livingRoomDisplay"]
BEDROOM_DEVICE_NAME = device_names["bedroomSpeaker"]

def play_mesaharaty_on_all_devices(sound_url, sleep_duration, preferred_volune):
    devices = [LIVINGROOM_DEVICE_NAME, BEDROOM_DEVICE_NAME]
    for device in devices:
        play_sound_on_nest(sound_url, sleep_duration, device, preferred_volune)
# --- Web Scraping and Time Extraction ---
def get_times_from_webpage(url, css_selectors):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        times = []
        for selector in css_selectors:
            element = soup.select_one(selector)
            if element:
                times.append(element.text.strip())
        return times
    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return []
def update_prayer_times():
    global parsed_times
    print("Updating prayer times...")
    extracted_times = get_times_from_webpage(TARGET_WEBPAGE_URL, CSS_SELECTOR_FOR_TIMES)
    print(f"Extracted times: {extracted_times}")
    parsed_times = create_prayer_times_dict(extracted_times)
    if not parsed_times:
        print("No valid times found on the webpage.")
    else:
        print("Prayer times updated successfully.")
def create_prayer_times_dict(extracted_times):
    prayer_names = ["FAJR", "SHUROOQ", "DHUHR", "ASR", "MAGHRIB", "ISHA"]
    parsed_times = {}

    for prayer, time in zip(prayer_names, extracted_times):
        parsed_time = parse_time(time)
        if parsed_time:
            parsed_times[prayer] = {
                "name": prayer,
                "time": parsed_time
            }

    return parsed_times
def parse_time(time_str):
    try:
        # Assuming the time format is HH:MM (e.g., 14:30)
        return datetime.datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        print(f"Error parsing time: {time_str}. Please ensure it's in HH:MM format.")
        return None

extracted_times = get_times_from_webpage(TARGET_WEBPAGE_URL, CSS_SELECTOR_FOR_TIMES)
print(f"Extracted times: {extracted_times}")
parsed_times = create_prayer_times_dict(extracted_times)
if not parsed_times:
    print("No valid times found on the webpage. Exiting.")
    exit()

def schedule_next_prayer():
    now = datetime.datetime.now()
    next_prayer_time = None
    next_prayer_name = None

    # Add Mesaharaty time
    fajr_time = parsed_times.get("FAJR", {}).get("time")
    if fajr_time:
        fajr_datetime = datetime.datetime.combine(now.date(), fajr_time)
        mesaharaty_time = fajr_datetime - datetime.timedelta(hours=1, minutes=30)

        if mesaharaty_time <= now:
            mesaharaty_time += datetime.timedelta(days=1)

        if next_prayer_time is None or mesaharaty_time < next_prayer_time:
            next_prayer_time = mesaharaty_time
            next_prayer_name = "MESAHARATY"


    # Convert times to datetime for proper comparison
    for prayer, data in parsed_times.items():
        prayer_time = data["time"]
        prayer_datetime = datetime.datetime.combine(now.date(), prayer_time)

        # If prayer time has passed today, schedule for tomorrow
        if prayer_datetime <= now:
            prayer_datetime += datetime.timedelta(days=1)

        if next_prayer_time is None or prayer_datetime < next_prayer_time:
            next_prayer_time = prayer_datetime
            next_prayer_name = prayer

    # Schedule the next prayer
    schedule.clear()
    schedule.every().day.at(next_prayer_time.time().strftime("%H:%M")).do(check_and_play)
    schedule.every().day.at("01:00").do(update_prayer_times)
    schedule.every().day.at("01:01").do(schedule_next_prayer)  # Reschedule after update

    print(f"Next prayer scheduled: {next_prayer_name} at {next_prayer_time.strftime('%H:%M')}")
# --- Google Nest Playback ---
def play_sound_on_nest(sound_url, sleep_duration, nest_name, preferred_volume):
    try:
        chromecasts, browser = pychromecast.get_chromecasts()
        cast = next(cc for cc in chromecasts if cc.name == nest_name)
        cast.wait()
        cast.set_volume(preferred_volume)

        # Stop any currently playing media
        mc = cast.media_controller
        if mc.status and mc.status.player_state in ['PLAYING', 'PAUSED']:
            mc.stop()

        # Play Azan
        mc.play_media(sound_url, 'audio/mp3')
        mc.block_until_active()
        time.sleep(sleep_duration)
        mc.stop()

        # Play Duaa
        mc.play_media(DUAAS["MAGHRIB_ALSHAARAWY_DUAA_AUDIO"]["URL"], 'audio/mp3')
        mc.block_until_active()
        time.sleep(DUAAS["MAGHRIB_ALSHAARAWY_DUAA_AUDIO"]["DURATION"])
        cast.set_volume(0.4)
        mc.stop()

        # cast.quit()
        cast.disconnect()
        browser.stop_discovery()
        print(f"Played sound on {nest_name}.")
    except StopIteration:
        print(f"Google Nest device '{nest_name}' not found.")
    except Exception as e:
        print(f"Error playing sound: {e}")
# --- Time Checking and Scheduling ---
def check_and_play():
    now = datetime.datetime.now()
    print(f"Checking time: {now.strftime('%H:%M')}")
    # Check for Mesaharaty first
    fajr_time = parsed_times.get("FAJR", {}).get("time")
    if fajr_time:
        fajr_datetime = datetime.datetime.combine(now.date(), fajr_time)
        mesaharaty_time = fajr_datetime - datetime.timedelta(hours=1, minutes=30)

        # If Fajr is after midnight, adjust Mesaharaty time
        if fajr_datetime < datetime.datetime.combine(now.date(), datetime.time(hour=3)):
            mesaharaty_time = mesaharaty_time + datetime.timedelta(days=1)

        time_diff = (now - mesaharaty_time).total_seconds() / 60
        if 0 <= time_diff <= 2:
            print("Time for Mesaharaty")
            play_mesaharaty_on_all_devices(
                MESAHARATY["MESAHARATY_AUDIO"]["URL"],
                MESAHARATY["MESAHARATY_AUDIO"]["DURATION"], 0.5
            )

    for prayer, timeData in parsed_times.items():
        prayer_time = timeData["time"]
        prayer_datetime = datetime.datetime.combine(now.date(), prayer_time)

        # Allow a 2-minute window after the prayer time
        time_diff = (now - prayer_datetime).total_seconds() / 60
        if 0 <= time_diff <= 2:  # Within 2 minutes after prayer time
            print(f"Time for {prayer} prayer: {prayer_time.strftime('%H:%M')}")
            prayer_to_azan = {
                "FAJR": "FAJR_AZAN_SOUND",
                "SHUROOQ": "SHUROOQ_AZAN_SOUND",
                "DHUHR": "DHUHR_AZAN_SOUND",
                "ASR": "ASR_AZAN_SOUND",
                "MAGHRIB": "MAGHRIB_AZAN_SOUND",
                "ISHA": "ISHA_AZAN_SOUND"
            }
            azan_key = prayer_to_azan.get(prayer)
            if azan_key in azan_sound_urls:
                azan_data = azan_sound_urls[azan_key]
                if prayer in ["FAJR", "SHUROOQ"]:
                    play_sound_on_nest(
                        azan_data["URL"],
                        azan_data["DURATION"],
                        BEDROOM_DEVICE_NAME, 0.4
                    )
                elif prayer in ["DHUHR", "ASR"]:(
                    play_sound_on_nest(
                        azan_data["URL"],
                        azan_data["DURATION"],
                        LIVINGROOM_DEVICE_NAME, 0.6
                    ))
                elif prayer in ["MAGHRIB"]:(
                    play_sound_on_nest(
                        azan_data["URL"],
                        azan_data["DURATION"],
                        LIVINGROOM_DEVICE_NAME, 0.6
                    ))
                else:
                    play_sound_on_nest(
                        azan_data["URL"],
                        azan_data["DURATION"],
                        LIVINGROOM_DEVICE_NAME, 0.7
                    )
                schedule_next_prayer()
                break
# Schedule the next prayer after updating the times
schedule_next_prayer()
# Add daily update schedule
schedule.every().day.at("01:00").do(update_prayer_times)
# Initial update
update_prayer_times()

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)
