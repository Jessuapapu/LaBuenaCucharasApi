CREATE PROC Analitica_Ventas
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- Variables locales para capturar los fragmentos JSON de los sub-procedimientos
    DECLARE @RendimientoPorSegmento NVARCHAR(MAX),
            @AnalisisDeFidelidad NVARCHAR(MAX),
            @PerfilDeConsumo NVARCHAR(MAX),
            @RendimientoPorDiaSemana NVARCHAR(MAX),
            @EficienciaDeRotacion NVARCHAR(MAX),
            @PlatillosMasVendidosPorSegmento NVARCHAR(MAX),
            @Top10_Comedor NVARCHAR(MAX),
            @Top10_Eventos NVARCHAR(MAX),
            @DesgloseSemanal NVARCHAR(MAX),
            @ResumenEstadisticoFechas NVARCHAR(MAX);

    -- Ejecución secuencial de los módulos especializados
    EXEC pa_Sub_Analitica_Macro @FechaInicio, @FechaFin, @RendimientoPorSegmento OUTPUT, @AnalisisDeFidelidad OUTPUT, @PerfilDeConsumo OUTPUT;
    EXEC pa_Sub_Analitica_Operaciones @FechaInicio, @FechaFin, @RendimientoPorDiaSemana OUTPUT, @EficienciaDeRotacion OUTPUT;
    EXEC pa_Sub_Analitica_Rankings @FechaInicio, @FechaFin, @PlatillosMasVendidosPorSegmento OUTPUT, @Top10_Comedor OUTPUT, @Top10_Eventos OUTPUT;
    EXEC pa_Sub_Analitica_Cronologia @FechaInicio, @FechaFin, @DesgloseSemanal OUTPUT, @ResumenEstadisticoFechas OUTPUT;

    -- Ensamblaje final de las piezas en un único árbol JSON unificado
    DECLARE @ResultadoJSON NVARCHAR(MAX) = (
        SELECT 
            JSON_QUERY(@RendimientoPorSegmento) AS RendimientoPorSegmento,
            JSON_QUERY(@AnalisisDeFidelidad) AS AnalisisDeFidelidad,
            JSON_QUERY(@PerfilDeConsumo) AS PerfilDeConsumo,
            JSON_QUERY(@RendimientoPorDiaSemana) AS RendimientoPorDiaSemana,
            JSON_QUERY(@EficienciaDeRotacion) AS EficienciaDeRotacion,
            JSON_QUERY(@PlatillosMasVendidosPorSegmento) AS PlatillosMasVendidosPorSegmento,
            JSON_QUERY(@Top10_Comedor) AS Top10_Comedor,
            JSON_QUERY(@Top10_Eventos) AS Top10_Eventos,
            JSON_QUERY(@DesgloseSemanal) AS DesgloseSemanal,
            JSON_QUERY(@ResumenEstadisticoFechas) AS ResumenEstadisticoFechas
        FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    );

    -- Retorno de la información
    SELECT ISNULL(@ResultadoJSON, '{}') AS AnaliticaVentasMaestra;
END;
