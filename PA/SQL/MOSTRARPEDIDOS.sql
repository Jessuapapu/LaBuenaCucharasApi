CREATE PROC MostrarPedidos
	@IdOrden INT = NULL,
	@IdPedido INT = NULL,
	@IdCliente INT = NULL,
	@Pagina  INT = 1,
	@Rows INT  = 10,
	@Todo BIT = 0
AS 
BEGIN
	SET NOCOUNT ON
	-- Validaciones para la paginacion
	-- si queremos todo mandamos un 1 en la variable todo
	IF @Pagina < 0 OR @Rows <= 1
		BEGIN
			PRINT ('INGRESE UNA PAGINA O UNA CANTIDAD DE FILAS VALIDAS')
			RETURN -1
		END
	SET @Rows = IIF(@Todo = 1, (SELECT COUNT(IdOrdenes) FROM ordenes), @Rows)
	-- SI TODO ES 1, SE DEBE INICIAR DESDE LA PAGINA 0
	SET @Pagina = IIF(@Todo = 1, 1, @Pagina)

	SELECT P.IdPedido,SUM(O.CostoTotal) MONTO_TOTAL, O.Estado, C.NombreCliente FROM pedidos P 
	INNER JOIN pedidosordenes PO ON P.IdPedido = PO.IdPedido
	INNER JOIN ordenes O ON PO.IdOrdenes = O.IdOrdenes
	INNER JOIN clientes C ON O.IdCliente = C.IdCliente
	WHERE (@IdOrden IS NULL OR O.IdOrdenes = @IdOrden) AND (@IdPedido IS NULL OR P.IdPedido = @IdPedido) 
	AND (@IdCliente IS NULL OR C.IdCliente = @IdCliente)
	GROUP BY P.IdPedido, O.Estado, C.NombreCliente
	ORDER BY P.IdPedido
	OFFSET (@Pagina - 1) * @Rows ROWS FETCH NEXT @Rows ROWS ONLY

END