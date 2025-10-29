CREATE DATABASE InventarioComidaDB;
GO

USE InventarioComidaDB;
GO

-- Tabla de Productos (versión simplificada)
CREATE TABLE Productos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo_barras NVARCHAR(50) UNIQUE,
    nombre NVARCHAR(100) NOT NULL,
    descripcion NVARCHAR(255),
    categoria NVARCHAR(50),  -- Ahora es un campo de texto en lugar de una clave foránea
    proveedor NVARCHAR(100), -- Ahora es un campo de texto en lugar de una clave foránea
    precio_compra DECIMAL(10, 2) NOT NULL,
    precio_venta DECIMAL(10, 2) NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    stock_minimo INT DEFAULT 10,
    fecha_vencimiento DATE,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    activo BIT DEFAULT 1
);

-- Insertar algunos productos de ejemplo
INSERT INTO Productos (codigo_barras, nombre, descripcion, categoria, proveedor, precio_compra, precio_venta, stock_actual, stock_minimo, fecha_vencimiento)
VALUES 
('7501001234567', 'Leche Entera 1L', 'Leche entera pasteurizada', 'Lácteos', 'Lácteos La Vaquita', 15.50, 25.00, 50, 10, '2023-12-31'),
('7501012345678', 'Huevo Blanco 1kg', 'Huevo blanco grado AA', 'Huevos', 'Avícola San Juan', 45.00, 65.00, 30, 5, '2023-11-15'),
('7501023456789', 'Arroz 1kg', 'Arroz blanco grano largo', 'Granos', 'Distribuidora de Granos', 25.00, 35.00, 100, 20, '2024-06-30'),
('7501034567890', 'Frijol Negro 1kg', 'Frijol negro mayocoba', 'Legumbres', 'Distribuidora de Granos', 30.00, 45.00, 75, 15, '2024-05-31'),
('7501045678901', 'Manzana Roja', 'Manzana roja deliciosa', 'Frutas', 'Frutas y Verduras Frescas', 25.00, 40.00, 60, 10, '2023-11-30');
GO
