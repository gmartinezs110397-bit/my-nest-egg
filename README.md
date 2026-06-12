# My Nest Egg

App Streamlit independiente para planear pagos de tarjetas por quincena.

## Ejecutar local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Cloud

1. Crea un repo nuevo, separado de Plan de Choque. Nombre sugerido: `my-nest-egg`.
2. Sube estos archivos al repo.
3. En Streamlit Cloud, crea una app nueva apuntando a `app.py`.
4. En `Settings > Secrets`, agrega:

```toml
APP_PASSWORD = "tu-contrasena"
```

5. Comparte la URL pública solo con quien deba verla.

## Datos

La app guarda la información en `data/payment_data.json`.
También tiene export/import de respaldo JSON desde la pestaña `Datos`.

Nota: si la app queda pública sin contraseña, cualquier persona con el link podría verla.
