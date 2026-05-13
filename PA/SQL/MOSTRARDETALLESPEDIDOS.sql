CREATE PROC MostrarDetallesPedidos
	@IdPedido INT = NULL,
	@IdOrden INT = NULL,
	@IdCliente INT = NULL
AS
BEGIN
	SET NOCOUNT ON
	IF @IdPedido IS NULL
	BEGIN
		PRINT 'INGRESE EL ID DEL PEDIDO'
		RETURN -1
	END
	IF @IdPedido IS NULL AND @IdCliente IS NULL AND @IdOrden IS NULL
	BEGIN
		PRINT('INGRESE ALMENOS UN IDENTIFICADOR')
		RETURN -1
	END

	SELECT PDOR.IdPedido, C.NombreCliente, O.IdOrdenes, P.NombrePlatillo, OD.CantidadPlatillo, OD.PrecioUnico FROM ordenes O
	INNER JOIN detallesordenes OD ON O.IdOrdenes = OD.IdOrdenes
	INNER JOIN clientes C ON O.IdCliente = C.IdCliente
	INNER JOIN platillos P ON OD.IdPlatillo = P.IdPlatillo
	INNER JOIN pedidosordenes PDOR ON O.IdOrdenes = PDOR.IdOrdenes
	WHERE (@IdOrden IS NULL OR O.IdOrdenes = @IdOrden)
    AND
    (@IdCliente IS NULL OR O.IdCliente = @IdCliente)
	AND 
	PDOR.IdPedido = @IdPedido 
	ORDER BY C.NombreCliente

END