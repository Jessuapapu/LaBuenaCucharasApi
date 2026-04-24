CREATE PROC MostrarOrdenes
	@IdOrden INT = NULL,
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
			RETURN
		END
	SET @Rows = IIF(@Todo = 1,(SELECT COUNT(IdOrdenes) FROM ordenes),@Rows)
	-- SI TODO ES 1, SE DEBE INICIAR DESDE LA PAGINA 0
	SET @Pagina = IIF(@Todo = 1,1,@Pagina)

	

	SELECT C.NombreCliente, O.IdOrdenes, SUM(OD.CantidadPlatillo * OD.PrecioUnico) MONTOTOTAL,
	O.Fecha, CD.dirreccion
	FROM detallesordenes OD
	INNER JOIN ordenes O ON OD.IdOrdenes = O.IdOrdenes
	INNER JOIN clientes C ON O.IdCliente = C.IdCliente
	INNER JOIN clientedirrecion CD ON O.IdCliente = CD.IdCliente
	WHERE (@IdOrden IS NULL OR O.IdOrdenes = @IdOrden)
	GROUP BY C.NombreCliente, O.IdOrdenes, O.Fecha
	ORDER BY O.IdOrdenes
	OFFSET (@Pagina - 1) * @Rows ROWS FETCH NEXT @Rows ROWS ONLY

END
