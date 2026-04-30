CREATE PROC MostrarFacturas
    @IdCliente INT = NULL,
    @IdOrden INT = NULL,
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL,
    @Monto DECIMAL(18,2) = NULL,
    @MontoFin DECIMAL(18,2) = NULL,
    @CantidadTotal INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF (@FechaInicio IS NOT NULL AND @FechaFin IS NOT NULL AND @FechaInicio > @FechaFin)
    BEGIN
        print 'Error: La fecha de inicio no puede ser mayor a la fecha fin.';
        RETURN 1;
    END

    IF (@Monto IS NOT NULL AND @MontoFin IS NOT NULL AND @Monto > @MontoFin)
    BEGIN
        print 'Error: El monto inicial no puede ser mayor al monto final.';
        RETURN 1;
    END

    SELECT C.NombreCliente, F.* FROM facturas F
    INNER JOIN FacturasOrdenes FO ON F.IdFactura = FO.IdFactura
    INNER JOIN ordenes O ON FO.IdOrdenes = O.IdOrdenes
    INNER JOIN clientes C ON O.IdCliente = C.IdCliente
    WHERE 
        (@IdCliente IS NULL OR C.IdCliente = @IdCliente)
        AND (@IdOrden IS NULL OR O.IdOrdenes = @IdOrden)
        AND (@FechaInicio IS NULL OR F.Fecha >= @FechaInicio)
        AND (@FechaFin IS NULL OR F.Fecha <= @FechaFin)
        AND (@Monto IS NULL OR F.MontoTotal >= @Monto)
        AND (@MontoFin IS NULL OR F.MontoTotal <= @MontoFin)
        AND (@CantidadTotal IS NULL OR F.CantidadTotal = @CantidadTotal);
END