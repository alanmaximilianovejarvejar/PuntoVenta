# Punto de Venta Cauloti

Sistema POS offline-first para escritorio, construido con Django, SQLite y una interfaz integrada con templates y JavaScript local. Esta base esta pensada para negocios con conectividad limitada: todas las operaciones principales funcionan sin internet y los datos viven en una base SQLite local.

## Caracteristicas

- Autenticacion local con roles `admin` y `cajero`.
- CRUD de productos, categorias, codigos de barras, imagen opcional, costos, precios e inventario.
- Punto de venta rapido con busqueda por nombre/codigo, soporte para lector de codigo de barras, carrito dinamico, efectivo/tarjeta y cambio automatico.
- Registro de ventas con detalle, tickets imprimibles y PDF.
- Inventario con movimientos, ajustes manuales, descuento automatico y alertas de bajo stock.
- Dashboard con ventas diarias, semanales, mensuales, productos mas vendidos y graficas canvas locales.
- Exportacion JSON/CSV e importacion JSON para preparar sincronizacion futura.
- Wrapper Tauri preparado para empaquetar como app de escritorio con Django como sidecar.

## Requisitos

- Python 3.12+
- Windows, Linux o macOS
- Para empaquetar escritorio: Rust, Node.js y Tauri CLI

## Instalacion local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py collectstatic --noinput
python manage.py runserver 127.0.0.1:8000
```

Abre `http://127.0.0.1:8000`.

Usuarios de prueba:

- Admin: `admin` / `admin12345`
- Cajero: `cajero` / `cajero12345`

## Scripts rapidos

```powershell
.\scripts\bootstrap.ps1
.\scripts\run.ps1
```

`bootstrap.ps1` crea el entorno, instala dependencias, migra, carga semillas y recopila estaticos. `run.ps1` levanta el servidor local.

## Empaquetado como escritorio con Tauri

La carpeta `desktop/` contiene un proyecto Tauri v2 preparado para cargar el POS desde un servidor Django local ejecutado como sidecar. Tauri recomienda usar sidecars para incluir binarios externos como servidores Python empaquetados con PyInstaller.

1. Instala dependencias Python y prepara estaticos:

```powershell
.\scripts\bootstrap.ps1
```

2. Construye el sidecar Django con PyInstaller:

```powershell
.\scripts\build_sidecar.ps1
```

3. Instala dependencias de Tauri y compila:

```powershell
cd desktop
npm install
npm run tauri build
```

El instalador final se genera dentro de `desktop/src-tauri/target/release/bundle`.

Notas:

- La configuracion de Tauri usa `externalBin` para incluir el sidecar.
- En Windows, el script renombra el binario con el target triple requerido por Tauri.
- La app final sigue usando SQLite local en el directorio de datos configurado por el sidecar.

## Exportacion e importacion

Desde la interfaz:

- `Sincronizacion > Exportar JSON`
- `Sincronizacion > Exportar ventas CSV`
- `Sincronizacion > Importar JSON`

Tambien por CLI:

```powershell
python manage.py export_data --format json --output exports/cauloti-export.json
python manage.py export_data --format csv --output exports/sales.csv
python manage.py import_data exports/cauloti-export.json
```

## Seguridad incluida

- CSRF en formularios y acciones POST.
- Login requerido en vistas de negocio.
- Permisos por rol usando grupos Django.
- Validacion de precios, stock, codigos unicos y pagos.
- Transacciones atomicas al registrar ventas y cancelar ventas.
- Snapshot de producto/precio en cada venta para auditoria.
- Secret key por variable de entorno en produccion.

## Estructura

```text
cauloti_pos/        Configuracion Django
core/               Dashboard, sync, tickets y utilidades compartidas
users/              Roles, permisos y autenticacion
products/           Categorias, productos, formularios y repositorios
sales/              POS, ventas, tickets y servicios de venta
inventory/          Movimientos, ajustes y alertas
templates/          Layout y pantallas
static/             CSS/JS locales
desktop/            Wrapper Tauri v2
scripts/            Bootstrap, ejecucion y empaquetado
exports/            Salidas JSON/CSV locales
media/              Imagenes de productos/logo
```

