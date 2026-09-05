import os
from day1_worker_data import run_day1
from day2_worker_assignment import run_day2
from day3_flood_routing import run_day3
from day4_notifications import run_day4
from send_sms_fast2sms import send_dispatch_sms

def main():
    print("=" * 80)
    print("HydroGraph-Twin — MEMBER 6: Worker Assignment, Safe Routing & Alert Pipeline")
    print("=" * 80)

    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Day 1 -> Day 4
    run_day1()
    run_day2()
    run_day3()
    run_day4()

    print("\n" + "=" * 80)
    print("[SUCCESS] Member 6 Pipeline Executed Successfully!")
    print("Outputs saved in /output:")
    print("  1. output/worker_assignment_output.csv")
    print("  2. output/route_output.csv")
    print("  3. output/notification_output.csv")
    print("=" * 80)

    # Trigger SMS dispatch
    print("\nTriggering Fast2SMS notification engine...")
    send_dispatch_sms()

if __name__ == "__main__":
    main()