# Plan de correcciones de la segunda entrega
La segunda entrega se realizo el 18/11/2026 y cada corrección sale de la devolución de ese día. 

### Ingesta desde los archivos originales
- Prioridad 1
- Responsable: Mariana Wagner
- Fecha de cierre: 23/11
-En la devolucion se marco que Bronze no leía los 120 archivos originales, sino un replay ordenado por timestamp. Eso evitaba el problema de los datos tardíos en vez de resolverlo.
- lo que decidmos hacer es : sacar el replay y Bronze lee directo los 120 archivos originales. Asi el watermark pasó a la hora de llegada en ingest_ts, y no se descarta ningún evento por su fecha, y Silver y Gold siguen calculando por la fecha del evento. Ademas dejamos en el notebook la prueba que lee los archivos originales con el watermark por fecha del evento, para mostrar por qué no lo usamos: con ese watermark se pierde alrededor del 98,3 % de los eventos.
- Evidencia:  se encuentra en la celdas 9, 10, 11 y 17 del notebook 02, donde se ve que Bronze tiene 43.200 eventos leídos en 12 micro-lotes desde los archivos originales.
