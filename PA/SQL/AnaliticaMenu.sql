CREATE PROC pa_Analitica_Menu_Indispensable
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        p.IdPlatillo AS IdPlatillo,
        p.NombrePlatillo AS NombrePlatillo,
        SUM(do.CantidadPlatillo) AS UnidadesVendidas,
        SUM(do.CostoTotal) AS IngresoTotalGenerado,
        -- Permite evaluar si el precio asignado es correcto o si hubo descuentos/promociones
        ISNULL(AVG(do.CostoTotal / NULLIF(do.CantidadPlatillo, 0)), 0) AS PrecioPromedioVenta
    FROM detallesordenes do
    INNER JOIN platillos p ON do.IdPlatillo = p.IdPlatillo
    INNER JOIN ordenes o ON do.IdOrdenes = o.IdOrdenes
    WHERE o.Estado NOT IN ('ANULADO', 'ANULADA', 'CANCELADO', 'CANCELADA', 'PENDIENTE')
      AND (@FechaInicio IS NULL OR o.Fecha >= @FechaInicio) 
      AND (@FechaFin IS NULL OR o.Fecha <= @FechaFin)
    GROUP BY p.IdPlatillo, p.NombrePlatillo
    ORDER BY IngresoTotalGenerado DESC;
END;
