CREATE DATABASE MealsDB;
GO

USE MealsDB;
GO

CREATE TABLE Meals (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100),
    categoria NVARCHAR(100),
    area NVARCHAR(100),
    image_url NVARCHAR(255)
);
GO

-- Insertar datos de ejemplo
INSERT INTO Meals (name, categoria, area, image_url) VALUES 
('Pancakes', 'Breakfast', 'American', 'https://www.themealdb.com/images/media/meals/rwuyqx1511383174.jpg'),
('Spaghetti Carbonara', 'Pasta', 'Italian', 'https://www.themealdb.com/images/media/meals/llcbn01574260722.jpg'),
('Chicken Tikka Masala', 'Chicken', 'Indian', 'https://www.themealdb.com/images/media/meals/wyxwsp1486979827.jpg'),
('Beef Wellington', 'Beef', 'British', 'https://www.themealdb.com/images/media/meals/vvpprx1487325699.jpg'),
('Pad Thai', 'Seafood', 'Thai', 'https://www.themealdb.com/images/media/meals/wvtzxv1511475309.jpg'),
('Tacos', 'Beef', 'Mexican', 'https://www.themealdb.com/images/media/meals/tkxquw1628771028.jpg'),
('Sushi Rolls', 'Seafood', 'Japanese', 'https://www.themealdb.com/images/media/meals/g046bb1663960946.jpg'),
('Greek Salad', 'Vegetarian', 'Greek', 'https://www.themealdb.com/images/media/meals/k29viq1585565980.jpg'),
('Croissant', 'Dessert', 'French', 'https://www.themealdb.com/images/media/meals/4i5cnx1587672171.jpg'),
('Fish and Chips', 'Seafood', 'British', 'https://www.themealdb.com/images/media/meals/uvuyxu1503067369.jpg');
GO

PRINT 'MealsDB initialized successfully!';
GO