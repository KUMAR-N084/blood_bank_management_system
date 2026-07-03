import os
import sys
import subprocess
import shutil
from pathlib import Path

# Blood Bank Management System - Reset Demo Script
BASE_DIR = Path(__file__).resolve().parent

def run_cmd(args):
    print(f"Running: {' '.join(args)}")
    res = subprocess.run(args, cwd=BASE_DIR, shell=True)
    if res.returncode != 0:
        print(f"Error executing command: {' '.join(args)}")
        sys.exit(res.returncode)

def main():
    print("=" * 60)
    print("      BLOOD BANK MANAGEMENT SYSTEM — DEMO DATABASE RESET")
    print("=" * 60)
    
    db_path = BASE_DIR / "db.sqlite3"
    migrations_dir = BASE_DIR / "bank" / "migrations"

    # 1. Remove database if exists
    if db_path.exists():
        print(f"Removing existing database file: {db_path}")
        try:
            os.remove(db_path)
            print("Successfully deleted database file.")
        except Exception as e:
            print(f"Could not delete database: {e}")
            print("Please stop any running local server before running this reset script.")
            sys.exit(1)
            
    # 2. Run migrations
    print("\nRunning Django Migrations...")
    run_cmd([sys.executable, "manage.py", "migrate"])

    # 3. Load fixtures
    fixture_path = BASE_DIR / "bank" / "fixtures" / "sample_data.json"
    if fixture_path.exists():
        print("\nLoading sample fixtures...")
        run_cmd([sys.executable, "manage.py", "loaddata", "bank/fixtures/sample_data.json"])
    else:
        print(f"\nWarning: Sample fixture file not found at: {fixture_path}")

    # 4. Display credentials
    print("\n" + "=" * 60)
    print("                DEMO ACCOUNTS & LOGIN INFO")
    print("=" * 60)
    print(" Access the public site at: http://127.0.0.1:8000/")
    print(" Access the Admin Panel at: http://127.0.0.1:8000/admin/")
    print("-" * 60)
    print(" Account Type  | Username     | Password      | Access Level")
    print("-" * 60)
    print(" Admin (Super) | demo_admin   | DemoPass123!  | Full /admin/ & Staff Pages")
    print(" Staff Panel   | demo_staff   | DemoPass123!  | Full /admin/ & Staff Pages")
    print(" Regular User  | demo_user    | DemoPass123!  | Public Requests & Booking")
    print("=" * 60)
    print("Database reset completed successfully! Run server using:")
    print("  python manage.py runserver")
    print("=" * 60)

if __name__ == "__main__":
    main()
