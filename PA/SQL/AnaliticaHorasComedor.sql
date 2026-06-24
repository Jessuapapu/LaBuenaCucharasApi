CREATE PROC pa_Analitica_Top5_Horas_Comedor
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- CTE ultra rápida: Ya no hacemos JOIN, solo filtramos por IdCliente = 1
    WITH CTE_HorasComedor AS (
        SELECT 
            DATEPART(HOUR, Fecha) AS HoraDelDia,
            IdOrdenes,
            CostoTotal,
            CAST(Fecha AS DATE) AS FechaDia
        FROM ordenes
        WHERE IdCliente = 1 -- <--- LA REGLA DE ORO DEL COMEDOR
          AND Estado NOT IN ('ANULADO', 'ANULADA', 'CANCELADO', 'CANCELADA', 'PENDIENTE')
          AND (@FechaInicio IS NULL OR Fecha >= @FechaInicio)
          AND (@FechaFin IS NULL OR Fecha <= @FechaFin)
    )
    SELECT TOP 5
        HoraDelDia,
        COUNT(IdOrdenes) AS TotalOrdenesHistoricas,
        COUNT(DISTINCT FechaDia) AS DiasLaboradosEnEsaHora,
        
        -- Cálculo del promedio de mesas/órdenes por día en esta hora
        ISNULL(
            CAST(COUNT(IdOrdenes) AS DECIMAL(10,2)) / NULLIF(COUNT(DISTINCT FechaDia), 0)
        , 0) AS PromedioOrdenesPorDia,
        
        SUM(CostoTotal) AS IngresoTotalGenerado,
        ISNULL(AVG(CostoTotal), 0) AS IngresoPromedioEnEstaHora

    FROM CTE_HorasComedor
    GROUP BY HoraDelDia
    ORDER BY PromedioOrdenesPorDia DESC;
END;
