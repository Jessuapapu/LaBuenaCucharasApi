CREATE PROC pa_Analitica_Horas_Criticas
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        DATEPART(HOUR, Fecha) AS HoraDelDia,
        COUNT(IdOrdenes) AS FlujoDeOrdenes,
        SUM(CostoTotal) AS DineroIngresado,
        AVG(CostoTotal) AS TicketPromedioHora
    FROM ordenes
    WHERE Estado NOT IN ('ANULADO', 'ANULADA', 'CANCELADO', 'CANCELADA', 'PENDIENTE')
      AND (@FechaInicio IS NULL OR Fecha >= @FechaInicio) 
      AND (@FechaFin IS NULL OR Fecha <= @FechaFin)
    GROUP BY DATEPART(HOUR, Fecha)
    ORDER BY HoraDelDia ASC;
END;
