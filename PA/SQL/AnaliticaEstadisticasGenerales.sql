CREATE PROC pa_Analitica_Estadisticas_Generales
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- CTE 1: Normalizamos estados, determinamos el segmento (Comedor vs Evento) y contamos artículos.
    WITH CTE_OrdenesBase AS (
        SELECT 
            o.IdOrdenes, 
            o.CostoTotal,
            CASE 
                WHEN o.Estado IN ('ANULADO', 'ANULADA', 'CANCELADO', 'CANCELADA') THEN 'ANULADA'
                WHEN o.Estado = 'PENDIENTE' THEN 'PENDIENTE'
                ELSE 'COMPLETADA'
            END AS EstadoLimpio,
            CASE 
                WHEN po.IdPedido IS NOT NULL THEN 'EVENTO/CONTRATO'
                ELSE 'COMEDOR' 
            END AS SegmentoNegocio,
            CAST(o.Fecha AS DATE) AS FechaDia,
            ISNULL((SELECT SUM(CantidadPlatillo) FROM detallesordenes WHERE IdOrdenes = o.IdOrdenes), 0) AS CantidadArticulos
        FROM ordenes o
        LEFT JOIN pedidosordenes po ON o.IdOrdenes = po.IdOrdenes
        WHERE (@FechaInicio IS NULL OR o.Fecha >= @FechaInicio)
          AND (@FechaFin IS NULL OR o.Fecha <= @FechaFin)
    ),
    
    -- CTE 2: Para calcular el "Promedio Diario", debemos saber cuántos días efectivos trabajó *cada segmento*.
    CTE_DiasActivos AS (
        SELECT 
            SegmentoNegocio, 
            COUNT(DISTINCT FechaDia) AS TotalDiasLaborados
        FROM CTE_OrdenesBase
        WHERE EstadoLimpio = 'COMPLETADA'
        GROUP BY SegmentoNegocio
    )
    
    -- SELECT FINAL: Agrupamos todo por el SegmentoNegocio.
    SELECT 
        ob.SegmentoNegocio,
        
        -- ================= VOLUMEN DE VENTAS =================
        COUNT(ob.IdOrdenes) AS TransaccionesTotales,
        SUM(CASE WHEN ob.EstadoLimpio = 'COMPLETADA' THEN 1 ELSE 0 END) AS VentasExitosas,
        SUM(CASE WHEN ob.EstadoLimpio = 'ANULADA' THEN 1 ELSE 0 END) AS VentasAnuladas_Reembolsadas,
        
        -- ================= PROMEDIOS DE COSTOS =================
        ISNULL(AVG(CASE WHEN ob.EstadoLimpio = 'COMPLETADA' THEN ob.CostoTotal ELSE NULL END), 0) AS TicketPromedio,
        ISNULL(MAX(CASE WHEN ob.EstadoLimpio = 'COMPLETADA' THEN ob.CostoTotal ELSE NULL END), 0) AS VentaMasAlta,
        ISNULL(MIN(CASE WHEN ob.EstadoLimpio = 'COMPLETADA' AND ob.CostoTotal > 0 THEN ob.CostoTotal ELSE NULL END), 0) AS VentaMasBaja,
        
        -- ================= PROMEDIOS DE CONSUMO =================
        -- ¿Cuántos platos se sirven por ticket en este segmento?
        ISNULL(AVG(CASE WHEN ob.EstadoLimpio = 'COMPLETADA' THEN CAST(ob.CantidadArticulos AS DECIMAL(10,2)) ELSE NULL END), 0) AS PromedioPlatillosPorOrden,
        
        -- ================= PROMEDIOS DIARIOS =================
        -- (Volumen completado / Días laborados por el segmento)
        ISNULL(
            CAST(SUM(CASE WHEN ob.EstadoLimpio = 'COMPLETADA' THEN 1 ELSE 0 END) AS DECIMAL(10,2)) / 
            NULLIF(CAST(MAX(da.TotalDiasLaborados) AS DECIMAL(10,2)), 0)
        , 0) AS PromedioOrdenesPorDia,
        
        ISNULL(
            SUM(CASE WHEN ob.EstadoLimpio = 'COMPLETADA' THEN ob.CostoTotal ELSE 0 END) / 
            NULLIF(CAST(MAX(da.TotalDiasLaborados) AS DECIMAL(10,2)), 0)
        , 0) AS PromedioIngresoPorDia,
        
        -- ================= MÉTRICAS DE RIESGO =================
        ISNULL(CAST(SUM(CASE WHEN ob.EstadoLimpio = 'ANULADA' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(ob.IdOrdenes), 0) AS DECIMAL(5,2)), 0) AS PorcentajeAnulacion
        
    FROM CTE_OrdenesBase ob
    LEFT JOIN CTE_DiasActivos da ON ob.SegmentoNegocio = da.SegmentoNegocio
    GROUP BY ob.SegmentoNegocio;
END;