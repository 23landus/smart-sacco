Smart-SACCO Management System
Streamlining Financial Workflows for Savings Groups

Project Objective
The goal of this project is to replace manual Excel-based record-keeping with an automated, transparent, and secure backend system. It specifically handles member shares, loan distributions, and interest calculations to ensure financial accuracy for SACCO groups.

 Key Features
* Member Management:** Custom user models to track member profiles and contact details.
* Automated Ledger:** Real-time tracking of savings, deposits, and withdrawals.
* Loan Logic:** Built-in interest rate calculators and repayment scheduling.
* Role-Based Access:** Different dashboards for Admin, Treasurers, and Members.
* Audit Trail:** Every transaction is logged to prevent manual errors or fraud.

Technical Stack

*Backend:** Python 3.10 + Django 5.x
* Database:** SQLite (Development/Testing) | PostgreSQL (Production)
* Deployment:** Hosted on Render with GitHub CI/CD integration.
*Styling:** Tailwind CSS for a modern, responsive interface.

Current Progress
- [x] Initial System Architecture & Database Design
- [x] Custom User Authentication (Register/Login)
- [x] Core Ledger & Transaction Models
- [ ] Automated Interest Disbursement (In Progress)
- [ ] Financial Reporting & PDF Export (Upcoming)

Local Setup Instructions
To run this project locally for testing:
1. Clone the repository: `git clone [Your-Repo-Link]`
2. Create a virtual environment: `python -m venv venv`
3. Activate venv: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Start the server: `python manage.py runserver`

---
Developer: Landus
Login: 256784177493
Password: %Baldev256
