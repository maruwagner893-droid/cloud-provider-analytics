CREATE TABLE IF NOT EXISTS cloud_provider.org_daily_usage_by_service (
    org_id text,
    usage_date date,
    service text,
    daily_cost_usd double,
    requests bigint,
    cpu_hours double,
    storage_gb_hours double,
    genai_tokens bigint,
    carbon_kg double,
    n_events bigint,
    PRIMARY KEY ((org_id), usage_date, service)
) WITH CLUSTERING ORDER BY (usage_date ASC, service ASC);

CREATE TABLE IF NOT EXISTS cloud_provider.org_top_services_14d (
       org_id text,
       window_end date,
       cost_usd_14d double,
       service text,
       PRIMARY KEY ((org_id, window_end), cost_usd_14d, service)
   ) WITH CLUSTERING ORDER BY (cost_usd_14d DESC, service ASC);

-- Carga (se ejecuta desde el notebook con los datos de Gold, como sentencia preparada)
-- INSERT INTO cloud_provider.org_daily_usage_by_service
-- (org_id, usage_date, service, daily_cost_usd, requests, cpu_hours,
--  storage_gb_hours, genai_tokens, carbon_kg, n_events)
-- VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
-- INSERT INTO cloud_provider.org_top_services_14d (org_id, window_end, cost_usd_14d, service)
-- VALUES (?, ?, ?, ?);

-- Consulta 1: costos y requests diarios de una organización en un rango de fechas
SELECT usage_date, service, daily_cost_usd, requests
FROM cloud_provider.org_daily_usage_by_service
WHERE org_id = 'org_dbdw2pcn'
  AND usage_date >= '2025-07-01'
  AND usage_date <= '2025-07-14';

 -- Consulta 2: servicios que más costaron en los últimos 14 días de una organización
  SELECT service, cost_usd_14d
  FROM cloud_provider.org_top_services_14d
  WHERE org_id = 'org_dbdw2pcn'
    AND window_end = '2025-08-31'
  LIMIT 5;
