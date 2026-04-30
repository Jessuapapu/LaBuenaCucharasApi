CREATE PROC MostrarDetalleFactura
	@Id INT = NULL,
	@IdCliente INT = NULL,
	@IdOrden INT = NULL
	AS
	BEGIN
		WITH DetallesFacturas
		AS (
		
			SELECT F.IdFactura, 
			DO.IdOrdenes, DO.CostoTotal, DO.CantidadPlatillo, DO.IdPlatillo, DO.PrecioUnico,
			O.IdCliente FROM facturas F
			INNER JOIN FacturasOrdenes FO ON F.IdFactura = FO.IdFactura
			INNER JOIN detallesordenes DO ON FO.IdOrdenes = DO.IdOrdenes
			INNER JOIN ordenes O ON DO.IdOrdenes = O.IdOrdenes

		)
		SELECT DF.IdFactura, DF.IdCliente, DF.IdOrdenes, DF.IdCliente, P.NombrePlatillo, DF.CantidadPlatillo, 
				DF.CostoTotal, DF.PrecioUnico
		FROM DetallesFacturas DF 
		INNER JOIN platillos P ON DF.IdPlatillo = P.IdPlatillo
		WHERE
			(@Id IS NULL OR DF.IdFactura = @Id) AND
			(@IdCliente IS NULL OR DF.IdCliente = @IdCliente) AND
			(@IdOrden IS NULL OR DF.IdOrdenes = @IdCliente)
		
	END
