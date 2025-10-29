# API de Gestión de Comidas

API REST contenerizada con FastAPI que gestiona comidas,para obtener recetas aleatorias y las almacena en SQL Server.


### 1. Clonar/Descargar el proyecto
```bash
cd meals-api-docker
```

### 2. Estructura de archivos
```
TAREA/
├── API/
│   ├── .env
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── db/
│   └── init.sql
├── docker-compose.yml
└── README.md
```

### 3. Levantar los contenedores
```bash
docker-compose up --build
```

## Uso de la API

### Endpoints disponibles


 GET    | `/`                   | Interfaz web del dashboard           
 GET    | `/meals`              | Lista todas las comidas              
 GET    | `/meals/{id}`         | Obtiene una comida por ID            
 GET    | `/meals/random/api`   | Obtiene comida aleatoria de TheMealDB
 POST   | `/meals`              | Crea una nueva comida                
 PUT    | `/meals/{id}`         | Actualiza una comida                 
 DELETE | `/meals/{id}`         | Elimina una comida                   
 DELETE | `/meals`              | Elimina todas las comidas            



**Desde el navegador:**
- Dashboard principal: http://localhost:8000/
- Documentación interactiva: http://localhost:8000/docs

### Respuestas de ejemplo

**GET /meals**
```json
{
  "total": 10,
  "meals": [
    {
      "id": 1,
      "name": "Pancakes",
      "categoria": "Breakfast",
      "area": "American",
      "image_url": "https://www.themealdb.com/images/..."
    }
  ]
}
```

**GET /meals/random/api**
```json
{
  "mensaje": "Comida guardada exitosamente",
  "meal": {
    "id": 11,
    "name": "Teriyaki Chicken",
    "categoria": "Chicken",
    "area": "Japanese",
    "image_url": "https://www.themealdb.com/images/..."
  }
}
```

## Base de Datos

### Acceder a SQL Server directamente
```bash
docker exec -it sqlserver_meals /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "YourStrong@Passw0rd" -C \
  -Q "SELECT * FROM MealsDB.dbo.Meals"
```

### Estructura de la tabla
```sql
CREATE TABLE Meals (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100),
    categoria NVARCHAR(100),
    area NVARCHAR(100),
    image_url NVARCHAR(255)
);
```

## Detener la aplicación
```bash
# Detener sin eliminar datos
docker-compose down

# Detener y eliminar volúmenes (borra datos)
docker-compose down -v
```

## Variables de entorno (api/.env)
```properties
DB_SERVER=sqlserver
DB_NAME=MealsDB
DB_USER=sa
DB_PASSWORD=YourStrong@Passw0rd
DB_PORT=1433
DB_DRIVER=ODBC Driver 18 for SQL Server
```



###  No se puede conectar a SQL Server
```bash
docker logs sqlserver_meals
docker logs fastapi_meals
```

### Reiniciar desde cero
```bash
docker-compose down -v
docker-compose up --build
```
## Inicio Rápido

```bash
# 1. Clonar proyecto
cd meals-api-docker

# 2. Levantar contenedores
docker-compose up --build

# 3. Probar
# Abrir http://localhost:8000/ en el navegador
```