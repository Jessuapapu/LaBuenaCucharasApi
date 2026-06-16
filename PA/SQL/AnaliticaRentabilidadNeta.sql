CREATE PROC pa_Analitica_Rentabilidad_Neta
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- Variables para centralizar los cálculos intermedios
    DECLARE @IngresoComedor DECIMAL(18,2) = 0;
    DECLARE @IngresoEventos DECIMAL(18,2) = 0;
    DECLARE @CostoAbastecimiento DECIMAL(18,2) = 0;

    -- 1. Cálculo de Ingresos Netos por Canales (Solo órdenes ejecutadas con éxito)
    SELECT 
        @IngresoComedor = ISNULL(SUM(CASE WHEN po.IdOrdenes IS NULL THEN o.CostoTotal ELSE 0 END), 0),
        @IngresoEventos = ISNULL(SUM(CASE WHEN po.IdOrdenes IS NOT NULL THEN o.CostoTotal ELSE 0 END), 0)
    FROM ordenes o
    LEFT JOIN pedidosordenes po ON o.IdOrdenes = po.IdOrdenes
    WHERE o.Estado NOT IN ('ANULADO', 'ANULADA', 'CANCELADO', 'CANCELADA', 'PENDIENTE')
      AND (@FechaInicio IS NULL OR o.Fecha >= @FechaInicio)
      AND (@FechaFin IS NULL OR o.Fecha <= @FechaFin);

    -- 2. Cálculo de Costos de Abastecimiento (Con tu tabla 'registrodeabastecimiento' y columna 'CostoTotal')
    SELECT @CostoAbastecimiento = ISNULL(SUM(CostoTotal), 0)
    FROM registrodeabastecimiento
    WHERE (@FechaInicio IS NULL OR Fecha >= @FechaInicio)
      AND (@FechaFin IS NULL OR Fecha <= @FechaFin);

    -- 3. Cálculo de Márgenes Finales
    DECLARE @IngresoTotal DECIMAL(18,2) = @IngresoComedor + @IngresoEventos;
    DECLARE @GananciaNeta DECIMAL(18,2) = @IngresoTotal - @CostoAbastecimiento;
    DECLARE @MargenPorcentaje DECIMAL(18,2) = 0;

    -- Previene errores de división por cero si no hay ventas registradas
    IF @IngresoTotal > 0
        SET @MargenPorcentaje = CAST((@GananciaNeta * 100.0) / @IngresoTotal AS DECIMAL(10,2));

    -- Retorno en un conjunto de resultados plano de una sola fila
    SELECT 
        @IngresoComedor AS IngresoComedor,
        @IngresoEventos AS IngresoEventos,
        @IngresoTotal AS IngresoTotalVentas,
        @CostoAbastecimiento AS TotalCostoAbastecimiento,
        @GananciaNeta AS GananciaNetaReal,
        @MargenPorcentaje AS MargenRentabilidadPorcentaje;
END;
