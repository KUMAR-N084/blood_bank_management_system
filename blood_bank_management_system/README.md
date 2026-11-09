# Blood Bank Management System (BBMS)

A comprehensive, premium Django-based **Blood Bank Management System** developed as a Software Engineering mini-project. This application facilitates complete management of blood stock, donor directories, patient requests, appointment bookings, and staff review operations.

---

## 🎨 Design & UX Enhancements

The project features a complete developer UI overhaul with the following modern design characteristics:
- **Color Palette**: Dark-charcoal navigation/menus paired with crimson-red accents, and soft greys for maximum readability.
- **Typography**: Clean, professional look powered by the **Inter** Google Font.
- **Micro-Animations**: Animated stat counters on the homepage dashboard, pulse effects on low-stock items, and subtle page/card hover lifts.
- **Responsive Layout**: Designed mobile-first using Bootstrap 5 grids; data tables wrap cleanly with horizontal scrolling on smaller screens.
- **Auto-Dismiss Alerts**: Message banners automatically slide out of view after 5 seconds to reduce screen clutter.
- **Client-Side Validation**: Instant validation of phone numbers, age ranges (18-100), email formats, and future-only dates.

---

## 🔑 Demo Accounts & Credentials

For local evaluation only, the demo fixture creates three sample accounts. Run the reset script (described below) to recreate them. These are public demo credentials, not secure production accounts; change or remove them before any deployment and never enter real donor or patient information into a public demo instance.

| Account Role | Username | Password | Email | Accessible Interfaces |
| :--- | :--- | :--- | :--- | :--- |
| **Super Admin** | `demo_admin` | `DemoPass123!` | `admin@bloodbank.demo` | Django Admin (`/admin/`), Staff Operations & Public Pages |
| **Staff Member** | `demo_staff` | `DemoPass123!` | `demo@example.com` | Django Admin (`/admin/`), Staff Operations & Public Pages |
| **Public User** | `demo_user` | `DemoPass123!` | `user@bloodbank.demo` | Blood Requests, Donor Applications, Booking Slots |

---

## 🚀 Quick Start & Installation

Follow these steps to set up and run the application locally:

### 1. Clone & Navigate to Project
Ensure python is installed on your local operating system. Open a command terminal and enter:
```bash
cd blood_bank_management_system/blood_bank_management_system
```

### 2. Create Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell/CMD):
.venv\Scripts\activate

# Or on macOS/Linux:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure local environment
Copy the example file and generate a fresh Django secret key:

```powershell
Copy-Item .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste the generated value into `.env` as `DJANGO_SECRET_KEY=...`. Keep `.env` private and never commit it. `DJANGO_DEBUG` defaults to `false`; enable it only for local development if needed.

### 4. Run One-Click Database Reset
Execute the database setup script to migrate schemas, populate fixtures, and initialize the demo accounts:
```bash
python reset_demo.py
```

### 5. Start the Server
```bash
python manage.py runserver
```

Once running, navigate to:
- **Public Website**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Superuser Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🛠️ One-Click Database Reset Tool

A helper script `reset_demo.py` is included in the project root. Running it will:
1. Remove any existing local `db.sqlite3` database to recreate a clean demo database. The generated database file is intentionally not tracked in Git.
2. Re-run all Django migration sequences.
3. Automatically load the expanded database fixtures (`sample_data.json`) including 6 donors, 8 stock blood groups, applications, and requests.
4. Output the credentials table directly to the console terminal window.

To reset the database at any time, run:
```bash
python reset_demo.py
```

---

## 📌 Project Architecture & Architecture Outline

The system is organized into a modular Django application structure under the `bank` app:

### 1. Data Models (`bank/models.py`)
- **`Donor`**: Represents verified active donors including age, phone, city, and date of last donation.
- **`BloodStock`**: Tracks unit levels of each of the 8 major blood groups (`A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`).
- **`BloodRequest`**: Patient request logs mapping contact info, blood requirements, hospital destinations, and approval status.
- **`DonorApplication`**: Pending applications submitted by prospective donors, awaiting staff verification.
- **`DonationAppointment`**: Booked slots at medical centers for donor appointments.
- **`ContactRequest`**: Inquiries from recipients requesting contact details of verified donors.
- **`AuditLog`**: Simple audit tracker recording history of actions performed by staff accounts.

### 2. Form Controllers (`bank/forms.py`)
Provides validation rules matching:
- **Name validation**: letters, dots, spaces, hyphens.
- **Phone validation**: digits, length between 7 and 15 characters.
- **Age validation**: min value 18, max value 100.
- **Slot validation**: checks that date and time belong to the future.

### 3. Core Logic Views (`bank/views.py`)
Implements authorization boundaries:
- Public functions for requesting blood, booking appointments, and applying to donate.
- Staff functions (checking `@request.user.is_staff`) for reviewing donor queues, updating stock values, managing requests, changing appointment statuses, and auditing logs.

---

## 🧭 URL Routing Index

| View URL Endpoint | Method | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Public | Homepage dashboard, stock levels, and counters. |
| `/donors/` | `GET` | Public / Staff | Search directory of donors by blood group, city, hospital. |
| `/donors/apply/` | `GET`, `POST` | Public | Public interface to apply as a donor. |
| `/appointments/book/`| `GET`, `POST` | Public | Submit slots for donation. |
| `/request/` | `GET`, `POST` | Public | Request urgent blood stocks. |
| `/accounts/login/` | `GET`, `POST` | Public | Public account login interface. |
| `/accounts/register/`| `GET`, `POST` | Public | Registration interface. |
| `/staff/login/` | `GET`, `POST` | Staff | Access staff control room. |
| `/applications/` | `GET` | Staff Only | Manage incoming donor applications. |
| `/appointments/` | `GET` | Staff Only | Manage appointment slots. |
| `/requests/` | `GET` | Staff Only | List requests, approve/reject. |
| `/stock/add/` | `GET`, `POST` | Staff Only | Manually top up stock quantities. |
| `/export/donors/` | `GET` | Staff Only | Export current donor registry as CSV. |
| `/admin/` | `GET`, `POST` | Superuser | Complete database CRUD console. |

---

## 📧 Email Alerts Setup

The system uses Django's console email backend for development. Any alerts (approving contact details, confirming appointment slots, or rejecting requests) print direct logs to the terminal where you launched `runserver`.

To wire up a real SMTP mail server, set these environment variables before booting the server:
```bash
# Windows
set EMAIL_USE_SMTP=1
set EMAIL_HOST=smtp.gmail.com
set EMAIL_PORT=587
set EMAIL_HOST_USER=example@gmail.com
set EMAIL_HOST_PASSWORD=your_password
```

---

## 🧪 Unit Testing

Run the Django automated unit tests using:
```bash
python manage.py test
```
The test suite validates request flows, permission boundaries, email outputs, and audit logs.


## Security and data handling

- The Django secret key is loaded from the local `.env` file; the repository does not contain a production secret.
- Debug mode is disabled by default. Configure `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` for the hostnames used by a deployment.
- The repository's SQLite database is generated locally by the reset script and is excluded from version control. The fixture contains synthetic demonstration records.
- Donor and patient records can contain sensitive personal information. Use only synthetic data for demos, restrict access to staff views, and apply appropriate privacy and security controls before real-world use.
- The demo usernames and passwords shown above are intentionally public for local evaluation only. Do not deploy the application with those credentials.
