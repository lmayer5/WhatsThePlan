"""
College Bar Night Simulation
----------------------------
Simulates realistic Friday night traffic at college bars from 7 PM to 2 AM.
Duration: 10 real-world minutes = 7 virtual hours.

Traffic Pattern (Typical Friday Night):
- 7-8 PM:   Early birds, staff, regulars (Low)
- 8-9 PM:   First wave after dinner (Moderate)
- 9-10 PM:  Main crowd arriving (High)
- 10-11 PM: Peak hour (Maximum)
- 11-12 AM: Late peak, some leaving (High)
- 12-1 AM:  Winding down, last call approaching (Moderate)
- 1-2 AM:   Last call, closing time (Low)
"""

import time
import datetime
import random
import os

# ==================== CONFIGURATION ====================

CSV_FILE = "current_log.csv"

# Time Compression
REAL_DURATION_SECONDS = 600  # 10 real minutes
VIRTUAL_START_HOUR = 19       # 7:00 PM
VIRTUAL_END_HOUR = 26         # 2:00 AM (next day, represented as 26)
TOTAL_VIRTUAL_HOURS = VIRTUAL_END_HOUR - VIRTUAL_START_HOUR  # 7 hours

# Venues with personality
VENUES = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "name": "Joe Kool's",
        "type": "popular",        # Most popular bar in town
        "peak_multiplier": 1.5,   # Draws bigger crowds
        "early_crowd": True,      # Gets busy earlier
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "name": "Barney's",
        "type": "popular",
        "peak_multiplier": 1.4,
        "early_crowd": True,
    },
    {
        "id": "00000000-0000-0000-0000-000000000003",
        "name": "Molly Bloom's",
        "type": "casual",         # Moderate crowd
        "peak_multiplier": 1.0,
        "early_crowd": False,
    },
    {
        "id": "00000000-0000-0000-0000-000000000004",
        "name": "The Ceeps",
        "type": "late_night",     # Gets busy later
        "peak_multiplier": 1.2,
        "early_crowd": False,
    },
    {
        "id": "00000000-0000-0000-0000-000000000005",
        "name": "Toboggan",
        "type": "dive",           # Consistent but smaller crowd
        "peak_multiplier": 0.7,
        "early_crowd": True,
    },
]

# ==================== TRAFFIC CURVES ====================

def get_base_traffic(virtual_hour: float) -> int:
    """
    Returns base transaction count based on time of night.
    Models a typical Friday night traffic pattern.
    """
    hour = int(virtual_hour)
    
    # Early Evening (7-8 PM): Light
    if hour == 19:
        return random.randint(2, 6)
    
    # Warming Up (8-9 PM): Moderate
    elif hour == 20:
        return random.randint(8, 15)
    
    # Getting Busy (9-10 PM): High
    elif hour == 21:
        return random.randint(15, 25)
    
    # Peak Hour (10-11 PM): Maximum
    elif hour == 22:
        return random.randint(25, 40)
    
    # Late Peak (11 PM - 12 AM): Still High
    elif hour == 23:
        return random.randint(20, 35)
    
    # Winding Down (12-1 AM): Moderate
    elif hour == 24:
        return random.randint(10, 20)
    
    # Closing Time (1-2 AM): Low
    elif hour == 25:
        return random.randint(2, 8)
    
    return 0


def apply_venue_modifier(base_traffic: int, venue: dict, virtual_hour: float) -> int:
    """
    Adjusts traffic based on venue personality.
    """
    traffic = base_traffic
    hour = int(virtual_hour)
    
    # Apply peak multiplier
    traffic = int(traffic * venue["peak_multiplier"])
    
    # Early crowd venues get extra traffic 7-9 PM
    if venue["early_crowd"] and hour in [19, 20]:
        traffic = int(traffic * 1.3)
    
    # Late night venues get extra traffic after midnight
    if venue["type"] == "late_night" and hour >= 24:
        traffic = int(traffic * 1.5)
    
    # Dive bars are more consistent
    if venue["type"] == "dive":
        # Less variance, more steady
        traffic = int(traffic * 0.8) + random.randint(-2, 2)
    
    # Random surge events (sports game ending, etc.) - 5% chance
    if random.random() < 0.05:
        surge = random.randint(10, 25)
        traffic += surge
        print(f"    🚨 SURGE at {venue['name']}: +{surge} people!")
    
    return max(0, traffic)


# ==================== MAIN SIMULATION ====================

def simulate():
    """
    Main simulation loop.
    Compresses 7 virtual hours (7PM-2AM) into 10 real minutes.
    """
    print("=" * 60)
    print("🍺 COLLEGE BAR FRIDAY NIGHT SIMULATION 🍺")
    print("=" * 60)
    print(f"Virtual Time: 7:00 PM → 2:00 AM ({TOTAL_VIRTUAL_HOURS} hours)")
    print(f"Real Time: {REAL_DURATION_SECONDS // 60} minutes")
    print(f"Output: {CSV_FILE}")
    print("=" * 60)
    print()

    start_time = time.time()
    update_interval = 2  # Write data every 2 seconds

    while True:
        elapsed = time.time() - start_time
        if elapsed > REAL_DURATION_SECONDS:
            break

        # Calculate virtual time
        progress = elapsed / REAL_DURATION_SECONDS
        virtual_hour = VIRTUAL_START_HOUR + (progress * TOTAL_VIRTUAL_HOURS)
        
        # Format for display
        display_hour = int(virtual_hour) % 24
        display_minute = int((virtual_hour % 1) * 60)
        time_str = f"{display_hour:02d}:{display_minute:02d}"
        
        # Progress bar
        bar_len = 40
        filled = int(bar_len * progress)
        bar = "█" * filled + "░" * (bar_len - filled)
        
        print(f"\r[{bar}] {int(progress * 100):3d}% | 🕐 {time_str}", end="", flush=True)

        # Construct virtual timestamp for database
        base_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        virtual_dt = base_date + datetime.timedelta(hours=virtual_hour)
        timestamp_iso = virtual_dt.isoformat()

        # Generate transactions for each venue
        with open(CSV_FILE, "a") as f:
            for venue in VENUES:
                base = get_base_traffic(virtual_hour)
                quantity = apply_venue_modifier(base, venue, virtual_hour)
                
                if quantity > 0:
                    line = f"{timestamp_iso},{venue['id']},{quantity}\n"
                    f.write(line)

        time.sleep(update_interval)

    print()
    print()
    print("=" * 60)
    print("🎉 SIMULATION COMPLETE!")
    print("=" * 60)


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    # Write PID for process management
    pid_file = "/tmp/simulate_traffic.pid"
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))
    
    # Clear/create the CSV file
    with open(CSV_FILE, "w") as f:
        pass  # Create empty file
    
    print(f"Traffic Simulator running (PID: {os.getpid()})")
    try:
        simulate()
    except KeyboardInterrupt:
        print("\n\n⛔ Simulation stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup PID file
        if os.path.exists(pid_file):
            os.remove(pid_file)
