# Registro de calidad de datos

En la etapa 2 del proyecto implemetamos la limpieza de usage_events_stream. Ppr que para las demás tablas este registro describe las reglas definidas: customers_orgs, users y billing_monthly ya están tipificadas en Bronze, y la limpieza en Silver, junto con resources, support_tickets, marketing_touches y nps_surveys, queda para la entrega final.

## customers_orgs
Los nulos en nps_score (13.75%) se mantienen como nulos en Silver para no afectar el promedio. El valor 101, que está fuera del rango válido de NPS (-100 a 100), se envía a Quarantine. La columna signup_date se convierte a datetime en Bronze.

## users
el campo last_login tiene un 17.38% de nulos,  por lo que quedan como nulos en Silver. Las columnas created_at y last_login se castean a datetime en Bronze.

## resources
 el campo tags_json tiene un 20.75% de nulos, se conservan en Silver. La columna created_at se castea a datetime en Bronze.

## support_tickets
Los nulos en resolved_at son del 24% y  se mantienen como nulos porque indican tickets que todavía están abiertos. Los nulos en csat son del 25.4% y se mantienen como nulos en Silver. Las columnas created_at y resolved_at se convierte a datetime en Bronze.

## marketing_touches
la tabla no tiene problemas de nulos. ademas la columna timestamp se castea a datetime en Bronze.

## nps_surveys
Los nulos en nps_score (20.65%) y comment (10.87%) se mantienen como nulos en Silver. La columna survey_date se convierte a datetime en Bronze.

## billing_monthly
Los nulos en credits (57.08%) se tratan como 0 en Silver, previa confirmación con FinOps. Las 13 facturas con subtotal negativo  donde la más baja es de -1671.83, se mantienen y se marcan como créditos, porque probablemente son créditos del proveedor y no errores. Todas las facturas se normalizan a USD multiplicando el subtotal por exchange_rate_to_usd, incluidas las que ya vienen en USD, porque su tasa no es exactamente 1.0. La columna month se convierte a datetime en Bronze.

## usage_events_stream
Los nulos en carbon_kg (25%) se mantienen porque corresponden exactamente a los registros de schema_version = 1 y no son errores de carga. Los nulos en genai_tokens (92.75%) también se mantienen como nulos en Silver. Los valores de cost_usd_increment menores a -0,01 se envían a Quarantine como anomalías. La columna value se transforma a tipo numérico en Bronze. La columna timestamp se convierte a datetime en Bronze.Los nulos en value (2.03%) se mantienen como nulos en Silver. Los nulos en unit (4.80%) se completan según la métrica del evento y se marcan con unit_imputed.
