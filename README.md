# 📦 ICT Inventory Management System API

This API is designed to manage assets, software, consumables, and user roles within an ICT inventory system. It uses **Flask**, **PostgreSQL** as the database, and **Redis** for authentication and caching.

## 🏗️ Tech Stack
- **Backend:** Flask (Python)
- **Database:** PostgreSQL
- **Authentication & Caching:** Redis
- **Deployment:** Flask-RESTful, Flask-JWT-Extended

## 📌 Authentication
- The system uses **JWT tokens** stored in Redis for authentication.
- Users must **log in** to receive an access token, which must be included in requests.

---
## 📜 API Endpoints

### **🔐 Authentication Routes**
| Method  | Route               | Description |
|---------|--------------------|-------------|
| `POST`  | `/auth/register`   | Register a new user |
| `POST`  | `/auth/login`      | Authenticate user & return JWT |
| `POST`  | `/auth/logout`     | Invalidate JWT token |
| `POST`  | `/auth/refresh`    | Refresh access token |
| `PUT`   | `/auth/update/<user_id>` | Update user details |

### **👤 User Routes**
| Method  | Route               | Description |
|---------|--------------------|-------------|
| `GET`   | `/user/<int:user_id>` | Retrieve user details |

### **🏢 Department Routes**
| Method  | Route                               | Description |
|---------|------------------------------------|-------------|
| `POST`  | `/register/department`            | Create a new department |
| `GET`   | `/departments`                    | Get all departments |
| `GET`   | `/department/<department_id>`     | Retrieve a department by ID |
| `PUT`   | `/department/<int:department_id>` | Update a department |
| `DELETE`| `/department/<department_id>`     | Delete a department |

### **🔑 Role Routes**
| Method  | Route                         | Description |
|---------|------------------------------|-------------|
| `POST`  | `/register/role`             | Create a new role |
| `GET`   | `/roles`                     | Retrieve all roles |
| `GET`   | `/role/<int:role_id>`        | Retrieve a role by ID |
| `PUT`   | `/role/<int:role_id>`        | Update a role |
| `DELETE`| `/role/<int:role_id>`        | Delete a role |

### **🖥️ Asset Routes**
| Method  | Route                         | Description |
|---------|------------------------------|-------------|
| `POST`  | `/register/asset`            | Add a new asset |
| `GET`   | `/assets`                     | Retrieve all assets |
| `GET`   | `/assets/search`              | Search for assets |
| `DELETE`| `/delete/assets`              | Delete multiple assets |

### **📄 Software Routes**
| Method  | Route                          | Description |
|---------|-------------------------------|-------------|
| `POST`  | `/register/software`          | Register new software |
| `GET`   | `/softwares`                   | Retrieve all software |
| `GET`   | `/software/search`             | Search software |
| `GET`   | `/software/license-status`     | Get license status of software |
| `POST`  | `/software/bulk-register`      | Bulk register software |
| `GET`   | `/software/expiry`             | Get expiring software |
| `GET`   | `/software/report`             | Generate software report |
| `DELETE`| `/software/<int:software_id>`  | Delete software |

---
## 🔥 Running the Application
### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/bonii254/ICT-INVENTORY-SYSTEM.git
```

### **2️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **3️⃣ Set Environment Variables**
```sh
set FLASK_APP=app.py  # Windows
$envPYTHONPATH="." # Windows
export FLASK_APP=app.py  # Mac/Linux

```

### **4️⃣ Run the Application**
```sh
flask run
```

### **5️⃣ Test the API**
After successful installation and setup, you can test the API using **Postman** or **cURL**.

#### Example: Register a new user
```sh
curl -X POST "http://127.0.0.1:5000/auth/register" -H "Content-Type: application/json" -d '{"email": "testuser@gmail.com", "password": "testpass", "fullname", "test user",
"department_id": 1, "role_id":1}'
```

#### Example: Login
```sh
curl -X POST "http://127.0.0.1:5000/auth/login" -H "Content-Type: application/json" -d '{"email": "testuser@gmail.com", "password": "testpass"}'
```

---
## 🛠️ Contribution & Support
- Pull requests are welcome.
- Report issues in the GitHub repository.

## 👨‍💻 Author
**Boniface Murangiri**

## 📜 License
This project is **unlicensed**, meaning you are free to use, modify, and distribute the code without restrictions. However, the author holds no liability for any consequences of using this software.
