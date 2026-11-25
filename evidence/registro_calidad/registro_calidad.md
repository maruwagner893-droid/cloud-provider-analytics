# Registro de calidad de datos

En la etapa 2 implementamos la limpieza en Silver de dos tablas: usage_events_stream y billing_monthly, y para la entrega final sumamos support_tickets. Para las demás tablas como: customers_orgs, users, resources, marketing_touches y nps_surveys dejamos definidas las reglas de calidad que se van a aplicar en Silver.

## customers_orgs
Los nulos en nps_score (13.75%) se mantienen como nulos en Silver para no afectar el promedio. El valor 101, que está fuera del rango válido de NPS (-100 a 100), se envía a Quarantine. La columna signup_date se convierte a datetime en Bronze.

## users
el campo last_login tiene un 17.38% de nulos,  por lo que quedan como nulos en Silver. Las columnas created_at y last_login se castean a datetime en Bronze.

## resources
 el campo tags_json tiene un 20.75% de nulos, se conservan en Silver. La columna created_at se castea a datetime en Bronze.

## support_tickets
Los nulos en resolved_at son del 24% y  se mantienen como nulos porque indican tickets que todavía están abiertos, en Silver se marcan con is_open. Los nulos en csat son del 25.4% y se mantienen como nulos en Silver, asi no cambian el promedio csat_avg de Gold. Las columnas created_at y resolved_at se convierte a datetime en Bronze. Los tickets sin ticket_id o sin created_at se envían a Quarantine, en los datos actuales no hay ninguno, y los 1000 tickets pasan a Silver. Ademas en Silver se agregan los datos de la organización con un join a customers_orgs. Encontramos 172 tickets con csat pero sin resolved_at, y 186 tickets cerrados sin csat, estos se dejan como vienen porque no hay una regla definida para esos casos. El csat va de 0 a 7, donde hay un solo ticket con 7 y como la escala no está confirmada no se aplica una regla de rango.

## marketing_touches
la tabla no tiene problemas de nulos. ademas la columna timestamp se castea a datetime en Bronze.

## nps_surveys
Los nulos en nps_score (20.65%) y comment (10.87%) se mantienen como nulos en Silver. La columna survey_date se convierte a datetime en Bronze.

## billing_monthly
Los nulos en credits  que son el 57.08% se tratan como 0 en Silver y se marcan con credits_imputed para saber cuáles se completaron. Las 13 facturas con subtotal negativo, donde la más baja es de -1671.83, se mantienen y se marcan con is_credit, porque probablemente son créditos del proveedor y no errores. Todas las facturas se normalizan a USD en la columna net_usd, calculada como: (subtotal - credits) × exchange_rate_to_usd, incluidas las que ya vienen en USD, debido a que su tasa no es exactamente 1.0. Las facturas con exchange_rate_to_usd nulo o menor o igual a cero se envían a Quarantine; en los datos actuales no hay ninguna, y las 240 facturas pasan a Silver. La columna month se convierte a datetime en Bronze.

## usage_events_stream
Los nulos en carbon_kg los cuales son el 25% se mantienen porque corresponden exactamente a los registros de schema_version = 1 y no son errores de carga. Los nulos en genai_tokens que son el 92.75% también se mantienen como nulos en Silver. Los valores de cost_usd_increment menores a -0,01 se envían a Quarantine como anomalías. La columna value se transforma a tipo numérico en Bronze. La columna timestamp se convierte a datetime en Bronze.Los nulos en value (2.03%) se mantienen como nulos en Silver. Los nulos en unit (4.80%) se completan según la métrica del evento y se marcan con unit_imputed.
