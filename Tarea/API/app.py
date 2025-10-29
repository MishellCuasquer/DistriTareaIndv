from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import pyodbc
import os
from datetime import datetime, date
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación
app = FastAPI(
    title="🛒 API de Inventario de Comida",
    description="Sistema de gestión de inventario para alimentos",
    version="1.0.0"
)

# Configuración de la base de datos
conn_str = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={os.getenv('DB_SERVER')},{os.getenv('DB_PORT')};"
    f"DATABASE={os.getenv('DB_NAME')};"
    f"UID={os.getenv('DB_USER')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    f"TrustServerCertificate=yes;"
)

# Modelos Pydantic
class ProductoBase(BaseModel):
    codigo_barras: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    categoria: Optional[str] = Field(None, max_length=50)
    proveedor: Optional[str] = Field(None, max_length=100)
    precio_compra: float = Field(..., gt=0)
    precio_venta: float = Field(..., gt=0)
    stock_actual: int = Field(0, ge=0)
    stock_minimo: int = Field(10, ge=0)
    fecha_vencimiento: Optional[date] = None

    @validator('precio_venta')
    def precio_venta_mayor_compra(cls, v, values):
        if 'precio_compra' in values and v < values['precio_compra']:
            raise ValueError('El precio de venta debe ser mayor o igual al precio de compra')
        return v

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    codigo_barras: Optional[str] = Field(None, max_length=50)
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    categoria: Optional[str] = Field(None, max_length=50)
    proveedor: Optional[str] = Field(None, max_length=100)
    precio_compra: Optional[float] = Field(None, gt=0)
    precio_venta: Optional[float] = Field(None, gt=0)
    stock_actual: Optional[int] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    fecha_vencimiento: Optional[date] = None
    activo: Optional[bool] = None

class Producto(ProductoBase):
    id: int
    fecha_creacion: datetime
    activo: bool

    class Config:
        from_attributes = True

# Funciones de base de datos
def get_db_connection():
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar a la base de datos: {str(e)}")

# ==================== INTERFAZ WEB ====================

@app.get("/", response_class=HTMLResponse)
async def home():
    """Interfaz web principal del inventario"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🏪 Gestión de Inventario</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen">
            <!-- Barra de navegación -->
            <nav class="bg-blue-600 text-white shadow-lg">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between h-16">
                        <div class="flex items-center">
                            <i class="ri-store-2-line text-2xl mr-2"></i>
                            <span class="text-xl font-bold">Sistema de Inventario</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <button onclick="mostrarModalAgregar()" class="bg-green-500 hover:bg-green-600 px-4 py-2 rounded-md flex items-center">
                                <i class="ri-add-line mr-1"></i> Nuevo Producto
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <!-- Contenido principal -->
            <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <!-- Resúmenes -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="p-3 rounded-full bg-blue-100 text-blue-600 mr-4">
                                <i class="ri-box-2-line text-2xl"></i>
                            </div>
                            <div>
                                <p class="text-gray-500 text-sm">Total Productos</p>
                                <h3 id="total-productos" class="text-2xl font-bold">0</h3>
                            </div>
                        </div>
                    </div>
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="p-3 rounded-full bg-yellow-100 text-yellow-600 mr-4">
                                <i class="ri-alert-line text-2xl"></i>
                            </div>
                            <div>
                                <p class="text-gray-500 text-sm">Stock Bajo</p>
                                <h3 id="stock-bajo" class="text-2xl font-bold">0</h3>
                            </div>
                        </div>
                    </div>
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="p-3 rounded-full bg-red-100 text-red-600 mr-4">
                                <i class="ri-calendar-close-line text-2xl"></i>
                            </div>
                            <div>
                                <p class="text-gray-500 text-sm">Por Vencer</p>
                                <h3 id="por-vencer" class="text-2xl font-bold">0</h3>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tabla de productos -->
                <div class="bg-white shadow rounded-lg overflow-hidden">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h2 class="text-lg font-medium text-gray-900">Inventario de Productos</h2>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio Venta</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vencimiento</th>
                                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                                </tr>
                            </thead>
                            <tbody id="productos-table" class="bg-white divide-y divide-gray-200">
                                <!-- Los productos se cargarán aquí dinámicamente -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>

        <!-- Modal para agregar/editar producto -->
        <div id="modal-producto" class="fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
            <div class="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                <div class="p-6">
                    <div class="flex justify-between items-center mb-4">
                        <h3 id="modal-titulo" class="text-xl font-bold">Nuevo Producto</h3>
                        <button onclick="cerrarModal()" class="text-gray-500 hover:text-gray-700">
                            <i class="ri-close-line text-2xl"></i>
                        </button>
                    </div>
                    <form id="form-producto" class="space-y-4">
                        <input type="hidden" id="producto-id">
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label for="codigo_barras" class="block text-sm font-medium text-gray-700">Código de Barras</label>
                                <input type="text" id="codigo_barras" name="codigo_barras" required
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            </div>
                            
                            <div>
                                <label for="nombre" class="block text-sm font-medium text-gray-700">Nombre del Producto</label>
                                <input type="text" id="nombre" name="nombre" required
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            </div>
                            
                            <div class="md:col-span-2">
                                <label for="descripcion" class="block text-sm font-medium text-gray-700">Descripción</label>
                                <textarea id="descripcion" name="descripcion" rows="2"
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"></textarea>
                            </div>
                            
                            <div>
                                <label for="categoria" class="block text-sm font-medium text-gray-700">Categoría</label>
                                <input type="text" id="categoria" name="categoria"
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            </div>
                            
                            <div>
                                <label for="proveedor" class="block text-sm font-medium text-gray-700">Proveedor</label>
                                <input type="text" id="proveedor" name="proveedor"
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            </div>
                            
                            <div>
                                <label for="precio_compra" class="block text-sm font-medium text-gray-700">Precio de Compra</label>
                                <input type="number" id="precio_compra" name="precio_compra" step="0.01" min="0" required
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            </div>
                            
                            <div>
                                <label for="precio_venta" class="block text-sm font-medium text-gray-700">Precio de Venta</label>
                                <input type="number" id="precio_venta" name="precio_venta" step="0.01" min="0" required
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            </div>
                            
                            <div>
                                <label for="stock_actual" class="block text-sm font-medium text-gray-700">Stock Actual</label>
                                <input type="number" id="stock_actual" name="stock_actual" min="0" required
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            </div>
                            
                            <div>
                                <label for="stock_minimo" class="block text-sm font-medium text-gray-700">Stock Mínimo</label>
                                <input type="number" id="stock_minimo" name="stock_minimo" min="0" required
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            </div>
                            
                            <div>
                                <label for="fecha_vencimiento" class="block text-sm font-medium text-gray-700">Fecha de Vencimiento</label>
                                <input type="date" id="fecha_vencimiento" name="fecha_vencimiento"
                                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            </div>
                            
                            <div class="flex items-center">
                                <input type="checkbox" id="activo" name="activo" checked
                                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
                                <label for="activo" class="ml-2 block text-sm text-gray-700">Producto Activo</label>
                            </div>
                        </div>
                        
                        <div class="flex justify-end space-x-3 pt-4">
                            <button type="button" onclick="cerrarModal()"
                                class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                Cancelar
                            </button>
                            <button type="submit"
                                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                Guardar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script>
            // Variables globales
            let productos = [];
            let modoEdicion = false;
            
            // Cargar datos al iniciar
            document.addEventListener('DOMContentLoaded', function() {
                cargarProductos();
                configurarFormulario();
            });
            
            // Configurar el formulario
            function configurarFormulario() {
                const form = document.getElementById('form-producto');
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    guardarProducto();
                });
                
                // Validar que el precio de venta sea mayor o igual al de compra
                const precioCompra = document.getElementById('precio_compra');
                const precioVenta = document.getElementById('precio_venta');
                
                [precioCompra, precioVenta].forEach(input => {
                    input.addEventListener('change', function() {
                        const compra = parseFloat(precioCompra.value) || 0;
                        const venta = parseFloat(precioVenta.value) || 0;
                        
                        if (venta < compra) {
                            alert('El precio de venta no puede ser menor al precio de compra');
                            precioVenta.value = compra.toFixed(2);
                        }
                    });
                });
            }
            
            // Cargar lista de productos
            async function cargarProductos() {
                try {
                    const response = await fetch('/api/productos');
                    if (!response.ok) throw new Error('Error al cargar productos');
                    
                    productos = await response.json();
                    actualizarTabla();
                    actualizarResumenes();
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error al cargar los productos: ' + error.message);
                }
            }
            
            // Actualizar la tabla de productos
            function actualizarTabla() {
                const tbody = document.getElementById('productos-table');
                tbody.innerHTML = '';
                
                if (productos.length === 0) {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                            No hay productos registrados
                        </td>
                    `;
                    tbody.appendChild(tr);
                    return;
                }
                
                productos.forEach(producto => {
                    const tr = document.createElement('tr');
                    tr.className = producto.activo ? '' : 'bg-gray-50 text-gray-400';
                    
                    // Formatear fecha
                    const fechaVencimiento = producto.fecha_vencimiento 
                        ? new Date(producto.fecha_vencimiento).toLocaleDateString('es-ES')
                        : 'Sin fecha';
                    
                    // Determinar clases de stock
                    let stockClases = 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full ';
                    if (producto.stock_actual <= 0) {
                        stockClases += 'bg-red-100 text-red-800';
                    } else if (producto.stock_actual <= producto.stock_minimo) {
                        stockClases += 'bg-yellow-100 text-yellow-800';
                    } else {
                        stockClases += 'bg-green-100 text-green-800';
                    }
                    
                    tr.innerHTML = `
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${producto.codigo_barras}</td>
                        <td class="px-6 py-4">
                            <div class="text-sm font-medium ${producto.activo ? 'text-gray-900' : 'text-gray-400'}">${producto.nombre}</div>
                            <div class="text-sm ${producto.activo ? 'text-gray-500' : 'text-gray-400'}">${producto.descripcion || 'Sin descripción'}</div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm ${producto.activo ? 'text-gray-900' : 'text-gray-400'}">${producto.categoria || 'Sin categoría'}</td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span class="${stockClases}">
                                ${producto.stock_actual} ${producto.stock_actual <= producto.stock_minimo ? '⚠️' : ''}
                            </span>
                            ${producto.stock_actual <= producto.stock_minimo ? 
                              `<span class="text-xs text-gray-500 ml-1">(mín: ${producto.stock_minimo})</span>` : ''}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm ${producto.activo ? 'text-gray-900' : 'text-gray-400'}">
                            $${producto.precio_venta.toFixed(2)}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm ${producto.activo ? 'text-gray-900' : 'text-gray-400'}">
                            ${fechaVencimiento}
                            ${producto.fecha_vencimiento && new Date(producto.fecha_vencimiento) < new Date() ? '⚠️' : ''}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button onclick="editarProducto(${producto.id})" class="text-blue-600 hover:text-blue-900 mr-3">
                                <i class="ri-edit-line"></i>
                            </button>
                            <button onclick="eliminarProducto(${producto.id})" class="text-red-600 hover:text-red-900">
                                <i class="ri-delete-bin-line"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            }
            
            // Actualizar resúmenes
            function actualizarResumenes() {
                // Total de productos
                document.getElementById('total-productos').textContent = productos.length;
                
                // Productos con stock bajo
                const stockBajo = productos.filter(p => p.stock_actual <= p.stock_minimo && p.activo).length;
                document.getElementById('stock-bajo').textContent = stockBajo;
                
                // Productos por vencer (en los próximos 30 días)
                const hoy = new Date();
                const en30Dias = new Date();
                en30Dias.setDate(hoy.getDate() + 30);
                
                const porVencer = productos.filter(p => {
                    if (!p.fecha_vencimiento || !p.activo) return false;
                    const fechaVencimiento = new Date(p.fecha_vencimiento);
                    return fechaVencimiento >= hoy && fechaVencimiento <= en30Dias;
                }).length;
                
                document.getElementById('por-vencer').textContent = porVencer;
            }
            
            // Mostrar modal para agregar producto
            function mostrarModalAgregar() {
                modoEdicion = false;
                document.getElementById('modal-titulo').textContent = 'Nuevo Producto';
                document.getElementById('form-producto').reset();
                document.getElementById('producto-id').value = '';
                document.getElementById('modal-producto').classList.remove('hidden');
                document.getElementById('modal-producto').classList.add('flex');
            }
            
            // Cerrar modal
            function cerrarModal() {
                document.getElementById('modal-producto').classList.add('hidden');
                document.getElementById('modal-producto').classList.remove('flex');
            }
            
            // Cargar datos de un producto en el formulario
            async function editarProducto(id) {
                try {
                    const response = await fetch(`/api/productos/${id}`);
                    if (!response.ok) throw new Error('Error al cargar el producto');
                    
                    const producto = await response.json();
                    
                    modoEdicion = true;
                    document.getElementById('modal-titulo').textContent = 'Editar Producto';
                    
                    // Llenar el formulario con los datos del producto
                    const form = document.getElementById('form-producto');
                    form.reset();
                    
                    document.getElementById('producto-id').value = producto.id;
                    document.getElementById('codigo_barras').value = producto.codigo_barras;
                    document.getElementById('nombre').value = producto.nombre;
                    document.getElementById('descripcion').value = producto.descripcion || '';
                    document.getElementById('categoria').value = producto.categoria || '';
                    document.getElementById('proveedor').value = producto.proveedor || '';
                    document.getElementById('precio_compra').value = producto.precio_compra;
                    document.getElementById('precio_venta').value = producto.precio_venta;
                    document.getElementById('stock_actual').value = producto.stock_actual;
                    document.getElementById('stock_minimo').value = producto.stock_minimo;
                    document.getElementById('activo').checked = producto.activo;
                    
                    if (producto.fecha_vencimiento) {
                        const fecha = new Date(producto.fecha_vencimiento);
                        const fechaFormato = fecha.toISOString().split('T')[0];
                        document.getElementById('fecha_vencimiento').value = fechaFormato;
                    } else {
                        document.getElementById('fecha_vencimiento').value = '';
                    }
                    
                    document.getElementById('modal-producto').classList.remove('hidden');
                    document.getElementById('modal-producto').classList.add('flex');
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error al cargar el producto: ' + error.message);
                }
            }
            
            // Guardar producto (crear o actualizar)
            async function guardarProducto() {
                try {
                    const form = document.getElementById('form-producto');
                    const formData = new FormData(form);
                    const productoId = document.getElementById('producto-id').value;
                    
                    const productoData = {
                        codigo_barras: formData.get('codigo_barras'),
                        nombre: formData.get('nombre'),
                        descripcion: formData.get('descripcion') || null,
                        categoria: formData.get('categoria') || null,
                        proveedor: formData.get('proveedor') || null,
                        precio_compra: parseFloat(formData.get('precio_compra')),
                        precio_venta: parseFloat(formData.get('precio_venta')),
                        stock_actual: parseInt(formData.get('stock_actual')),
                        stock_minimo: parseInt(formData.get('stock_minimo')),
                        fecha_vencimiento: formData.get('fecha_vencimiento') || null,
                        activo: formData.get('activo') === 'on'
                    };
                    
                    let response;
                    const url = modoEdicion 
                        ? `/api/productos/${productoId}`
                        : '/api/productos';
                    
                    const method = modoEdicion ? 'PUT' : 'POST';
                    
                    response = await fetch(url, {
                        method: method,
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(productoData)
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'Error al guardar el producto');
                    }
                    
                    cerrarModal();
                    cargarProductos();
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error al guardar el producto: ' + error.message);
                }
            }
            
            // Eliminar producto
            async function eliminarProducto(id) {
                if (!confirm('¿Estás seguro de que deseas eliminar este producto?')) {
                    return;
                }
                
                try {
                    const response = await fetch(`/api/productos/${id}`, {
                        method: 'DELETE'
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'Error al eliminar el producto');
                    }
                    
                    cargarProductos();
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error al eliminar el producto: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """

# ==================== API ENDPOINTS ====================

@app.post("/api/productos/", response_model=Producto)
async def crear_producto(producto: ProductoCreate):
    """Crear un nuevo producto en el inventario"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO Productos (
            codigo_barras, nombre, descripcion, categoria, proveedor,
            precio_compra, precio_venta, stock_actual, stock_minimo, fecha_vencimiento
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(
            query,
            (
                producto.codigo_barras,
                producto.nombre,
                producto.descripcion,
                producto.categoria,
                producto.proveedor,
                producto.precio_compra,
                producto.precio_venta,
                producto.stock_actual,
                producto.stock_minimo,
                producto.fecha_vencimiento
            )
        )
        
        # Obtener el ID del producto recién insertado
        cursor.execute("SELECT SCOPE_IDENTITY()")
        producto_id = cursor.fetchone()[0]
        
        conn.commit()
        
        # Obtener el producto completo para devolverlo
        cursor.execute(
            "SELECT * FROM Productos WHERE id = ?",
            (producto_id,)
        )
        
        columns = [column[0] for column in cursor.description]
        producto_creado = dict(zip(columns, cursor.fetchone()))
        
        return producto_creado
        
    except pyodbc.IntegrityError as e:
        if "IX_Productos_codigo_barras" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Ya existe un producto con este código de barras"
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.get("/api/productos/", response_model=List[Producto])
async def listar_productos(activo: bool = None, categoria: str = None):
    """Listar todos los productos del inventario"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM Productos WHERE 1=1"
        params = []
        
        if activo is not None:
            query += " AND activo = ?"
            params.append(activo)
            
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
            
        query += " ORDER BY nombre"
        
        cursor.execute(query, params)
        
        columns = [column[0] for column in cursor.description]
        productos = []
        
        for row in cursor.fetchall():
            # Convertir la fecha de vencimiento a string ISO si existe
            row_dict = dict(zip(columns, row))
            if 'fecha_vencimiento' in row_dict and row_dict['fecha_vencimiento']:
                row_dict['fecha_vencimiento'] = row_dict['fecha_vencimiento'].isoformat()
            if 'fecha_creacion' in row_dict and row_dict['fecha_creacion']:
                row_dict['fecha_creacion'] = row_dict['fecha_creacion'].isoformat()
            productos.append(row_dict)
        
        return productos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.get("/api/productos/{producto_id}", response_model=Producto)
async def obtener_producto(producto_id: int):
    """Obtener un producto por su ID"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM Productos WHERE id = ?",
            (producto_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        columns = [column[0] for column in cursor.description]
        producto = dict(zip(columns, row))
        
        # Convertir fechas a string ISO
        if 'fecha_vencimiento' in producto and producto['fecha_vencimiento']:
            producto['fecha_vencimiento'] = producto['fecha_vencimiento'].isoformat()
        if 'fecha_creacion' in producto and producto['fecha_creacion']:
            producto['fecha_creacion'] = producto['fecha_creacion'].isoformat()
        
        return producto
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.put("/api/productos/{producto_id}", response_model=Producto)
async def actualizar_producto(producto_id: int, producto: ProductoUpdate):
    """Actualizar un producto existente"""
    conn = None
    cursor = None
    try:
        # Verificar si el producto existe
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM Productos WHERE id = ?", (producto_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Construir la consulta dinámicamente basada en los campos proporcionados
        update_fields = []
        params = []
        
        if producto.codigo_barras is not None:
            update_fields.append("codigo_barras = ?")
            params.append(producto.codigo_barras)
            
        if producto.nombre is not None:
            update_fields.append("nombre = ?")
            params.append(producto.nombre)
            
        if producto.descripcion is not None:
            update_fields.append("descripcion = ?")
            params.append(producto.descripcion)
            
        if producto.categoria is not None:
            update_fields.append("categoria = ?")
            params.append(producto.categoria)
            
        if producto.proveedor is not None:
            update_fields.append("proveedor = ?")
            params.append(producto.proveedor)
            
        if producto.precio_compra is not None:
            update_fields.append("precio_compra = ?")
            params.append(producto.precio_compra)
            
        if producto.precio_venta is not None:
            update_fields.append("precio_venta = ?")
            params.append(producto.precio_venta)
            
        if producto.stock_actual is not None:
            update_fields.append("stock_actual = ?")
            params.append(producto.stock_actual)
            
        if producto.stock_minimo is not None:
            update_fields.append("stock_minimo = ?")
            params.append(producto.stock_minimo)
            
        if producto.fecha_vencimiento is not None:
            update_fields.append("fecha_vencimiento = ?")
            params.append(producto.fecha_vencimiento)
            
        if producto.activo is not None:
            update_fields.append("activo = ?")
            params.append(producto.activo)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        # Agregar el ID al final para el WHERE
        params.append(producto_id)
        
        # Construir y ejecutar la consulta
        query = f"UPDATE Productos SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        
        # Obtener el producto actualizado para devolverlo
        cursor.execute("SELECT * FROM Productos WHERE id = ?", (producto_id,))
        
        columns = [column[0] for column in cursor.description]
        producto_actualizado = dict(zip(columns, cursor.fetchone()))
        
        # Convertir fechas a string ISO
        if 'fecha_vencimiento' in producto_actualizado and producto_actualizado['fecha_vencimiento']:
            producto_actualizado['fecha_vencimiento'] = producto_actualizado['fecha_vencimiento'].isoformat()
        if 'fecha_creacion' in producto_actualizado and producto_actualizado['fecha_creacion']:
            producto_actualizado['fecha_creacion'] = producto_actualizado['fecha_creacion'].isoformat()
        
        return producto_actualizado
        
    except pyodbc.IntegrityError as e:
        if "IX_Productos_codigo_barras" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Ya existe un producto con este código de barras"
            )
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.delete("/api/productos/{producto_id}")
async def eliminar_producto(producto_id: int):
    """Eliminar un producto del inventario"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si el producto existe
        cursor.execute("SELECT id FROM Productos WHERE id = ?", (producto_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Eliminar el producto
        cursor.execute("DELETE FROM Productos WHERE id = ?", (producto_id,))
        conn.commit()
        
        return {"mensaje": "Producto eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Ejecutar la aplicación si se ejecuta directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
