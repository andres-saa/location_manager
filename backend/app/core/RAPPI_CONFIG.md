# Configuración de Rappi Cargo

Este archivo centraliza la configuración de los endpoints y tokens de Rappi Cargo para facilitar el cambio entre desarrollo y producción.

## Archivo de Configuración

La configuración está en `app/core/rappi_config.py` y se basa en la variable de entorno `RAPPI_ENV`.

## Variables de Entorno

En tu archivo `.env`, configura:

```env
# Ambiente de Rappi: 'dev' o 'prod'
RAPPI_ENV=dev

# Token de usuario para API de Rappi
RAPPI_USER_TOKEN=8f4e1480ebdafc50245cbb590bbc8411
```

## Cambiar a Producción

Para cambiar a producción, simplemente actualiza el `.env`:

```env
RAPPI_ENV=prod
RAPPI_USER_TOKEN=tu_token_de_produccion
```

Y actualiza la URL de producción en `app/core/rappi_config.py`:

```python
RAPPI_BASE_URLS = {
    'dev': 'https://microservices.dev.rappi.com',
    'prod': 'https://microservices.rappi.com'  # URL de producción real
}
```

## Endpoints Configurados

- **Picking Point (crear/actualizar/eliminar)**: `/api/cargo-api-gateway/picking-point`
- **Listar Picking Points**: `/api/cargo-api-gateway/picking-point/list`
- **Validar Orden**: `/api/cargo-api-gateway/v3/order-validate`

Todos los endpoints se construyen automáticamente según el ambiente configurado.
