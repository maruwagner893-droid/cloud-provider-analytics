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

CREATE TABLE IF NOT EXISTS cloud_provider.tickets_by_org_date (
    org_id text,
    severity text,
    ticket_date date,
    n_tickets bigint,
    n_sla_breached bigint,
    sla_breach_rate double,
    csat_avg double,
    n_open bigint,
    PRIMARY KEY ((org_id, severity), ticket_date)
) WITH CLUSTERING ORDER BY (ticket_date DESC);

CREATE TABLE IF NOT EXISTS cloud_provider.revenue_by_org_month (
    org_id text,
    month date,
    currency text,
    subtotal_usd double,
    credits_usd double,
    taxes_usd double,
    revenue_usd double,
    exchange_rate_to_usd double,
    n_facturas int,
    PRIMARY KEY ((org_id), month)
) WITH CLUSTERING ORDER BY (month ASC);

CREATE TABLE IF NOT EXISTS cloud_provider.genai_tokens_by_org_date (
    org_id text,
    usage_date date,
    genai_tokens bigint,
    cost_usd double,
    n_events bigint,
    PRIMARY KEY ((org_id), usage_date)
) WITH CLUSTERING ORDER BY (usage_date ASC);

-- Carga (se ejecuta desde el notebook con los datos de Gold, como sentencia preparada)
-- INSERT INTO cloud_provider.org_daily_usage_by_service
-- (org_id, usage_date, service, daily_cost_usd, requests, cpu_hours,
--  storage_gb_hours, genai_tokens, carbon_kg, n_events)
-- VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
-- INSERT INTO cloud_provider.org_top_services_14d (org_id, window_end, cost_usd_14d, service)
-- VALUES (?, ?, ?, ?);
-- INSERT INTO cloud_provider.tickets_by_org_date
-- (org_id, severity, ticket_date, n_tickets, n_sla_breached, sla_breach_rate, csat_avg, n_open)
-- VALUES (?, ?, ?, ?, ?, ?, ?, ?);
-- INSERT INTO cloud_provider.revenue_by_org_month
-- (org_id, month, currency, subtotal_usd, credits_usd, taxes_usd, revenue_usd, exchange_rate_to_usd, n_facturas)
-- VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
-- INSERT INTO cloud_provider.genai_tokens_by_org_date (org_id, usage_date, genai_tokens, cost_usd, n_events)
-- VALUES (?, ?, ?, ?, ?);

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

-- Consulta 3: tickets críticos y tasa de SLA breach por día en los últimos 30 días de una organización
SELECT ticket_date, n_tickets, n_sla_breached, sla_breach_rate, csat_avg, n_open
FROM cloud_provider.tickets_by_org_date
WHERE org_id = 'org_w3zp08j3'
  AND severity = 'critical'
  AND ticket_date >= '2025-08-02'
  AND ticket_date <= '2025-08-31';

-- Consulta 4: revenue mensual de una organización, con créditos e impuestos, en USD
SELECT month, currency, subtotal_usd, credits_usd, taxes_usd, exchange_rate_to_usd, revenue_usd
FROM cloud_provider.revenue_by_org_month
WHERE org_id = 'org_xaji0y6d';

-- Consulta 5: tokens GenAI y costo estimado por día de una organización
SELECT usage_date, genai_tokens, cost_usd, n_events
FROM cloud_provider.genai_tokens_by_org_date
WHERE org_id = 'org_pbhsahxt'
  AND usage_date >= '2025-08-18'
  AND usage_date <= '2025-08-31';
