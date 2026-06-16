CREATE PROC pa_Analitica_Platillos_Comedor
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP 10
        p.IdPlatillo AS IdPlatillo,
        p.NombrePlatillo AS NombrePlatillo,
        SUM(do.CantidadPlatillo) AS UnidadesVendidas,
        SUM(do.CostoTotal) AS IngresoTotalGenerado,
        -- Calcula a cómo se vendió en promedio cada unidad
        ISNULL(AVG(do.CostoTotal / NULLIF(do.CantidadPlatillo, 0)), 0) AS PrecioPromedioVenta
    FROM detallesordenes do
    INNER JOIN platillos p ON do.IdPlatillo = p.IdPlatillo
    INNER JOIN ordenes o ON do.IdOrdenes = o.IdOrdenes
    LEFT JOIN pedidosordenes po ON o.IdOrdenes = po.IdOrdenes
    WHERE po.IdOrdenes IS NULL -- Filtra para que solo se sumen las ventas hechas en el Comedor
      AND o.Estado NOT IN ('ANULADO', 'ANULADA', 'CANCELADO', 'CANCELADA', 'PENDIENTE')
      AND (@FechaInicio IS NULL OR o.Fecha >= @FechaInicio)
      AND (@FechaFin IS NULL OR o.Fecha <= @FechaFin)
    GROUP BY p.IdPlatillo, p.NombrePlatillo
    ORDER BY UnidadesVendidas DESC; -- Ordenado por el que más unidades movió
END;
