CREATE DATABASE IF NOT EXISTS vmas_dev;
USE vmas_dev;

CREATE TABLE IF NOT EXISTS visitors (
    visitor_id VARCHAR(20) PRIMARY KEY,
    visitor_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS department_staff (
    staff_id VARCHAR(20) PRIMARY KEY,
    staff_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS security_guards (
    security_id VARCHAR(20) PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);
