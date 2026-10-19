
# Hallazgos de calidad de datos
## customers_orgs:
Nulos en nps_score (13.75%), y un valor fuera de rango (101, cuando la escala NPS va de -100 a 100). La columna signup_date está guardada como texto en vez de datetime. Además, nps_score aparece también en nps_surveys, lo que puede generar inconsistencias si los valores no están sincronizados.

## users:
Nulos en last_login (17.38%). Las columnas created_at y last_login están guardadas como texto en vez de datetime.

## resources:

Nulos en tags_json (20.75%). La columna created_at está guardada como texto en vez de datetime.

## support_tickets:

Nulos en resolved_at (24%) y csat (25.4%). Las columnas created_at y resolved_at están guardadas como texto. La columna csat usa una escala 0-7 poco habitual que conviene confirmar con la fuente.

## marketing_touches:

Sin problemas de nulos, pero la columna timestamp está guardada como texto en vez de datetime.

## nps_surveys:

Nulos en nps_score (20.65%) y comment (10.87%). La columna survey_date está guardada como texto en vez de datetime.

## billing_monthly:

Nulos en credits (57.08%), y 13 facturas con subtotal negativo (el valor más bajo es -1671.83). Estos valores probablemente son créditos del proveedor de nube, como devoluciones o ajustes por compromisos de uso. Las facturas vienen en tres monedas (USD, ARS y EUR); la tabla incluye exchange_rate_to_usd para convertirlas, pero si no se aplica en la capa Silver las sumas quedan en monedas distintas y resultan incorrectas. La columna month está guardada como texto en vez de datetime.

## usage_events_stream:

Nulos en value (2.03%), unit (4.80%), carbon_kg (25%) y genai_tokens (92.75%); además costos negativos en cost_usd_increment. Los nulos de carbon_kg coinciden exactamente con los registros de schema_version = 1, lo que indica una evolución del esquema y no un error aleatorio. La columna value tiene tipo object en vez de numérico, lo que impide cálculos de consumo. La columna timestamp está guardada como texto en vez de datetime.


Se verificó tambien que ninguna de las tablas muestra filas duplicadas. Además, todas las tablas tienen columnas de fecha guardadas como texto. Los nulos de carbon_kg en usage_events_stream son parte del diseño por el cambio de schema_version = 1 a v2, no errores de carga.
