# 🛒 Sistema de Gestión de Inventario de Alimentos

[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQL Server](https://img.shields.io/badge/Microsoft%20SQL%20Server-CC2927?style=for-the-badge&logo=microsoft%20sql%20server&logoColor=white)](https://www.microsoft.com/sql-server/)

Sistema completo de gestión de inventario para tiendas de alimentos, construido con FastAPI, SQL Server y Docker.

##  Características

- **Gestión de Productos**: CRUD completo para productos alimenticios
- **Búsqueda y Filtrado**: Por categoría, proveedor y estado
- **Control de Inventario**: Seguimiento de stock actual y mínimo
- **Fechas de Vencimiento**: Alertas de productos por vencer
- **Interfaz Web**: Interfaz amigable y responsiva
- **API RESTful**: Documentación interactiva con Swagger UI

##  Requisitos Previos

- Docker Desktop (Windows/Mac) o Docker Engine (Linux)
- Docker Compose
- Puerto 8000 y 1434 disponibles

##  Instalación

1. Clona el repositorio:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd catfacts-api-docker
   ```

2. Configura las variables de entorno (opcional):
   - Copia `.env.example` a `.env` y ajusta los valores si es necesario

3. Inicia los servicios con Docker Compose:
   ```bash
   docker-compose up -d --build
   ```

4. Espera a que todos los contenedores estén en ejecución:
   ```bash
   docker ps
   ```

##  Acceso

- **Interfaz Web**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Base de Datos**:
  - Servidor: `localhost,1434`
  - Usuario: `sa`
  - Contraseña: `StrongPassword123!`
  - Base de datos: `InventarioComidaDB`

##  Endpoints de la API

### Productos

- `GET /api/productos/` - Listar todos los productos
- `GET /api/productos/{id}` - Obtener un producto por ID
- `POST /api/productos/` - Crear un nuevo producto
- `PUT /api/productos/{id}` - Actualizar un producto
- `DELETE /api/productos/{id}` - Eliminar un producto (lógico)

### Filtros disponibles

- `?activo=true/false` - Filtrar por estado activo/inactivo
- `?categoria=nombre` - Filtrar por categoría

##  Estructura del Proyecto
```
.
├── api/                  # Código fuente de la API
│   ├── app.py           # Aplicación FastAPI principal
│   ├── requirements.txt  # Dependencias de Python
│   └── .env.example     # Variables de entorno de ejemplo
├── db/
│   └── init.sql         # Script de inicialización de la base de datos
├── docker-compose.yml   # Configuración de Docker Compose
└── README.md            # Este archivo
```

##  Comandos Útiles
- **Iniciar servicios**: `docker-compose up -d`
- **Detener servicios**: `docker-compose down`
- **Ver logs**: `docker-compose logs -f`
- **Reconstruir y reiniciar**: `docker-compose up -d --build`

##  Notas de Desarrollo

- La base de datos SQL Server se inicializa con datos de ejemplo
- Los productos eliminados se marcan como inactivos (soft delete)
- La interfaz web incluye validación en tiempo real

##  Solución de Problemas

### Error: Puerto 8000 en uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux
lsof -ti:8000 | xargs kill -9
```

### Error: No se puede conectar a SQL Server
```bash
docker logs sqlserver_container
docker logs api_container
```

### Reiniciar desde cero
```bash
docker-compose down -v
docker-compose up --build
```

## Licencia

Este proyecto está bajo la Licencia MIT.



