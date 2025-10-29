from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import pyodbc
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
app = FastAPI(title="🍽️ Meals API")

# Conexión a SQL Server
conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    f"TrustServerCertificate=yes;"
)

THEMEALDB_URL = "https://www.themealdb.com/api/json/v1/1/random.php"

# Modelos
class MealCreate(BaseModel):
    name: str
    categoria: str
    area: str
    image_url: str

class MealUpdate(BaseModel):
    name: Optional[str] = None
    categoria: Optional[str] = None
    area: Optional[str] = None
    image_url: Optional[str] = None

# ==================== INTERFAZ WEB ====================

@app.get("/", response_class=HTMLResponse)
def home():
    """Interfaz web profesional"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Meals Manager - Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                background: #0f172a;
                color: #e2e8f0;
                min-height: 100vh;
            }
            
            .navbar {
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                padding: 1.5rem 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                border-bottom: 1px solid #334155;
            }
            
            .navbar-content {
                max-width: 1400px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 1.5rem;
                font-weight: 700;
                color: #fff;
            }
            
            .logo-icon {
                font-size: 2rem;
            }
            
            .nav-links {
                display: flex;
                gap: 1rem;
            }
            
            .nav-link {
                color: #94a3b8;
                text-decoration: none;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.3s;
                font-weight: 500;
            }
            
            .nav-link:hover {
                background: #334155;
                color: #fff;
            }
            
            .container {
                max-width: 1400px;
                margin: 2rem auto;
                padding: 0 2rem;
            }
            
            .header {
                margin-bottom: 2rem;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
                color: #fff;
            }
            
            .header p {
                color: #94a3b8;
                font-size: 1.1rem;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .stat-card {
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #334155;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            }
            
            .stat-label {
                color: #94a3b8;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.5rem;
            }
            
            .stat-value {
                font-size: 2.5rem;
                font-weight: 700;
                color: #fff;
            }
            
            .actions-bar {
                display: flex;
                gap: 1rem;
                margin-bottom: 2rem;
                flex-wrap: wrap;
            }
            
            .btn {
                padding: 0.875rem 1.5rem;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                color: white;
            }
            
            .btn-success {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
            }
            
            .btn-warning {
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                color: white;
            }
            
            .btn-danger {
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                color: white;
            }
            
            .meals-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: 1.5rem;
                margin-top: 2rem;
            }
            
            .meal-card {
                background: #1e293b;
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid #334155;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                transition: all 0.3s;
            }
            
            .meal-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
                border-color: #3b82f6;
            }
            
            .meal-image {
                width: 100%;
                height: 220px;
                object-fit: cover;
                background: #334155;
            }
            
            .meal-content {
                padding: 1.5rem;
            }
            
            .meal-header {
                display: flex;
                justify-content: space-between;
                align-items: start;
                margin-bottom: 1rem;
            }
            
            .meal-id {
                background: #3b82f6;
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 700;
            }
            
            .meal-name {
                font-size: 1.25rem;
                font-weight: 700;
                color: #fff;
                margin-bottom: 1rem;
                line-height: 1.4;
            }
            
            .meal-tags {
                display: flex;
                gap: 0.5rem;
                margin-bottom: 1rem;
                flex-wrap: wrap;
            }
            
            .meal-tag {
                background: #334155;
                padding: 0.375rem 0.75rem;
                border-radius: 6px;
                font-size: 0.875rem;
                color: #cbd5e1;
                font-weight: 500;
            }
            
            .meal-actions {
                display: flex;
                gap: 0.5rem;
                padding-top: 1rem;
                border-top: 1px solid #334155;
            }
            
            .btn-small {
                padding: 0.5rem 1rem;
                font-size: 0.875rem;
                flex: 1;
            }
            
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                z-index: 1000;
                backdrop-filter: blur(4px);
            }
            
            .modal.active {
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .modal-content {
                background: #1e293b;
                border-radius: 16px;
                padding: 2rem;
                max-width: 600px;
                width: 90%;
                max-height: 90vh;
                overflow-y: auto;
                border: 1px solid #334155;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
            }
            
            .modal-header {
                margin-bottom: 1.5rem;
            }
            
            .modal-header h2 {
                font-size: 1.75rem;
                color: #fff;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
            }
            
            .form-label {
                display: block;
                margin-bottom: 0.5rem;
                color: #cbd5e1;
                font-weight: 600;
                font-size: 0.875rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .form-input {
                width: 100%;
                padding: 0.875rem;
                border: 2px solid #334155;
                border-radius: 8px;
                font-size: 1rem;
                background: #0f172a;
                color: #fff;
                transition: all 0.3s;
            }
            
            .form-input:focus {
                outline: none;
                border-color: #3b82f6;
                background: #1e293b;
            }
            
            .alert {
                padding: 1rem 1.5rem;
                border-radius: 8px;
                margin-bottom: 1.5rem;
                display: none;
                font-weight: 500;
                animation: slideDown 0.3s;
            }
            
            .alert.active {
                display: block;
            }
            
            .alert-success {
                background: #10b981;
                color: white;
            }
            
            .alert-error {
                background: #ef4444;
                color: white;
            }
            
            .loading {
                text-align: center;
                padding: 3rem;
                color: #94a3b8;
                font-size: 1.1rem;
            }
            
            .empty-state {
                text-align: center;
                padding: 4rem 2rem;
                color: #64748b;
            }
            
            .empty-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @media (max-width: 768px) {
                .navbar-content {
                    flex-direction: column;
                    gap: 1rem;
                }
                
                .header h1 {
                    font-size: 2rem;
                }
                
                .meals-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-content">
                <div class="logo">
                    <span class="logo-icon">🍽️</span>
                    <span>Meals Manager</span>
                </div>
                <div class="nav-links">
                    <a href="/" class="nav-link">Dashboard</a>
                    <a href="/docs" class="nav-link">API Docs</a>
                </div>
            </div>
        </nav>
        
        <div class="container">
            <div class="header">
                <h1>Dashboard de Comidas</h1>
                <p>Gestiona tu colección de recetas internacionales</p>
            </div>
            
            <div id="alert" class="alert"></div>
            
            <div class="stats-grid" id="stats"></div>
            
            <div class="actions-bar">
                <button class="btn btn-primary" onclick="loadMeals()">
                    📋 Cargar Todas
                </button>
                <button class="btn btn-success" onclick="getRandomMeal()">
                    🎲 Comida Aleatoria
                </button>
                <button class="btn btn-warning" onclick="openModal('create')">
                    ➕ Agregar Nueva
                </button>
                <button class="btn btn-danger" onclick="confirmDeleteAll()">
                    🗑️ Eliminar Todas
                </button>
            </div>
            
            <div id="mealsList" class="meals-grid"></div>
        </div>
        
        <!-- Modal Crear -->
        <div id="createModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>➕ Agregar Nueva Comida</h2>
                </div>
                <form id="createForm">
                    <div class="form-group">
                        <label class="form-label">Nombre</label>
                        <input type="text" id="create_name" class="form-input" placeholder="Ej: Spaghetti Carbonara" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Categoría</label>
                        <input type="text" id="create_categoria" class="form-input" placeholder="Ej: Pasta" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">País/Área</label>
                        <input type="text" id="create_area" class="form-input" placeholder="Ej: Italian" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">URL de la Imagen</label>
                        <input type="url" id="create_image" class="form-input" placeholder="https://..." required>
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <button type="submit" class="btn btn-success" style="flex: 1;">💾 Guardar</button>
                        <button type="button" class="btn btn-danger" onclick="closeModal('create')" style="flex: 1;">❌ Cancelar</button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Modal Editar -->
        <div id="editModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>✏️ Editar Comida #<span id="edit_id"></span></h2>
                </div>
                <form id="editForm">
                    <div class="form-group">
                        <label class="form-label">Nombre</label>
                        <input type="text" id="edit_name" class="form-input">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Categoría</label>
                        <input type="text" id="edit_categoria" class="form-input">
                    </div>
                    <div class="form-group">
                        <label class="form-label">País/Área</label>
                        <input type="text" id="edit_area" class="form-input">
                    </div>
                    <div class="form-group">
                        <label class="form-label">URL de la Imagen</label>
                        <input type="url" id="edit_image" class="form-input">
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <button type="submit" class="btn btn-success" style="flex: 1;">✅ Actualizar</button>
                        <button type="button" class="btn btn-danger" onclick="closeModal('edit')" style="flex: 1;">❌ Cancelar</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            let currentEditId = null;
            
            window.onload = () => loadMeals();
            
            function showAlert(message, type) {
                const alert = document.getElementById('alert');
                alert.textContent = message;
                alert.className = \`alert alert-\${type} active\`;
                setTimeout(() => alert.className = 'alert', 5000);
            }
            
            function updateStats(total) {
                const stats = document.getElementById('stats');
                stats.innerHTML = \`
                    <div class="stat-card">
                        <div class="stat-label">Total Comidas</div>
                        <div class="stat-value">\${total}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Estado</div>
                        <div class="stat-value" style="font-size: 1.5rem;">✅ Activo</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Base de Datos</div>
                        <div class="stat-value" style="font-size: 1.5rem;">🗄️ SQL Server</div>
                    </div>
                \`;
            }
            
            async function loadMeals() {
                const list = document.getElementById('mealsList');
                list.innerHTML = '<div class="loading">🍳 Cargando comidas...</div>';
                
                try {
                    const response = await fetch('/meals');
                    const data = await response.json();
                    
                    updateStats(data.total);
                    
                    if (data.meals.length === 0) {
                        list.innerHTML = \`
                            <div class="empty-state" style="grid-column: 1 / -1;">
                                <div class="empty-icon">🍽️</div>
                                <h3 style="margin-bottom: 0.5rem; color: #94a3b8;">No hay comidas registradas</h3>
                                <p>Comienza agregando una comida o obtén una aleatoria</p>
                            </div>
                        \`;
                        return;
                    }
                    
                    list.innerHTML = data.meals.map(meal => \`
                        <div class="meal-card">
                            <img src="\${meal.image_url}" alt="\${meal.name}" class="meal-image" 
                                 onerror="this.src='https://via.placeholder.com/320x220/334155/94a3b8?text=No+Image'">
                            <div class="meal-content">
                                <div class="meal-header">
                                    <div class="meal-id">ID: \${meal.id}</div>
                                </div>
                                <div class="meal-name">\${meal.name}</div>
                                <div class="meal-tags">
                                    <span class="meal-tag">📁 \${meal.categoria}</span>
                                    <span class="meal-tag">🌍 \${meal.area}</span>
                                </div>
                                <div class="meal-actions">
                                    <button class="btn btn-warning btn-small" onclick="editMeal(\${meal.id})">
                                        ✏️ Editar
                                    </button>
                                    <button class="btn btn-danger btn-small" onclick="deleteMeal(\${meal.id})">
                                        🗑️ Eliminar
                                    </button>
                                </div>
                            </div>
                        </div>
                    \`).join('');
                    
                    showAlert(\`✅ Se cargaron \${data.total} comidas\`, 'success');
                } catch (error) {
                    list.innerHTML = '<div class="empty-state" style="grid-column: 1 / -1;"><div class="empty-icon">❌</div><p>Error al cargar las comidas</p></div>';
                    showAlert('❌ Error al cargar las comidas', 'error');
                }
            }
            
            async function getRandomMeal() {
                showAlert('🎲 Obteniendo comida aleatoria...', 'success');
                try {
                    const response = await fetch('/meals/random/api');
                    const data = await response.json();
                    showAlert(\`✅ Comida guardada: "\${data.meal.name}"\`, 'success');
                    loadMeals();
                } catch (error) {
                    showAlert('❌ Error al obtener comida aleatoria', 'error');
                }
            }
            
            function openModal(type) {
                document.getElementById(\`\${type}Modal\`).classList.add('active');
            }
            
            function closeModal(type) {
                document.getElementById(\`\${type}Modal\`).classList.remove('active');
            }
            
            document.getElementById('createForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const meal = {
                    name: document.getElementById('create_name').value,
                    categoria: document.getElementById('create_categoria').value,
                    area: document.getElementById('create_area').value,
                    image_url: document.getElementById('create_image').value
                };
                
                try {
                    const response = await fetch('/meals', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(meal)
                    });
                    
                    if (response.ok) {
                        showAlert('✅ Comida creada exitosamente', 'success');
                        closeModal('create');
                        e.target.reset();
                        loadMeals();
                    } else {
                        showAlert('❌ Error al crear la comida', 'error');
                    }
                } catch (error) {
                    showAlert('❌ Error de conexión', 'error');
                }
            });
            
            async function editMeal(id) {
                try {
                    const response = await fetch(\`/meals/\${id}\`);
                    const meal = await response.json();
                    
                    currentEditId = id;
                    document.getElementById('edit_id').textContent = id;
                    document.getElementById('edit_name').value = meal.name;
                    document.getElementById('edit_categoria').value = meal.categoria;
                    document.getElementById('edit_area').value = meal.area;
                    document.getElementById('edit_image').value = meal.image_url;
                    
                    openModal('edit');
                } catch (error) {
                    showAlert('❌ Error al cargar la comida', 'error');
                }
            }
            
            document.getElementById('editForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const meal = {
                    name: document.getElementById('edit_name').value,
                    categoria: document.getElementById('edit_categoria').value,
                    area: document.getElementById('edit_area').value,
                    image_url: document.getElementById('edit_image').value
                };
                
                try {
                    const response = await fetch(\`/meals/\${currentEditId}\`, {
                        method: 'PUT',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(meal)
                    });
                    
                    if (response.ok) {
                        showAlert('✅ Comida actualizada exitosamente', 'success');
                        closeModal('edit');
                        loadMeals();
                    } else {
                        showAlert('❌ Error al actualizar la comida', 'error');
                    }
                } catch (error) {
                    showAlert('❌ Error de conexión', 'error');
                }
            });
            
            async function deleteMeal(id) {
                if (!confirm(\`¿Eliminar la comida #\${id}?\`)) return;
                
                try {
                    const response = await fetch(\`/meals/\${id}\`, { method: 'DELETE' });
                    if (response.ok) {
                        showAlert(\`✅ Comida #\${id} eliminada\`, 'success');
                        loadMeals();
                    } else {
                        showAlert('❌ Error al eliminar', 'error');
                    }
                } catch (error) {
                    showAlert('❌ Error de conexión', 'error');
                }
            }
            
            async function confirmDeleteAll() {
                if (!confirm('⚠️ ¿Eliminar TODAS las comidas?')) return;
                
                try {
                    const response = await fetch('/meals', { method: 'DELETE' });
                    const data = await response.json();
                    showAlert(\`✅ \${data.mensaje}\`, 'success');
                    loadMeals();
                } catch (error) {
                    showAlert('❌ Error al eliminar', 'error');
                }
            }
        </script>
    </body>
    </html>
    """

# ==================== API ENDPOINTS ====================

@app.get("/meals")
def get_all_meals():
    """Listar todas las comidas"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, categoria, area, image_url FROM Meals ORDER BY id DESC")
            rows = cursor.fetchall()
            
            meals = [
                {
                    "id": r[0],
                    "name": r[1],
                    "categoria": r[2],
                    "area": r[3],
                    "image_url": r[4]
                } for r in rows
            ]
            
            return {"total": len(meals), "meals": meals}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meals/{meal_id}")
def get_meal(meal_id: int):
    """Obtener una comida por ID"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, categoria, area, image_url FROM Meals WHERE id = ?",
                meal_id
            )
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Comida no encontrada")
            
            return {
                "id": row[0],
                "name": row[1],
                "categoria": row[2],
                "area": row[3],
                "image_url": row[4]
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meals/random/api")
def get_random_meal():
    """Obtener comida aleatoria de TheMealDB y guardarla"""
    try:
        response = requests.get(THEMEALDB_URL)
        response.raise_for_status()
        data = response.json()["meals"][0]

        name = data["strMeal"]
        categoria = data["strCategory"]
        area = data["strArea"]
        image_url = data["strMealThumb"]

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Meals (name, categoria, area, image_url) OUTPUT INSERTED.id VALUES (?, ?, ?, ?)",
                name, categoria, area, image_url
            )
            new_id = cursor.fetchone()[0]
            conn.commit()

        return {
            "mensaje": "Comida guardada exitosamente",
            "meal": {
                "id": new_id,
                "name": name,
                "categoria": categoria,
                "area": area,
                "image_url": image_url
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meals")
def create_meal(meal: MealCreate):
    """Crear una comida manualmente"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Meals (name, categoria, area, image_url) OUTPUT INSERTED.id VALUES (?, ?, ?, ?)",
                meal.name, meal.categoria, meal.area, meal.image_url
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
        
        return {
            "mensaje": "Comida creada exitosamente",
            "meal": {
                "id": new_id,
                "name": meal.name,
                "categoria": meal.categoria,
                "area": meal.area,
                "image_url": meal.image_url
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/meals/{meal_id}")
def update_meal(meal_id: int, meal: MealUpdate):
    """Actualizar una comida"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name, categoria, area, image_url FROM Meals WHERE id = ?", meal_id)
            existing = cursor.fetchone()
            
            if not existing:
                raise HTTPException(status_code=404, detail="Comida no encontrada")
            
            new_name = meal.name if meal.name else existing[1]
            new_categoria = meal.categoria if meal.categoria else existing[2]
            new_area = meal.area if meal.area else existing[3]
            new_image = meal.image_url if meal.image_url else existing[4]
            
            cursor.execute(
                "UPDATE Meals SET name = ?, categoria = ?, area = ?, image_url = ? WHERE id = ?",
                new_name, new_categoria, new_area, new_image, meal_id
            )
            conn.commit()
            
            return {
                "mensaje": "Comida actualizada exitosamente",
                "meal": {
                    "id": meal_id,
                    "name": new_name,
                    "categoria": new_categoria,
                    "area": new_area,
                    "image_url": new_image
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/meals/{meal_id}")
def delete_meal(meal_id: int):
    """Eliminar una comida por ID"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM Meals WHERE id = ?", meal_id)
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Comida no encontrada")
            
            cursor.execute("DELETE FROM Meals WHERE id = ?", meal_id)
            conn.commit()
            
            return {"mensaje": f"Comida con ID {meal_id} eliminada exitosamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/meals")
def delete_all_meals():
    """Eliminar todas las comidas"""
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Meals")
            count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM Meals")
            conn.commit()
            
            return {
                "mensaje": f"Se eliminaron {count} comidas exitosamente",
                "total_eliminados": count
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))