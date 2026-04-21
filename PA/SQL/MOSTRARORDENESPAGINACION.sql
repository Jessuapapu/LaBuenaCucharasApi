CREATE PROC MostrarOrdenes
	@IdOrden INT = NULL,
	@Pagina  INT = 1,
	@Rows INT  = 10,
	@Todo BIT = 0
-- Jessua Solis  4T1-COM  2023-0851U
AS 
BEGIN
	SET NOCOUNT ON

	IF @Rows <= 1 or @Pagina <= 0
		BEGIN
			PRINT('INGRESE VALORES VALIDOS PARA LA PAGINACION O LA CANTIDAD DE COLUMNAS')
			RETURN 1;
		END
	
	-- Validaciones para la paginacion
	-- si queremos todo mandamos un 1 en la variable todo
	--				si todo es 1, se le manda la cantidad total de id de ordenes, si no la misma varible
	SET @Rows = IIF(@Todo = 1,(SELECT COUNT(IdOrdenes) FROM ordenes),@Rows)
	--				si todo es 1, se le setea 1 como variable por defecto, si no la misma varible
	SET @Pagina = IIF(@Todo = 1,1,@Pagina)

	

	
	SELECT C.NombreCliente, O.IdOrdenes, SUM(OD.CantidadPlatillo * OD.PrecioUnico),
	O.Fecha
	FROM detallesordenes OD
	INNER JOIN ordenes O ON OD.IdOrdenes = O.IdOrdenes
	INNER JOIN clientes C ON O.IdCliente = C.IdCliente
	WHERE (@IdOrden IS NULL OR O.IdOrdenes = @IdOrden)
	GROUP BY C.NombreCliente, O.IdOrdenes, O.Fecha
	ORDER BY O.IdOrdenes
	-- Por defecto siempre sera la pagina #0 y las filas 10
	OFFSET (@Pagina - 1) * @Rows ROWS FETCH NEXT @Rows ROWS ONLY

END
