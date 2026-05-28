# ☁️ Cloud Computing Lab: Automated AWS Infrastructure

## 📌 Project Overview
This project automatically provisions and configures a scalable web infrastructure on AWS. It uses **Terraform** for Infrastructure as Code (IaC) to build servers and **Ansible** to configure them.

### 🏗 Architecture
* **Cloud Provider:** AWS (Amazon Web Services)
* **Frontend:** 1 Nginx Web Server (Public Subnet)
* **Backend:** 3 Nginx Backend Servers (Private access logic)
* **Networking:** Custom VPC, Subnets, Internet Gateway, and Route Tables.

---

## 🛠 Technologies Used
* **Terraform:** For provisioning VPC, EC2, Security Groups, and Keys.
* **Terraform Modules:** Refactored subnet logic into `modules/subnet`.
* **Ansible:** For configuration management (installing Nginx, HTML pages).
* **Ansible Roles:** Modular roles for `frontend` and `backend` configuration.

---

## 📂 Project Structure
```bash
.
├── ansible/               # Ansible Configuration
│   ├── roles/             # Roles for Frontend & Backend
│   └── inventory.tftpl    # Dynamic Inventory Template
├── modules/               # Terraform Modules
│   └── subnet/            # Reusable Subnet Module
├── screenshots/           # Documentation Images
├── main.tf                # Main Infrastructure Logic
├── locals.tf              # Common Tags & Variables
└── variables.tf           # Input Variables
```

---

## 🚀 How to Run

### 1. Prerequisites
* AWS CLI configured with credentials.
* Terraform installed.
* Ansible installed.

### 2. Deploy Infrastructure
```bash
terraform init
terraform apply -auto-approve
```

### 3. Verify Deployment
After the apply is complete, Terraform will output the **Frontend URL**.
* Copy the `frontend_url` from the output.
* Paste it into your browser to see the "Welcome to Frontend" page.

### 4. Clean Up (Destroy)
To delete all resources and stop billing:
```bash
terraform destroy -auto-approve
```

---

## 📸 Screenshots
Check the `screenshots/` folder for deployment evidence and output logs.
