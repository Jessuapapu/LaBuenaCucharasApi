CREATE PROC ActualizarPagos
	@IdPago INT = NULL,
	@IdOrden INT = NULL
AS
BEGIN

	UPDATE pago SET Estado = 0
	WHERE (@IdPago IS NULL OR IdPago = @IdPago)
	AND (@IdOrden IS NULL OR IdOrden = @IdOrden)

END

/* NJDS MUY MALA PRACTICA PERO ME DA HUEVA HACER TRIGGERS */