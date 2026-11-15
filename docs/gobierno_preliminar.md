
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
- Datos tardíos: enviamos un evento con un timestamp anterior al watermark y Spark lo descartó, lo que se ve en la métrica numRowsDroppedByWatermark = 1.
## Metadatos

## Linaje

## Responsabilidades

## Acceso

## Evidencias
