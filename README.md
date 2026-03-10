# 💄 BeautyVibe Backend API

A scalable **Django REST Framework based backend** for a beauty e-commerce and creator marketplace platform where users can discover beauty products through videos and creators can earn commission from product recommendations.

This system includes **Stripe payments, creator commissions, product discovery via videos, and a creator withdrawal system.**

---

# 🚀 Features

## 👤 User System

* User registration and authentication
* JWT authentication
* Social login (Google / Apple)
* Profile management
* Skin analysis profile

---

## 🛍 Product System

* Product categories
* Product search and filtering
* Product ratings
* Save products feature

---

## 🎬 Creator Video Platform

Creators can upload videos featuring beauty products.

Features:

* Upload product related videos
* Tag products inside videos
* Track views and engagement
* Earn commission from product sales

---

## 💳 Payment System

Integrated with **Stripe**.

Supported payments:

* Stripe Card Payments
* Apple Pay
* Google Pay

Secure checkout with Stripe.

---

## 💰 Commission System

Creators earn commission from product sales.

Includes:

* Commission tracking
* Creator earnings dashboard
* Sales analytics

---

## 🏦 Creator Withdraw System

Creators can withdraw earnings.

Features:

* Stripe Connect integration
* Withdraw request system
* Admin approval
* Bank payout tracking
* Withdraw history

---

## 📊 Creator Dashboard

Shows:

* Total Views
* Total Sales
* Commission Earned
* Total Videos Uploaded
* Video Performance

---

# 🛠 Tech Stack

| Technology            | Usage            |
| --------------------- | ---------------- |
| Python                | Backend Language |
| Django                | Web Framework    |
| Django REST Framework | API Development  |
| PostgreSQL / SQLite   | Database         |
| Stripe                | Payment Gateway  |
| JWT                   | Authentication   |
| Cloud Storage         | Media storage    |

---

# 📂 Project Structure

```
BeautyVibe/
│
├── accounts/        # Authentication system
├── products/        # Product management
├── videos/          # Creator video system
├── orders/          # Order management
├── payments/        # Stripe payment integration
├── commissions/     # Creator commission tracking
├── withdrawals/     # Creator withdraw system
│
├── media/           # Uploaded media files
├── manage.py
└── requirements.txt
```

---

# ⚙ Installation Guide

## 1️⃣ Clone Repository

```bash
git clone https://github.com/imhnoyon/BeautyVibe.git
cd BeautyVibe
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

### Windows

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Environment Variables

Create a `.env` file:

```
SECRET_KEY=your_secret_key
DEBUG=True

STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_publishable_key
```

---

## 5️⃣ Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 6️⃣ Run Development Server

```bash
python manage.py runserver
```

Server will run at:

```
http://127.0.0.1:8000/
```

---

## 📦 Postman Collection

You can test all APIs using the Postman collection.

⬇️ **Download Postman Collection**

[Download BeautyVibe Postman Collection](./BeautyVibe.postman_collection.json)

After downloading, import the file into Postman.

Steps:

1. Open Postman
2. Click **Import**
3. Select the downloaded JSON file
4. All API endpoints will be added automatically


# 🔐 Security

This backend uses:

* JWT authentication
* Role based permission system
* Secure Stripe payment flow
* Environment based secrets

---

# 🔮 Future Improvements

* AI product recommendations
* Smart video feed algorithm
* Creator analytics dashboard
* Live shopping features
* Recommendation engine

---

# 👨‍💻 Author

**Mahedi Hasan Noyon**

Backend Developer (Django & API Development)

GitHub
https://github.com/imhnoyon

---

# 📜 License

This project is licensed under the **MIT License**.
