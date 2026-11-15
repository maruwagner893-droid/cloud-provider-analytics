
# Gobierno preliminar

## Controles iniciales
Los controles los aplicamos en cada capa del pipeline, pero no todos funcionan de la misma forma. Los registros que no cumplen una regla de rechazo van a Quarantine junto con el motivo, en la columna quarantine_reason. Los datos que llegan incompletos se completan y les dejamos una marca para saber cuáles fueron imputados. Ademas loos eventos duplicados y los que llegan tarde se eliminan.

Las reglas que aplicamos son las siguentes:
- Event_id no nulo: si un evento no tiene event_id va a Quarantine con el motivo event_id_nulo. En los datos no encontramos ninguno.
- Costo: los eventos con cost_usd_increment menor a -0,01 van a Quarantine con el motivo cost_usd_increment_menor_a_-0.01. Son 211 -- Eventos es decir el 0,49 %, quedando asi en Silver quedan 42.989.
- Unit: cuando  falta, decidimos completarlos según la métrica y lo marcamos con unit_imputed.Fueron 2.069 y en Silver no queda ninguna vacía.
- Duplicados: los sacamos en Bronze por event_id con un watermark de 10 minutos, y quedan 43.200 eventos.
- Billing: los credits nulos los tomamos como 0 y los marcamos con credits_imputed, las facturas con subtotal negativo las marcamos con is_credit  y las que tengan tasa de cambio nula o menor o igual a 0 van a Quarantine con el motivo exchange_rate_nula_o_no_positiva. No hubo ninguna, por lo cual las 240 facturas pasan a Silver.

Además hicimos las siguentes pruebas:
- Idempotencia: volvimos a ejecutar el proceso sin archivos nuevos y con un archivo repetido, donde bronze se mantuvo en 43.200 en los dos casos y silver en 42.989.
- Archivos desordenados: con los archivos tal como vienen en el dataset solo pasaron 733 de 43.200 eventos, es decir que se descartó el 98,3 % por tardíos. Por eso enviamos los eventos ordenados por timestamp.
- Datos tardíos: enviamos un evento con un timestamp anterior al watermark y Spark lo descartó, lo que se ve en la métrica numRowsDroppedByWatermark = 1

## Metadatos
A cada registro le agregamos columnas que indican de dónde viene y cuándo se procesó, para poder rastrearlo y controlarlo.

Metadatos de ingesta, que se agregan en Bronze a las cuatro fuentes que procesamos: los maestros customers_orgs , users  y billing_monthly , y los eventos de usage_events_stream :
- ingest_ts: fecha y hora en que el registro se cargó en Bronze.
- source_file: Es el nombre del archivo del que se leyó el registro. En los maestros es el CSV de Landing, pero en los eventos es el archivo del replay (part-*.json), porque los eventos se leen desde data/replay/usage_events_stream, donde se reescriben ordenados por timestamp.

Metadatos del esquema:
- schema_version: viene en cada evento e indica la versión del esquema. Los eventos de la versión 1 no traen carbon_kg, por lo cual queda nula en ellos. Ademas genai_tokens solo viene en los eventos de la versión 2 del servicio genai, por eso en el resto queda nula.
- 
Marcas de calidad, que se agregan en Silver:
- unit_imputed: Aca la unidad del evento se completó a partir de la métrica.
- value_missing: el evento no trae value.
- credits_imputed: en billing, teniamo que credits venía nulo y se tomó como 0.
- is_credit: en billing, la factura tiene subtotal negativo.

Metadatos de Quarantine:
- quarantine_reason: Es el  motivo por el que se rechazó el registro.
- quarantine_ts: fecha y hora en que el registro se envió a Quarantine.
## Linaje

## Responsabilidades

## Acceso

## Evidencias
