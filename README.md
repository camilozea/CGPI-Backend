# CGPI - Backend

## Control de Gestión de Punto de Inventario

API backend para el sistema de control de inventario, ventas, reparaciones y cotizaciones. Desarrollada con FastAPI y SQLAlchemy asíncrono.

---

## Descripción

CGPI es un sistema integral de gestión para negocios que permite administrar productos, registrar ventas, gestionar reparaciones, crear cotizaciones y generar reportes detallados. El sistema soporta múltiples negocios con usuarios asignados y roles diferenciados.

### Funcionalidades principales

- **Gestión de productos** con precios por mayoreo y menudeo
- **Registro de ventas** con seguimiento de stock automático
- **Devolución de productos** con estados de seguimiento
- **Control de inventario** con historial de movimientos
- **Gestión de reparaciones** con seguimiento de estados
- **Creación de cotizaciones** con items y validez configurable
- **Reportes de rendimiento** por vendedor y metas diarias
- **Gestión de múltiples negocios** con subcategorías
- **Sistema de usuarios** con roles y permisos
- **Registro de actividad** (audit log)
- **Exportación de datos** en formato CSV

---

## Tecnologías

| Componente | Tecnología |
|------------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy (async) |
| Base de datos | SQLite + aiosqlite |
| Validación | Pydantic v2 |
| Autenticación | JWT (python-jose) |
| Servidor | Uvicorn |

---

## Estructura del proyecto

```
CGPI-Backend/
├── .env                    # Variables de entorno
├── .gitignore
├── cgpi.db                 # Base de datos SQLite
├── requirements.txt        # Dependencias
├── venv/                   # Entorno virtual
└── app/
    ├── __init__.py
    ├── main.py             # Punto de entrada de la aplicación
    ├── config.py           # Configuración (Settings)
    ├── database.py         # Conexión a BD y migraciones
    ├── dependencies.py     # Dependencias de autenticación y roles
    ├── models/             # Modelos de SQLAlchemy
    │   ├── user.py
    │   ├── product.py
    │   ├── sale.py
    │   ├── return_item.py
    │   ├── inventory.py
    │   ├── business.py
    │   ├── daily_goal.py
    │   ├── activity_log.py
    │   ├── repair.py
    │   └── quote.py
    ├── schemas/            # Schemas de Pydantic
    │   ├── user.py
    │   ├── product.py
    │   ├── sale.py
    │   ├── return_item.py
    │   ├── inventory.py
    │   ├── business.py
    │   ├── repair.py
    │   ├── quote.py
    │   └── types.py
    ├── routers/            # Endpoints de la API
    │   ├── auth.py
    │   ├── products.py
    │   ├── sales.py
    │   ├── returns.py
    │   ├── inventory.py
    │   ├── admin.py
    │   ├── admin_businesses.py
    │   ├── business_settings.py
    │   ├── reports.py
    │   ├── repairs.py
    │   └── quotes.py
    └── services/
        └── activity.py     # Servicio de registro de actividad
```

---

## Instalación

### Requisitos previos

- Python 3.10 o superior
- pip

### Pasos

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd CGPI-Backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (opcional)
# Editar el archivo .env con tus valores

# Ejecutar el servidor
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://127.0.0.1:8000`

---

## Variables de entorno

Archivo `.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./cgpi.db
SECRET_KEY=cgpi-secret-key-change-in-production-abc123xyz
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de conexión a la base de datos | `sqlite+aiosqlite:///./cgpi.db` |
| `SECRET_KEY` | Clave secreta para firmar tokens JWT | `cgpi-secret-key-change-in-production-abc123xyz` |
| `ALGORITHM` | Algoritmo de encriptación JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token en minutos | `1440` (24 horas) |

> **Nota**: En producción, cambia `SECRET_KEY` por una clave segura y aleatoria.

---

## Base de datos

### Modelos

#### Users (Usuarios)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `name` | String(100) | Nombre |
| `apellido` | String(100) | Apellido |
| `correo` | String(150) | Correo electrónico (único) |
| `usuario` | String(80) | Nombre de usuario (único) |
| `contrasena` | String(255) | Contraseña hasheada con PBKDF2-SHA256 |
| `role` | String(20) | Rol: `admin`, `propietario`, `vendedor`, `reparador` |
| `active` | Boolean | Estado de la cuenta |
| `business_id` | Integer (FK) | ID del negocio asociado |
| `created_at` | DateTime | Fecha de creación |

#### Products (Productos)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `name_product` | String(200) | Nombre del producto |
| `Marca` | String(100) | Marca |
| `Tipo` | String(50) | Tipo/categoría |
| `Description` | String(500) | Descripción |
| `Price_mayor` | Float | Precio de mayoreo |
| `Price_cliente` | Float | Precio al cliente (menudeo) |
| `cantidad` | Integer | Stock disponible |

#### Sales (Ventas)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `name_product` | String(200) | Nombre del producto vendido |
| `date` | Date | Fecha de la venta |
| `prise` | Float | Precio de venta |
| `name_cliente` | String(200) | Nombre del cliente |
| `documento` | String(50) | Documento del cliente |
| `discount_prise` | Float | Descuento aplicado |
| `user_id` | Integer | ID del vendedor |

#### Returns (Devoluciones)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `producto` | String(200) | Nombre del producto |
| `cliente` | String(200) | Nombre del cliente |
| `fecha` | Date | Fecha de la devolución |
| `cantidad` | Integer | Cantidad devuelta |
| `motivo` | String(500) | Motivo de la devolución |
| `estado` | String(20) | Estado: `pendiente`, `aprobada`, `rechazada` |
| `user_id` | Integer | ID del usuario que registró |

#### Inventory (Inventario)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `fecha` | Date | Fecha del movimiento |
| `nombre` | String(200) | Nombre del producto |
| `precio` | Float | Precio |
| `cantidad` | Integer | Cantidad (positiva=entrada, negativa=salida) |
| `pago` | String(50) | Tipo: `Entrada`, `Venta` |

#### Businesses (Negocios)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `name` | String(200) | Nombre del negocio (único) |
| `description` | Text | Descripción |
| `address` | String(300) | Dirección |
| `phone` | String(50) | Teléfono |
| `email` | String(150) | Correo electrónico |
| `profit_margin` | Integer | Margen de ganancia (%) - default: 30 |
| `type` | String(20) | Tipo: `ventas` o `reparacion` |
| `subcategories` | Text | Lista de subcategorías (JSON) |
| `created_at` | DateTime | Fecha de creación |

**Subcategorías de ventas:** ropa, calzado, electronica, electrodomesticos, tecnologia_celulares, tecnologia_computo, tecnologia_tablets, hogar, juguetes, deportes, alimentos, belleza, herramientas, mascotas, libros, automotriz, instrumentos_musicales, otros

**Subcategorías de reparación:** tecnologia_celulares, tecnologia_computo, tecnologia_tablets, electrodomesticos, vehiculos_motos, vehiculos_carros, vehiculos_bicicletas, herramientas, audiovisual, climatizacion, joyeria_relojes, instrumentos_musicales, hogar_muebles, otros

#### Repairs (Reparaciones)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `auto` | String(200) | Vehículo/equipo a reparar |
| `marca` | String(200) | Marca |
| `modelo` | String(100) | Modelo |
| `nombres` | String(200) | Nombres del cliente |
| `apellidos` | String(200) | Apellidos del cliente |
| `tipo_documento` | String(20) | Tipo de documento (default: `CC`) |
| `numero_documento` | String(50) | Número de documento |
| `tipo_reparacion` | String(200) | Tipo de reparación |
| `descripcion` | Text | Descripción del problema |
| `fotos` | Text | URLs de fotos |
| `costo` | Float | Costo de la reparación |
| `metodo_pago` | String(50) | Método de pago |
| `fecha_entrega` | Date | Fecha de entrega estimada |
| `estado` | String(30) | Estado: `pendiente`, `en_proceso`, `completado`, `entregado` |
| `created_at` | DateTime | Fecha de creación |
| `user_id` | Integer | ID del usuario |

#### Repair Parts (Repuestos)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `nombre` | String(200) | Nombre del repuesto |
| `cantidad` | Integer | Stock disponible |
| `precio_costo` | Float | Precio de compra |
| `precio_venta` | Float | Precio de venta |
| `proveedor` | String(200) | Proveedor |
| `created_at` | DateTime | Fecha de creación |
| `user_id` | Integer | ID del usuario |

#### Quotes (Cotizaciones)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `auto` | String(200) | Vehículo/equipo |
| `marca` | String(200) | Marca |
| `modelo` | String(100) | Modelo |
| `nombres` | String(200) | Nombres del cliente |
| `apellidos` | String(200) | Apellidos del cliente |
| `tipo_documento` | String(20) | Tipo de documento (default: `CC`) |
| `numero_documento` | String(50) | Número de documento |
| `tipo_reparacion` | String(200) | Tipo de reparación |
| `descripcion` | Text | Descripción |
| `items` | Text | Items de la cotización (JSON) |
| `total` | Float | Total de la cotización |
| `validez_dias` | Integer | Días de validez (default: 15) |
| `notas` | Text | Notas adicionales |
| `estado` | String(30) | Estado: `pendiente`, `aprobada`, `rechazada` |
| `created_at` | DateTime | Fecha de creación |
| `user_id` | Integer | ID del usuario |

#### Daily Goals (Metas Diarias)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `goal` | Float | Meta de ventas diaria |
| `date` | Date | Fecha |
| `business_id` | Integer (FK) | ID del negocio |

#### Activity Logs (Registro de actividad)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único |
| `user_id` | Integer | ID del usuario |
| `user_name` | String(200) | Nombre del usuario |
| `action` | String(50) | Acción realizada |
| `entity` | String(50) | Entidad afectada |
| `entity_id` | Integer | ID de la entidad |
| `detail` | Text | Detalle de la acción |
| `created_at` | DateTime | Fecha y hora |

---

## Roles de usuario

| Rol | Permisos |
|-----|----------|
| `admin` | Acceso total al sistema, gestión de usuarios, negocios, productos, ventas y reportes |
| `propietario` | Gestión de su negocio, productos, ventas, reportes y ajustes de negocio |
| `vendedor` | Registro de ventas y devoluciones |
| `reparador` | Gestión de reparaciones y repuestos |

> El primer usuario registrado se asigna automáticamente como `admin`.

---

## API Endpoints

### Autenticación (`/auth`)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Registrar nuevo usuario | No |
| POST | `/auth/login` | Iniciar sesión | No |
| GET | `/auth/me` | Obtener usuario actual | Sí |
| GET | `/auth/my-business` | Obtener negocio del usuario | Sí |

### Productos (`/products`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/products/` | Listar productos | Sí | Cualquier usuario |
| GET | `/products/{id}` | Obtener producto por ID | Sí | Cualquier usuario |
| POST | `/products/` | Crear producto | Sí | admin, propietario |
| PUT | `/products/{id}` | Actualizar producto | Sí | admin, propietario |
| DELETE | `/products/{id}` | Eliminar producto | Sí | admin, propietario |

### Ventas (`/sales`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/sales/` | Listar ventas | Sí | Cualquier usuario |
| GET | `/sales/{id}` | Obtener venta por ID | Sí | Cualquier usuario |
| POST | `/sales/` | Registrar venta | Sí | admin, propietario, vendedor |
| PUT | `/sales/{id}` | Actualizar venta | Sí | admin, propietario |
| DELETE | `/sales/{id}` | Eliminar venta | Sí | admin, propietario |
| GET | `/sales/{id}/invoice` | Generar factura | Sí | Cualquier usuario |

### Devoluciones (`/returns`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/returns/` | Listar devoluciones | Sí | Cualquier usuario |
| GET | `/returns/{id}` | Obtener devolución por ID | Sí | Cualquier usuario |
| POST | `/returns/` | Registrar devolución | Sí | admin, propietario, vendedor |
| PUT | `/returns/{id}` | Actualizar devolución | Sí | admin, propietario |
| DELETE | `/returns/{id}` | Eliminar devolución | Sí | admin, propietario |
| GET | `/returns/inventory/summary` | Resumen de devoluciones | Sí | Cualquier usuario |

### Inventario (`/inventory`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/inventory/` | Listar movimientos | Sí | Cualquier usuario |
| GET | `/inventory/stock` | Obtener stock actual | Sí | Cualquier usuario |
| GET | `/inventory/{id}` | Obtener movimiento por ID | Sí | Cualquier usuario |
| POST | `/inventory/` | Registrar movimiento | Sí | admin, propietario |
| PUT | `/inventory/{id}` | Actualizar movimiento | Sí | admin, propietario |
| DELETE | `/inventory/{id}` | Eliminar movimiento | Sí | admin, propietario |

### Reparaciones (`/repairs`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/repairs/` | Listar reparaciones | Sí | Cualquier usuario |
| POST | `/repairs/` | Crear reparación | Sí | Cualquier usuario |
| PUT | `/repairs/{id}` | Actualizar reparación | Sí | Cualquier usuario |
| DELETE | `/repairs/{id}` | Eliminar reparación | Sí | Cualquier usuario |
| GET | `/repairs/report` | Reporte de reparaciones | Sí | Cualquier usuario |
| GET | `/repairs/{id}/invoice` | Generar factura | Sí | Cualquier usuario |

### Repuestos (`/repairs/parts`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/repairs/parts` | Listar repuestos | Sí | Cualquier usuario |
| POST | `/repairs/parts` | Crear repuesto | Sí | Cualquier usuario |
| PUT | `/repairs/parts/{id}` | Actualizar repuesto | Sí | Cualquier usuario |
| DELETE | `/repairs/parts/{id}` | Eliminar repuesto | Sí | Cualquier usuario |

### Cotizaciones (`/quotes`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/quotes/` | Listar cotizaciones | Sí | Cualquier usuario |
| POST | `/quotes/` | Crear cotización | Sí | Cualquier usuario |
| PUT | `/quotes/{id}` | Actualizar cotización | Sí | Cualquier usuario |
| DELETE | `/quotes/{id}` | Eliminar cotización | Sí | Cualquier usuario |
| GET | `/quotes/{id}/invoice` | Generar factura | Sí | Cualquier usuario |

### Reportes (`/reports`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/reports/seller-performance` | Rendimiento por vendedor | Sí | Cualquier usuario |
| GET | `/reports/daily-goal` | Obtener meta diaria | Sí | Cualquier usuario |
| PUT | `/reports/daily-goal` | Establecer meta diaria | Sí | admin, propietario |

### Administración (`/admin`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| POST | `/admin/users` | Crear usuario | Sí | admin |
| GET | `/admin/users` | Listar usuarios | Sí | admin |
| GET | `/admin/users/{id}` | Obtener usuario por ID | Sí | admin |
| PUT | `/admin/users/{id}` | Actualizar usuario | Sí | admin |
| DELETE | `/admin/users/{id}` | Eliminar usuario | Sí | admin |
| GET | `/admin/stats` | Estadísticas generales | Sí | admin |
| GET | `/admin/activity` | Registro de actividad | Sí | admin |
| GET | `/admin/export/users` | Exportar usuarios CSV | Sí | admin |
| GET | `/admin/export/products` | Exportar productos CSV | Sí | admin |
| GET | `/admin/health` | Estado del sistema | Sí | admin |

### Gestión de Negocios (`/admin/businesses`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| POST | `/admin/businesses` | Crear negocio | Sí | admin |
| GET | `/admin/businesses` | Listar negocios | Sí | admin |
| GET | `/admin/businesses/summary` | Resumen de negocios | Sí | admin |
| GET | `/admin/businesses/{id}` | Obtener negocio por ID | Sí | admin |
| PUT | `/admin/businesses/{id}` | Actualizar negocio | Sí | admin |
| DELETE | `/admin/businesses/{id}` | Eliminar negocio | Sí | admin |
| GET | `/admin/businesses/{id}/users` | Usuarios del negocio | Sí | admin |

### Ajustes de Negocio (`/business`)

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| GET | `/business/settings` | Obtener ajustes del negocio | Sí | admin, propietario |
| PUT | `/business/settings` | Actualizar ajustes del negocio | Sí | admin, propietario |

---

## Documentación interactiva

Una vez ejecutado el servidor, la documentación Swagger está disponible en:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## Autenticación

El sistema utiliza tokens JWT para la autenticación. Para acceder a los endpoints protegidos:

1. Registrar un usuario con `POST /auth/register`
2. Iniciar sesión con `POST /auth/login` para obtener el token
3. Incluir el token en el header `Authorization: Bearer <token>`

---

## Desarrollo

```bash
# Ejecutar con auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ejecutar en producción
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Licencia

Proyecto privado - Todos los derechos reservados.
