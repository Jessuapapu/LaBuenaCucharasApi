CREATE PROC pa_Analitica_Logistica_Estados
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        Estado AS EstadoOrden,
        COUNT(IdOrdenes) AS CantidadOrdenes,
        SUM(CostoTotal) AS VolumenMonetario
    FROM ordenes
    WHERE (@FechaInicio IS NULL OR Fecha >= @FechaInicio) 
      AND (@FechaFin IS NULL OR Fecha <= @FechaFin)
    GROUP BY Estado
    ORDER BY CantidadOrdenes DESC;
END;
