CREATE PROC MostrarDetalles
	 @Id INT = NULL,
	 @IdCliente INT = NULL
AS
BEGIN
	SET NOCOUNT ON

	IF @Id IS NULL AND @IdCliente IS NULL
	BEGIN
		PRINT('INGRESE ALMENOS UN IDENTIFICADOR')
		RETURN 1
	END

	SELECT C.NombreCliente, O.IdOrdenes, P.NombrePlatillo, OD.CantidadPlatillo, OD.PrecioUnico FROM ordenes O
	INNER JOIN detallesordenes OD ON O.IdOrdenes = OD.IdOrdenes
	INNER JOIN clientes C ON O.IdCliente = C.IdCliente
	INNER JOIN platillos P ON OD.IdPlatillo = P.IdPlatillo
	WHERE O.IdOrdenes = IIF(@Id IS NULL, O.IdOrdenes, @Id) OR O.IdCliente = IIF(@IdCliente IS NULL, O.IdCliente, @IdCliente)
	ORDER BY C.NombreCliente

END