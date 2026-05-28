# Architecture Design – Assignment 2

## 1. Architecture Overview

This project implements a multi-tier web infrastructure on AWS using Terraform. 
The architecture is designed to provide scalability, high availability, security, 
and performance using a reverse proxy and multiple backend servers.

The system follows a load-balanced architecture where incoming user requests are 
handled by an Nginx server and forwarded to backend Apache web servers.

---

## 2. Architecture Diagram

┌─────────────────────────────────────────────────┐
│ Internet │
└─────────────────┬───────────────────────────────┘
│
│ HTTP (80) / HTTPS (443)
▼
┌────────────────────┐
│ Nginx Server │
│ (Load Balancer) │
│ - Reverse Proxy │
│ - Caching │
│ - SSL/TLS │
└────────┬───────────┘
│
┌───────────┼───────────┐
│ │ │
▼ ▼ ▼
┌─────┐ ┌─────┐ ┌─────┐
│Web-1│ │Web-2│ │Web-3│
│ │ │ │ │(BKP)│
└─────┘ └─────┘ └─────┘
Primary Primary Backup

---

## 3. Component Description

### Nginx Server
- Acts as a reverse proxy and load balancer
- Distributes traffic between backend servers
- Implements caching for improved performance
- Handles client-facing HTTP/HTTPS traffic

### Backend Web Servers
- Apache HTTP Server installed
- Serve static and dynamic content
- Web-1 and Web-2 act as primary servers
- Web-3 acts as a backup server

### Networking Components
- Custom VPC
- Public subnet
- Internet Gateway
- Route tables

### Security Groups
- Nginx security group allows HTTP/HTTPS from the internet
- Backend security group allows traffic only from Nginx
- SSH access restricted using key pairs

---

## 4. Network Topology

All EC2 instances are deployed within a public subnet of a custom VPC. 
The Nginx server is the only instance directly exposed to the internet. 
Backend servers are isolated and receive traffic only from the Nginx server.

---

## 5. Load Balancing Strategy

Nginx uses a round-robin load balancing strategy to distribute requests evenly 
between backend servers. The backup server ensures high availability in case 
primary servers fail.

---

## 6. High Availability Design

- Multiple backend servers
- Backup server for failover
- Stateless backend design
- Infrastructure reproducibility using Terraform
