BLOOD BANK MANAGEMENT SYSTEM (BBMS) - MCA MINI PROJECT

Steps to Run:

1. Open Command Prompt / Terminal in this project folder.

2. Install dependencies:
   pip install -r requirements.txt

3. Initialize and Reset database (One-click):
   python reset_demo.py

4. Run local server:
   python manage.py runserver

5. Open web browser:
   - Public Site: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

Demo Accounts (All passwords are DemoPass123!):
- Super Admin: demo_admin (Full access to /admin/ and staff views)
- Staff Member: demo_staff (Full access to /admin/ and staff views)
- Public User: demo_user (Access to donor request forms, appointment booking)

Please see the comprehensive README.md file in this directory for:
- Detailed system architecture explanation
- Data models structure and fields listing
- Full list of URL routing endpoints
- Form and input validation details
- Unit testing instructions
- Email alerts configuration
