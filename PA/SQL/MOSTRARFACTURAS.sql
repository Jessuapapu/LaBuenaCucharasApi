CREATE PROC MostrarFacturas
    @IdFactura INT = NULL,
    @IdCliente INT = NULL,
    @IdOrden INT = NULL,
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL,
    @Monto DECIMAL(18,2) = NULL,
    @MontoFin DECIMAL(18,2) = NULL,
    @CantidadTotal INT = NULL,
    @Pagina INT = 1,
	@Rows INT  = 10,
	@Todo BIT = 0
AS
BEGIN
    SET NOCOUNT ON;

    IF @Pagina < 0 OR @Rows <= 1
		BEGIN
			PRINT ('INGRESE UNA PAGINA O UNA CANTIDAD DE FILAS VALIDAS')
			RETURN -1
		END
	SET @Rows = IIF(@Todo = 1, (SELECT COUNT(IdOrdenes) FROM ordenes), @Rows)
	-- SI TODO ES 1, SE DEBE INICIAR DESDE LA PAGINA 0
	SET @Pagina = IIF(@Todo = 1, 1, @Pagina)

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
        (@IdFactura IS NULL OR f.IdFactura = @IdFactura)
        AND (@IdCliente IS NULL OR C.IdCliente = @IdCliente)
        AND (@IdOrden IS NULL OR O.IdOrdenes = @IdOrden)
        AND (@FechaInicio IS NULL OR F.Fecha >= @FechaInicio)
        AND (@FechaFin IS NULL OR F.Fecha <= @FechaFin)
        AND (@Monto IS NULL OR F.MontoTotal >= @Monto)
        AND (@MontoFin IS NULL OR F.MontoTotal <= @MontoFin)
        AND (@CantidadTotal IS NULL OR F.CantidadTotal = @CantidadTotal)
    ORDER BY f.IdFactura DESC
    OFFSET (@Pagina - 1) * @Rows ROWS FETCH NEXT @Rows ROWS ONLY
END