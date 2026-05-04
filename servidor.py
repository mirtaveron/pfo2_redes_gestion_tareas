from flask import Flask, request, jsonify, render_template_string
import sqlite3
import hashlib
import secrets
from datetime import datetime
from functools import wraps

app = Flask(__name__)

# Configuración de la base de datos
DB_NAME = 'tasks.db'

# Almacenamiento temporal de sesiones
active_sessions = {}

def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de tareas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            completada BOOLEAN DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente")


def hash_password(password, salt=None):
    """
    Hashea una contraseña usando SHA-256 con salt
    
    Args:
        password: Contraseña en texto plano
        salt: Salt hexadecimal (se genera uno nuevo si no se proporciona)
    
    Returns:
        tuple: (password_hash, salt)
    """
    if salt is None:
        # Generar un salt aleatorio de 32 bytes
        salt = secrets.token_hex(32)
    
    # Combinar password + salt y hashear
    password_salt = password + salt
    password_hash = hashlib.sha256(password_salt.encode()).hexdigest()
    
    return password_hash, salt


def verify_password(password, stored_hash, salt):
    """Verifica si una contraseña coincide con el hash almacenado"""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == stored_hash


def require_auth(f):
    """Decorador para proteger endpoints que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token de autenticación requerido'}), 401
        
        # Verificar si el token es válido
        if token not in active_sessions:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Agregar usuario_id al request para usar en la función
        request.usuario_id = active_sessions[token]
        return f(*args, **kwargs)
    
    return decorated_function


@app.route('/')
def home():
    """Página de inicio con información de la API"""
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API de Gestión de Tareas</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            .content {
                padding: 40px;
            }
            .section {
                margin-bottom: 30px;
            }
            .section h2 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 1.8em;
            }
            .endpoint {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 5px;
            }
            .method {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
                margin-right: 10px;
                font-size: 0.9em;
            }
            .post { background: #28a745; color: white; }
            .get { background: #007bff; color: white; }
            .put { background: #ffc107; color: black; }
            .delete { background: #dc3545; color: white; }
            code {
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .example {
                background: #2d3748;
                color: #e2e8f0;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                margin-top: 10px;
            }
            .example pre {
                margin: 0;
                font-family: 'Courier New', monospace;
            }
            .feature-list {
                list-style: none;
                padding: 0;
            }
            .feature-list li {
                padding: 10px 0;
                border-bottom: 1px solid #e9ecef;
            }
            .feature-list li:before {
                content: "✓ ";
                color: #28a745;
                font-weight: bold;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 API de Gestión de Tareas</h1>
                <p>Sistema completo con autenticación y persistencia en SQLite</p>
            </div>
            
            <div class="content">
                <div class="section">
                    <h2>Características</h2>
                    <ul class="feature-list">
                        <li>Autenticación segura con contraseñas hasheadas (SHA-256 + Salt)</li>
                        <li>Persistencia de datos con SQLite</li>
                        <li>API RESTful completa</li>
                        <li>Sistema de tokens para sesiones</li>
                        <li>Gestión completa de tareas (CRUD)</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Endpoints Disponibles</h2>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <strong>/registro</strong>
                        <p>Registra un nuevo usuario</p>
                        <div class="example">
                            <pre>{
  "usuario": "maria",
  "contraseña": "miPassword123"
}</pre>
                        </div>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <strong>/login</strong>
                        <p>Inicia sesión y obtiene un token de autenticación</p>
                        <div class="example">
                            <pre>{
  "usuario": "maria",
  "contraseña": "miPassword123"
}</pre>
                        </div>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <strong>/tareas</strong>
                        <p>Obtiene todas las tareas del usuario (requiere token)</p>
                        <div class="example">
                            <pre>Header: Authorization: tu_token_aqui</pre>
                        </div>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <strong>/tareas</strong>
                        <p>Crea una nueva tarea (requiere token)</p>
                        <div class="example">
                            <pre>{
  "titulo": "Completar proyecto",
  "descripcion": "Finalizar el PFO 2"
}</pre>
                        </div>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method put">PUT</span>
                        <strong>/tareas/&lt;id&gt;</strong>
                        <p>Actualiza una tarea existente (requiere token)</p>
                    </div>
                    
                    <div class="endpoint">
                        <span class="method delete">DELETE</span>
                        <strong>/tareas/&lt;id&gt;</strong>
                        <p>Elimina una tarea (requiere token)</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Ejemplo de Uso</h2>
                    <div class="example">
                        <pre># 1. Registrar usuario
curl -X POST http://localhost:5000/registro \
  -H "Content-Type: application/json" \
  -d '{"usuario":"maria","contraseña":"pass123"}'
 
# 2. Iniciar sesión
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"usuario":"maria","contraseña":"pass123"}'
 
# 3. Obtener tareas (usar el token recibido)
curl -X GET http://localhost:5000/tareas \
  -H "Authorization: tu_token_aqui"</pre>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)


@app.route('/registro', methods=['POST'])
def registro():
    """Endpoint para registrar nuevos usuarios"""
    try:
        data = request.get_json()
        
        # Validar datos de entrada
        if not data or 'usuario' not in data or 'contraseña' not in data:
            return jsonify({'error': 'Se requieren usuario y contraseña'}), 400
        
        usuario = data['usuario'].strip()
        password = data['contraseña']
        
        # Validaciones básicas
        if len(usuario) < 3:
            return jsonify({'error': 'El usuario debe tener al menos 3 caracteres'}), 400
        
        if len(password) < 4:
            return jsonify({'error': 'La contraseña debe tener al menos 4 caracteres'}), 400
        
        # Hashear la contraseña
        password_hash, salt = hash_password(password)
        
        # Guardar en la base de datos
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO usuarios (usuario, password_hash, salt) VALUES (?, ?, ?)',
                (usuario, password_hash, salt)
            )
            conn.commit()
            usuario_id = cursor.lastrowid
            
            return jsonify({
                'mensaje': 'Usuario registrado exitosamente',
                'usuario': usuario,
                'id': usuario_id
            }), 201
            
        except sqlite3.IntegrityError:
            return jsonify({'error': 'El usuario ya existe'}), 409
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500


@app.route('/login', methods=['POST'])
def login():
    """Endpoint para iniciar sesión"""
    try:
        data = request.get_json()
        
        if not data or 'usuario' not in data or 'contraseña' not in data:
            return jsonify({'error': 'Se requieren usuario y contraseña'}), 400
        
        usuario = data['usuario']
        password = data['contraseña']
        
        # Buscar usuario en la base de datos
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, password_hash, salt FROM usuarios WHERE usuario = ?',
            (usuario,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        usuario_id, stored_hash, salt = result
        
        # Verificar contraseña
        if not verify_password(password, stored_hash, salt):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Generar token de sesión
        token = secrets.token_hex(32)
        active_sessions[token] = usuario_id
        
        return jsonify({
            'mensaje': 'Inicio de sesión exitoso',
            'token': token,
            'usuario': usuario
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500


@app.route('/tareas', methods=['GET'])
@require_auth
def get_tareas():
    """Endpoint para obtener todas las tareas del usuario"""
    try:
        usuario_id = request.usuario_id
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, titulo, descripcion, completada, fecha_creacion
            FROM tareas
            WHERE usuario_id = ?
            ORDER BY fecha_creacion DESC
        ''', (usuario_id,))
        
        tareas = []
        for row in cursor.fetchall():
            tareas.append({
                'id': row[0],
                'titulo': row[1],
                'descripcion': row[2],
                'completada': bool(row[3]),
                'fecha_creacion': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'tareas': tareas,
            'total': len(tareas)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500


@app.route('/tareas', methods=['POST'])
@require_auth
def crear_tarea():
    """Endpoint para crear una nueva tarea"""
    try:
        data = request.get_json()
        
        if not data or 'titulo' not in data:
            return jsonify({'error': 'Se requiere un título para la tarea'}), 400
        
        titulo = data['titulo'].strip()
        descripcion = data.get('descripcion', '').strip()
        
        if not titulo:
            return jsonify({'error': 'El título no puede estar vacío'}), 400
        
        usuario_id = request.usuario_id
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tareas (usuario_id, titulo, descripcion)
            VALUES (?, ?, ?)
        ''', (usuario_id, titulo, descripcion))
        
        conn.commit()
        tarea_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'mensaje': 'Tarea creada exitosamente',
            'id': tarea_id,
            'titulo': titulo
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500


@app.route('/tareas/<int:tarea_id>', methods=['PUT'])
@require_auth
def actualizar_tarea(tarea_id):
    """Endpoint para actualizar una tarea existente"""
    try:
        data = request.get_json()
        usuario_id = request.usuario_id
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Verificar que la tarea pertenece al usuario
        cursor.execute(
            'SELECT id FROM tareas WHERE id = ? AND usuario_id = ?',
            (tarea_id, usuario_id)
        )
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Tarea no encontrada'}), 404
        
        # Actualizar campos proporcionados
        updates = []
        params = []
        
        if 'titulo' in data:
            updates.append('titulo = ?')
            params.append(data['titulo'])
        
        if 'descripcion' in data:
            updates.append('descripcion = ?')
            params.append(data['descripcion'])
        
        if 'completada' in data:
            updates.append('completada = ?')
            params.append(1 if data['completada'] else 0)
        
        if not updates:
            conn.close()
            return jsonify({'error': 'No hay campos para actualizar'}), 400
        
        params.extend([tarea_id, usuario_id])
        query = f"UPDATE tareas SET {', '.join(updates)} WHERE id = ? AND usuario_id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return jsonify({'mensaje': 'Tarea actualizada exitosamente'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500


@app.route('/tareas/<int:tarea_id>', methods=['DELETE'])
@require_auth
def eliminar_tarea(tarea_id):
    """Endpoint para eliminar una tarea"""
    try:
        usuario_id = request.usuario_id
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM tareas WHERE id = ? AND usuario_id = ?',
            (tarea_id, usuario_id)
        )
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Tarea no encontrada'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'mensaje': 'Tarea eliminada exitosamente'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500


if __name__ == '__main__':
    print("Iniciando servidor de gestión de tareas...")
    init_db()
    print("Servidor corriendo en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)