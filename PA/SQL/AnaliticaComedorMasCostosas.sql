CREATE PROC pa_Analitica_Comedor_MasCostosas
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP 10
        o.IdOrdenes AS IdFactura,
        o.CostoTotal AS MontoTotal,
        ISNULL((
            SELECT SUM(do.CantidadPlatillo)
            FROM detallesordenes do
            WHERE do.IdOrdenes = o.IdOrdenes
        ), 0) AS CantidadTotal,
        o.Estado AS Estado,
        o.Fecha AS Fecha,
        CASE
            WHEN o.IdCliente = 1 THEN 'Consumidor de Paso'
            ELSE ISNULL(c.NombreCliente, 'Consumidor de Paso')
        END AS NombreCliente
    FROM ordenes o
    LEFT JOIN clientes c ON o.IdCliente = c.IdCliente
    LEFT JOIN pedidosordenes po ON o.IdOrdenes = po.IdOrdenes
    WHERE po.IdOrdenes IS NULL -- Filtrado estricto de Comedor (No está en pedidosordenes)
      AND o.Estado NOT IN ('ANULADO', 'ANULADA', 'CANCELADO', 'CANCELADA', 'PENDIENTE')
      AND (@FechaInicio IS NULL OR o.Fecha >= @FechaInicio)
      AND (@FechaFin IS NULL OR o.Fecha <= @FechaFin)
    ORDER BY o.CostoTotal DESC;
END;
