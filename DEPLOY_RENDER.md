# Deploy demo en Render

Este deploy es para mostrar el POS en una URL publica. El modo recomendado para uso real offline sigue siendo local/escritorio.

## Opcion recomendada: Blueprint

1. Sube este proyecto a GitHub.
2. En Render entra a **Blueprints**.
3. Selecciona **New Blueprint Instance**.
4. Conecta el repositorio.
5. Render detectara `render.yaml`.
6. Aplica el Blueprint.

Render creara:

- Un web service Python.
- Una base Postgres.
- Variables de entorno.
- Build con `collectstatic`.
- Migraciones y seed demo antes de iniciar.

Cuando termine, Render te dara una URL como:

```text
https://punto-de-venta-cauloti.onrender.com
```

Usuarios demo:

```text
admin / admin12345
cajero / cajero12345
```

## Opcion manual

1. Crea una base PostgreSQL en Render.
2. Crea un Web Service desde tu repo.
3. Usa estos comandos:

Build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Pre-deploy command:

```bash
python manage.py migrate && python manage.py seed_demo
```

Start command:

```bash
gunicorn cauloti_pos.wsgi:application --bind 0.0.0.0:$PORT
```

Variables:

```text
PYTHON_VERSION=3.12.3
CAULOTI_DEBUG=0
CAULOTI_ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CAULOTI_CSRF_TRUSTED_ORIGINS=https://*.onrender.com
CAULOTI_SECRET_KEY=<genera una clave segura>
DATABASE_URL=<internal database url de Render Postgres>
```

## Nota importante

Este deploy publico no es offline-first. Es solo para demo remota. Para una tienda con internet limitado, usa la app local o empaquetada con Tauri.

