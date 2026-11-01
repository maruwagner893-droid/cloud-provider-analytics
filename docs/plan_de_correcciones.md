# Plan de correcciones de la primera entrega

 La primera entrega fue el 07/10/2026, donde cada corrección fue de la devolucion hecha de la misma:

###  Reproducibilidad
- Lo marcamos como 1
- Responsable: Mariana Wagner
- Fecha de cierre: 17/10 se corigio la rutas del notebook,  el 09/10 requirements, y el  30/10 Quickstart.
- Evidencia:
  - El notebook de exploración ya no usa rutas de Windows.
  - Está el archivo requirements.txt con las librerías.
  - Está el archivo .gitignore, que deja afuera los archivos secretos.
  - En el README se explican los pasos para ejecutar.
  - El notebook 02 se ejecuta en Colab por lo que al  clonar el repositorio funciona desde cero.
###  Data Lake: particiones, retención, metadatos y reglas de promoción
- Lo marcamos como priorodad 2
- Responsable: Mariana Wagner
- Fecha de cierre:  el 09/10  se corigio lo de retención y metadatos y el 20/10  lo de partición por year/month
- Evidencia:  Se encuentra en la  sección 7 del documento de diseño y evidence/02_decisiones/decisiones.md.

###  Decisiones de streaming con el comportamiento real
- Prioridad: Se considero prioridad 2
- Responsable: Mariana Wagner
- Fecha de cierre: 14/10
- Evidencia: en la sección 8.2, tambien en nota del watermark en decisiones.md y prueba con archivos desordenados en el notebook 02.

###  Diagrama con gobierno, metadatos, observabilidad y seguridad
- se considero prioridad 2
- Responsable: Mariana Wagner
- Fecha de cierre: 09/10
- Evidencia: en el diagrama de la sección 4 y en  docs/diagrama_arquitectura.md.

### Objetivos con números
- Se considero prioridad3
- Responsable: Mariana Wagner
- Fecha de cierre: 09/10
- Evidencia: sección 1 del documento de diseño.

### Justificación de volumen
- Lo consideramos prioridad 3
- Responsable: Mariana Wagner
- Fecha de cierre: 14/10
- Evidencia:  se encuentra en la sección 2 del documento de diseño.

###  Caso de MapReduce completo
- Se marco como priorodad 3
- Responsable: Mariana Wagner
- Fecha de cierre:  Fue el 13/10
- Evidencia: en la sección 9 con el caso billing_monthly.

### Registro formal de decisiones y evidencia estructurada
- Se considero como priorodad 3
- Responsable: Mariana Wagner
- Fecha de cierre: 09/10  fue de decisiones y registro de calidad y el  24/10  el de evidencia de Cassandra
- Evidencia:  dentro de la carpeta carpeta evidence/ (hallazgos, decisiones, registro de calidad, serving en Cassandra, pipeline Spark).


