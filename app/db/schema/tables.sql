IF OBJECT_ID('departments', 'U') IS NULL
CREATE TABLE departments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    is_production BIT NOT NULL DEFAULT 0
);

IF OBJECT_ID('employees', 'U') IS NULL
CREATE TABLE employees (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    personnel_number NVARCHAR(100) UNIQUE NOT NULL,
    department NVARCHAR(100) NOT NULL,
    category NVARCHAR(100) NOT NULL,
    CONSTRAINT check_employee_category
        CHECK (category IN (N'worker', N'specialist', N'manager'))
);

IF OBJECT_ID('orders', 'U') IS NULL
CREATE TABLE orders (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(450) NOT NULL,
    number NVARCHAR(255) UNIQUE NOT NULL
);

IF OBJECT_ID('works', 'U') IS NULL
CREATE TABLE works (
    id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT NOT NULL,
    name NVARCHAR(450) NOT NULL,
    planned_hours DECIMAL(10,2) NOT NULL,
    spent_hours DECIMAL(10,2) NOT NULL DEFAULT 0,
    remaining_hours AS (planned_hours - spent_hours),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

IF OBJECT_ID('hours', 'U') IS NULL
CREATE TABLE hours (
    id INT IDENTITY(1,1) PRIMARY KEY,
    order_name NVARCHAR(450) NOT NULL,
    order_number NVARCHAR(255) UNIQUE NOT NULL,
    work_name NVARCHAR(450) NOT NULL,
    spent_hours DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_date DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    created_time TIME(0) NOT NULL DEFAULT CAST(GETDATE() AS TIME)
);

IF OBJECT_ID('tasks', 'U') IS NULL
CREATE TABLE tasks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    employee_name NVARCHAR(255) NOT NULL,
    personnel_number NVARCHAR(100) NOT NULL,
    department NVARCHAR(100) NOT NULL,
    work_name NVARCHAR(450) NOT NULL,
    hours DECIMAL(10,2) NOT NULL DEFAULT 0,
    order_number NVARCHAR(255) NOT NULL,
    order_name NVARCHAR(450) NOT NULL,
    operation_date DATE NOT NULL DEFAULT GETDATE(),
    employee_category NVARCHAR(100) NOT NULL
);

IF OBJECT_ID('users', 'U') IS NULL
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    department NVARCHAR(100) NOT NULL,
    login NVARCHAR(100) UNIQUE NOT NULL,
    password_hash NVARCHAR(255),
    permissions_level NVARCHAR(100) NOT NULL DEFAULT 'standard',
    is_account_enabled BIT NOT NULL DEFAULT 0,
    is_factory_worker BIT NOT NULL DEFAULT 0,
    CONSTRAINT check_permissions_level
        CHECK (permissions_level IN ('minimal', 'standard', 'advanced')),
    is_admin BIT NOT NULL DEFAULT 0;
);

IF OBJECT_ID('logs', 'U') IS NULL
CREATE TABLE logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    action NVARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    entity_type NVARCHAR(50) NOT NULL,
    user_name NVARCHAR(100) NOT NULL,
    ip_address NVARCHAR(50) NOT NULL,
    platform NVARCHAR(50) NOT NULL,
    os_version NVARCHAR(50) NOT NULL,
    browser NVARCHAR(50) NOT NULL,
    browser_version NVARCHAR(50) NOT NULL,
    created_date DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    created_time TIME(0) NOT NULL DEFAULT CAST(GETDATE() AS TIME)
);
