# 📋 Sistema de Gestión de Tareas con API REST

Sistema completo de gestión de tareas con API REST desarrollado en Flask, autenticación segura y persistencia en SQLite.

## 🎯 Características

- ✅ **API REST completa** con endpoints CRUD
- 🔐 **Autenticación segura** con contraseñas hasheadas (SHA-256 + Salt)
- 💾 **Persistencia de datos** con SQLite
- 🎫 **Sistema de tokens** para manejo de sesiones
- 🖥️ **Cliente de consola** interactivo
- 📱 **Interfaz web** informativa

## 📁 Estructura del Proyecto

```
task_manager_api/
├── servidor.py          # API Flask con todos los endpoints
├── cliente.py           # Cliente de consola interactivo
├── requirements.txt     # Dependencias del proyecto
├── tasks.db            # Base de datos SQLite (se crea automáticamente)
└── README.md           # Esta documentación
```

## 🔧 Instalación

### Prerrequisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Paso 1: Clonar o descargar el proyecto

```bash
git clone <url-del-repositorio>
cd task_manager_api
```

### Paso 2: Instalar dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install Flask requests
```

## 💻 Uso

### Iniciar el Servidor

En una terminal, ejecuta:

```bash
python servidor.py
```

Deberías ver:

```
Iniciando servidor de gestión de tareas...
Base de datos inicializada correctamente
Servidor corriendo en http://localhost:5000
```

### Usar el Cliente de Consola

En **otra terminal**, ejecuta:

```bash
python cliente.py
```

### Acceder a la Interfaz Web

Abre tu navegador y visita:

```
http://localhost:5000
```

Verás una página con toda la documentación de la API.

## 📡 Endpoints de la API

### 🔓 Autenticación

#### 1. Registrar Usuario

```bash
POST /registro
Content-Type: application/json

{
  "usuario": "maria",
  "contraseña": "miPassword123"
}
```

**Respuesta exitosa (201):**
```json
{
  "mensaje": "Usuario registrado exitosamente",
  "usuario": "maria",
  "id": 1
}
```

#### 2. Iniciar Sesión

```bash
POST /login
Content-Type: application/json

{
  "usuario": "maria",
  "contraseña": "miPassword123"
}
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Inicio de sesión exitoso",
  "token": "a1b2c3d4e5f6...",
  "usuario": "maria"
}
```

### 📝 Gestión de Tareas

**IMPORTANTE:** Todos estos endpoints requieren el header de autenticación:
```
Authorization: tu_token_aqui
```

#### 3. Obtener Todas las Tareas

```bash
GET /tareas
Authorization: tu_token_aqui
```

**Respuesta (200):**
```json
{
  "tareas": [
    {
      "id": 1,
      "titulo": "Completar proyecto",
      "descripcion": "Finalizar el PFO 2",
      "completada": false,
      "fecha_creacion": "2025-05-04 10:30:00"
    }
  ],
  "total": 1
}
```

#### 4. Crear Nueva Tarea

```bash
POST /tareas
Authorization: tu_token_aqui
Content-Type: application/json

{
  "titulo": "Estudiar Flask",
  "descripcion": "Repasar rutas y decoradores"
}
```

**Respuesta (201):**
```json
{
  "mensaje": "Tarea creada exitosamente",
  "id": 2,
  "titulo": "Estudiar Flask"
}
```

#### 5. Actualizar Tarea

```bash
PUT /tareas/1
Authorization: tu_token_aqui
Content-Type: application/json

{
  "titulo": "Nuevo título",
  "descripcion": "Nueva descripción",
  "completada": true
}
```

**Respuesta (200):**
```json
{
  "mensaje": "Tarea actualizada exitosamente"
}
```

#### 6. Eliminar Tarea

```bash
DELETE /tareas/1
Authorization: tu_token_aqui
```

**Respuesta (200):**
```json
{
  "mensaje": "Tarea eliminada exitosamente"
}
```

## ⌨️ Pruebas con cURL

### Ejemplo completo de flujo

```bash
# 1. Registrar un usuario
curl -X POST http://localhost:5000/registro \
  -H "Content-Type: application/json" \
  -d '{"usuario":"test","contraseña":"1234"}'

# 2. Iniciar sesión
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"usuario":"test","contraseña":"1234"}'

# Copiar el token recibido

# 3. Crear una tarea
curl -X POST http://localhost:5000/tareas \
  -H "Content-Type: application/json" \
  -H "Authorization: TU_TOKEN_AQUI" \
  -d '{"titulo":"Mi primera tarea","descripcion":"Probar la API"}'

# 4. Ver todas las tareas
curl -X GET http://localhost:5000/tareas \
  -H "Authorization: TU_TOKEN_AQUI"

# 5. Marcar como completada (suponiendo ID 1)
curl -X PUT http://localhost:5000/tareas/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: TU_TOKEN_AQUI" \
  -d '{"completada":true}'

# 6. Eliminar tarea
curl -X DELETE http://localhost:5000/tareas/1 \
  -H "Authorization: TU_TOKEN_AQUI"
```

## 🔒 Seguridad

### Hashing de Contraseñas

El sistema utiliza **SHA-256 con salt** para proteger las contraseñas:

1. **Salt único:** Cada usuario tiene un salt aleatorio de 64 caracteres
2. **Hash SHA-256:** La contraseña + salt se hashean usando SHA-256
3. **Almacenamiento:** Solo el hash y el salt se guardan en la base de datos

**¿Por qué hashear contraseñas?**

- ✅ **Protección ante brechas:** Si la base de datos es comprometida, los atacantes no pueden ver las contraseñas reales
- ✅ **Irreversibilidad:** Es computacionalmente imposible obtener la contraseña original del hash
- ✅ **Salt previene rainbow tables:** Cada usuario tiene un hash único incluso con la misma contraseña
- ✅ **Buenas prácticas:** Es un estándar de la industria nunca almacenar contraseñas en texto plano

**Ejemplo del proceso:**

```
Usuario ingresa: "miPassword123"
Sistema genera salt: "a1b2c3d4..." (64 caracteres aleatorios)
Combina: "miPassword123" + "a1b2c3d4..."
Hashea: SHA-256("miPassword123a1b2c3d4...") = "e5f9a2b8..."
Almacena en DB: hash="e5f9a2b8...", salt="a1b2c3d4..."
```

### Sistema de Tokens

- Tokens aleatorios de 64 caracteres hexadecimales
- Se generan al iniciar sesión
- Deben incluirse en el header `Authorization` de cada petición protegida
- En producción, se recomienda usar JWT con expiración

## 💾 Base de Datos

### Ventajas de usar SQLite en este proyecto

1. **✅ Sin configuración:** No requiere instalación ni configuración de servidor
2. **✅ Portabilidad:** La base de datos es un solo archivo, fácil de respaldar y mover
3. **✅ Suficiente para el proyecto:** Maneja perfectamente el volumen de datos esperado
4. **✅ ACID compliant:** Garantiza integridad de datos con transacciones
5. **✅ Sin dependencias:** Incluido en la biblioteca estándar de Python
6. **✅ Ideal para desarrollo:** Perfecta para prototipos y proyectos pequeños/medianos

### Esquema de Base de Datos

#### Tabla `usuarios`

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla `tareas`

```sql
CREATE TABLE tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    completada BOOLEAN DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

## 📸 Capturas de Pruebas

### 1. Servidor en Ejecución



### 2. Cliente - Registro de Usuario


### 3. Cliente - Inicio de Sesión


### 4. Cliente - Ver Tareas


## 🛠️ Tecnologías Utilizadas

- **Flask 3.0.0:** Framework web minimalista para Python
- **SQLite3:** Base de datos embebida
- **hashlib:** Librería estándar de Python para hashing (SHA-256)
- **secrets:** Generación de tokens criptográficamente seguros
- **requests:** Cliente HTTP para el cliente de consola

## 🔍 Estructura del Código

### servidor.py

- `init_db()`: Inicializa las tablas de la base de datos
- `hash_password()`: Hashea contraseñas con SHA-256 + salt
- `verify_password()`: Verifica contraseñas contra el hash almacenado
- `require_auth`: Decorador para proteger endpoints
- Endpoints REST completos con manejo de errores

### cliente.py

- Interfaz de consola interactiva
- Manejo de sesiones con tokens
- Validación de entrada de usuario
- Comunicación con la API usando requests

## 📝 Respuestas Conceptuales

### ¿Por qué hashear contraseñas?

Las contraseñas **nunca** deben almacenarse en texto plano porque:

1. **Protección ante brechas de seguridad:** Si un atacante accede a la base de datos, no puede leer las contraseñas directamente.

2. **Irreversibilidad:** Las funciones hash son unidireccionales. Es matemáticamente imposible obtener la contraseña original del hash.

3. **Responsabilidad legal y ética:** Los desarrolladores tienen la obligación de proteger los datos de los usuarios.

4. **Prevención de ataques en cadena:** Los usuarios a menudo reutilizan contraseñas. Protegerlas evita que un atacante acceda a otras cuentas del usuario.

5. **Cumplimiento de regulaciones:** La protección de datos sensibles es fundamental para cumplir con normativas y buenas prácticas de seguridad de la información.<img width="783" height="296" alt="image" src="https://github.com/user-attachments/assets/64ce1f84-9ccc-4819-a206-d0c81e5deb6d" />


**Salt adicional:**
- Previene ataques de rainbow tables (tablas precalculadas de hashes)
- Hace que usuarios con la misma contraseña tengan hashes diferentes
- Aumenta la complejidad de ataques de fuerza bruta

### Ventajas de usar SQLite en este proyecto

1. **Simplicidad de implementación:**
   - No requiere servidor de base de datos separado
   - Configuración cero
   - Incluido en Python por defecto

2. **Portabilidad:**
   - Base de datos en un solo archivo (`tasks.db`)
   - Fácil de respaldar, compartir y versionar
   - Compatible con múltiples plataformas

3. **Rendimiento adecuado:**
   - Excelente para aplicaciones pequeñas/medianas
   - Maneja miles de transacciones por segundo
   - Bajo consumo de recursos

4. **Integridad de datos:**
   - Soporta transacciones ACID
   - Foreign keys para relaciones entre tablas
   - Constraints para validación de datos

5. **Sin costo de infraestructura:**
   - No requiere hosting de base de datos
   - Ideal para desarrollo y prototipado
   - Fácil migración a bases de datos más robustas si el proyecto crece

6. **Facilidad de testing:**
   - Crear y destruir bases de datos de prueba es trivial
   - No contamina el entorno de producción

## 🚧 Mejoras Futuras

- [ ] Implementar JWT con expiración de tokens
- [ ] Agregar paginación en listado de tareas
- [ ] Implementar filtros y búsqueda de tareas
- [ ] Agregar categorías/etiquetas a las tareas
- [ ] Sistema de recordatorios
- [ ] Frontend web completo con React/Vue
- [ ] Despliegue en la nube (Heroku, Railway, etc.)
- [ ] Tests unitarios y de integración
- [ ] Documentación con Swagger/OpenAPI

## 📄 Licencia

Este proyecto es de código abierto y está disponible para fines educativos.

## 👨‍💻 Autor

Proyecto desarrollado en el marco de la Práctica Formativa Obligatoria N.º 2  
de la materia **Programación sobre Redes** del **IFTS N.º 29**.

El trabajo consiste en el desarrollo de un sistema de gestión de tareas  
con API y base de datos.

---

**¿Preguntas o problemas?** Crea un issue en el repositorio o contacta al autor.
