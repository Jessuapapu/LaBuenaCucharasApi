CREATE PROC MostrarContratos
	@IdCliente INT = NULL,
	@FechaVencimiento DATETIME = NULL,
	@FechaInicio DATETIME = NULL,
	@Presupuesto FLOAT = NULL,
	@PresupuestoFin FLOAT = NULL

AS 
BEGIN

	-- Validar congruencia de fechas
    IF (@FechaInicio IS NOT NULL AND @FechaVencimiento IS NOT NULL AND @FechaInicio > @FechaVencimiento)
    BEGIN
        print 'Error: La fecha de inicio no puede ser mayor a la fecha de vencimiento.'
        RETURN 1;
    END

    -- Validar congruencia de presupuesto
    IF (@Presupuesto IS NOT NULL AND @PresupuestoFin IS NOT NULL AND @Presupuesto > @PresupuestoFin)
    BEGIN
        print 'Error: El presupuesto inicial no puede ser mayor al presupuesto final.'
        RETURN 1;
    END

	SELECT CLI.NombreCliente,CO.* FROM contrato CO
    INNER JOIN clientes CLI ON CO.IdCliente = CLI.IdCliente
	WHERE 
        (@IdCliente IS NULL OR CO.IdCliente = @IdCliente)
        
        AND (@FechaInicio IS NULL OR CO.FechaInicio >= @FechaInicio)
        AND (@FechaVencimiento IS NULL OR CO.FechaVencimiento <= @FechaVencimiento)
        
        AND (@Presupuesto IS NULL OR CO.Presupuesto >= @Presupuesto)
        AND (@PresupuestoFin IS NULL OR CO.Presupuesto <= @PresupuestoFin);
END