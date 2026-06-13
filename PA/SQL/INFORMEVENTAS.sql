CREATE PROC Analitica_Ventas
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @ResultadoJSON NVARCHAR(MAX);

    -- =========================================================================
    -- CTE 1: ORDENES BASE Y NORMALIZACIÓN DE ESTADOS (EL GRAN ARREGLO)
    -- =========================================================================
    WITH CTE_OrdenesBase AS (
        SELECT 
            o.IdOrdenes,
            o.CostoTotal,
            o.Fecha,
            o.IdCliente,
            
            -- Normalizamos el estado: Cualquier variación de anulación se agrupa
            CASE 
                WHEN o.Estado IN ('ANULADO', 'ANULADA', 'CANCELADO', 'CANCELADA') THEN 'ANULADA'
                WHEN o.Estado = 'PENDIENTE' THEN 'PENDIENTE'
                ELSE 'COMPLETADA' -- Cubre 'ENTREGADO', 'PREPARADO', etc.
            END AS EstadoOperativo,
            
            -- Segmentación Comedor vs Eventos
            CASE 
                WHEN po.IdPedido IS NOT NULL THEN 'EVENTO/CONTRATO'
                ELSE 'COMEDOR' 
            END AS SegmentoNegocio,
            
            DATENAME(WEEKDAY, o.Fecha) AS DiaSemana,
            ISNULL((SELECT SUM(CantidadPlatillo) FROM detallesordenes WHERE IdOrdenes = o.IdOrdenes), 0) AS VolumenArticulos
            
        FROM ordenes o
        LEFT JOIN pedidosordenes po ON o.IdOrdenes = po.IdOrdenes
        WHERE (@FechaInicio IS NULL OR o.Fecha >= @FechaInicio)
          AND (@FechaFin IS NULL OR o.Fecha <= @FechaFin)
    ),
    
    -- =========================================================================
    -- CTE 2: RENDIMIENTO DE PLATILLOS POR SEGMENTO
    -- =========================================================================
    CTE_VentasPlatillos AS (
        SELECT 
            ob.SegmentoNegocio,
            plat.NombrePlatillo,
            SUM(det.CantidadPlatillo) AS CantidadTotal,
            SUM(det.CostoTotal) AS IngresoTotal
        FROM detallesordenes det
        INNER JOIN platillos plat ON det.IdPlatillo = plat.IdPlatillo
        INNER JOIN CTE_OrdenesBase ob ON det.IdOrdenes = ob.IdOrdenes
        WHERE ob.EstadoOperativo = 'COMPLETADA' -- Ahora usamos el estado limpio
        GROUP BY ob.SegmentoNegocio, plat.NombrePlatillo
    ),

    -- =========================================================================
    -- CTE 3: AUDITORÍA DE TIEMPOS EN COMEDOR
    -- =========================================================================
    CTE_EficienciaMesas AS (
        SELECT 
            am.IdOrden,
            am.IdMesa,
            DATEDIFF(MINUTE, am.HoraEntrada, am.HoraSalida) AS MinutosEnMesa
        FROM auditoria_mesas am
        INNER JOIN CTE_OrdenesBase ob ON am.IdOrden = ob.IdOrdenes
        WHERE am.HoraSalida > am.HoraEntrada 
          AND ob.SegmentoNegocio = 'COMEDOR' 
    ),

    -- =========================================================================
    -- CTE 4: RENDIMIENTO DIARIO (FUENTE ÚNICA DE VERDAD)
    -- =========================================================================
    CTE_RendimientoDiario AS (
        SELECT 
            DATEPART(YEAR, ob.Fecha) AS Anio,
            DATEPART(WEEK, ob.Fecha) AS SemanaDelAnio,
            CAST(ob.Fecha AS DATE) AS FechaDia,
            DATENAME(WEEKDAY, ob.Fecha) AS DiaNombre,
            COUNT(ob.IdOrdenes) AS FlujoDeOrdenes,
            SUM(ob.CostoTotal) AS DineroIngresado,
            AVG(ob.CostoTotal) AS PromedioPorOrden
        FROM CTE_OrdenesBase ob
        WHERE ob.EstadoOperativo = 'COMPLETADA' -- Solo suma dinero real concretado
        GROUP BY DATEPART(YEAR, ob.Fecha), DATEPART(WEEK, ob.Fecha), CAST(ob.Fecha AS DATE), DATENAME(WEEKDAY, ob.Fecha)
    ),

    -- =========================================================================
    -- CTE 5: LIMITES DE SEMANA
    -- =========================================================================
    CTE_LimitesSemana AS (
        SELECT 
            Anio,
            SemanaDelAnio,
            MIN(FechaDia) AS FechaInicioSemana,
            MAX(FechaDia) AS FechaFinSemana
        FROM CTE_RendimientoDiario
        GROUP BY Anio, SemanaDelAnio
    )

    -- =========================================================================
    -- ENSAMBLAJE DEL JSON MAESTRO
    -- =========================================================================
    SELECT @ResultadoJSON = (
        SELECT 
            
            -- BLOQUE 1: KPIs FINANCIEROS Y OPERATIVOS
            JSON_QUERY((SELECT SegmentoNegocio, COUNT(IdOrdenes) AS TotalOrdenes, SUM(CASE WHEN EstadoOperativo = 'COMPLETADA' THEN 1 ELSE 0 END) AS Completadas, SUM(CASE WHEN EstadoOperativo = 'ANULADA' THEN 1 ELSE 0 END) AS Anuladas, ISNULL(SUM(CASE WHEN EstadoOperativo = 'COMPLETADA' THEN CostoTotal ELSE 0 END), 0) AS IngresoBruto, ISNULL(AVG(CASE WHEN EstadoOperativo = 'COMPLETADA' THEN CostoTotal ELSE NULL END), 0) AS TicketPromedio, ISNULL(CAST(SUM(CASE WHEN EstadoOperativo = 'ANULADA' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(IdOrdenes), 0) AS DECIMAL(5,2)), 0) AS TasaCancelacionPorcentaje FROM CTE_OrdenesBase GROUP BY SegmentoNegocio FOR JSON PATH)) AS RendimientoPorSegmento,
            
            -- BLOQUE 2: FIDELIZACIÓN
            JSON_QUERY((SELECT * FROM (SELECT 'Clientes Fidelizados' AS SegmentoCliente, COUNT(IdOrdenes) AS VolumenOperaciones, ISNULL(SUM(CASE WHEN EstadoOperativo = 'COMPLETADA' THEN CostoTotal ELSE 0 END), 0) AS ValorGenerado FROM CTE_OrdenesBase WHERE IdCliente > 1 UNION ALL SELECT 'Consumidor De Paso' AS SegmentoCliente, COUNT(IdOrdenes) AS VolumenOperaciones, ISNULL(SUM(CASE WHEN EstadoOperativo = 'COMPLETADA' THEN CostoTotal ELSE 0 END), 0) AS ValorGenerado FROM CTE_OrdenesBase WHERE IdCliente = 1 OR IdCliente IS NULL) AS SubFidelidad FOR JSON PATH)) AS AnalisisDeFidelidad,
            
            -- BLOQUE 3: PERFIL DE CONSUMO
            JSON_QUERY((SELECT SUM(CASE WHEN CostoTotal < 300 THEN 1 ELSE 0 END) AS OrdenesDeConsumoBajo, SUM(CASE WHEN CostoTotal BETWEEN 300 AND 1000 THEN 1 ELSE 0 END) AS OrdenesDeConsumoMedio, SUM(CASE WHEN CostoTotal > 1000 THEN 1 ELSE 0 END) AS OrdenesVIP_ConsumoAlto, ISNULL(AVG(VolumenArticulos), 0) AS PromedioArticulosPorBandeja FROM CTE_OrdenesBase WHERE EstadoOperativo = 'COMPLETADA' FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)) AS PerfilDeConsumo,
            
            -- BLOQUE 4: MAPA DE CALOR DIARIO GLOBAL
            JSON_QUERY((SELECT TOP 100 PERCENT DiaNombre AS Dia, SUM(FlujoDeOrdenes) AS FlujoDeOrdenes, SUM(DineroIngresado) AS DineroIngresado FROM CTE_RendimientoDiario GROUP BY DiaNombre ORDER BY DineroIngresado DESC FOR JSON PATH)) AS RendimientoPorDiaSemana,
            
            -- BLOQUE 5: ROTACIÓN DE COMEDOR
            JSON_QUERY((SELECT COUNT(DISTINCT IdMesa) AS MesasDiferentesAtendidas, COUNT(IdOrden) AS TotalServiciosEnMesa, ISNULL(AVG(MinutosEnMesa), 0) AS EstadiaPromedioMinutos, ISNULL(MAX(MinutosEnMesa), 0) AS EstadiaMasLargaRegistradaMinutos FROM CTE_EficienciaMesas FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)) AS EficienciaDeRotacion,
            
            -- BLOQUE 6: PLATILLOS
            JSON_QUERY((SELECT SegmentoNegocio, NombrePlatillo, CantidadTotal, IngresoTotal FROM (SELECT SegmentoNegocio, NombrePlatillo, CantidadTotal, IngresoTotal, ROW_NUMBER() OVER(PARTITION BY SegmentoNegocio ORDER BY CantidadTotal DESC) as ranking FROM CTE_VentasPlatillos) t WHERE ranking <= 5 FOR JSON PATH)) AS PlatillosMasVendidosPorSegmento,
            
            -- BLOQUE 7 Y 8: TOPS
            JSON_QUERY((SELECT TOP 10 ob.IdOrdenes AS OrdenId, ob.Fecha, CASE WHEN ob.IdCliente = 1 THEN 'Consumidor de Paso' ELSE ISNULL(c.NombreCliente, 'Consumidor de Paso') END AS Cliente, ob.CostoTotal AS MontoFacturado FROM CTE_OrdenesBase ob LEFT JOIN clientes c ON ob.IdCliente = c.IdCliente WHERE ob.SegmentoNegocio = 'COMEDOR' AND ob.EstadoOperativo = 'COMPLETADA' ORDER BY ob.CostoTotal DESC FOR JSON PATH)) AS Top10_Comedor,
            JSON_QUERY((SELECT TOP 10 ob.IdOrdenes AS OrdenId, ob.Fecha, CASE WHEN ob.IdCliente = 1 THEN 'Cliente Genérico de Evento' ELSE ISNULL(c.NombreCliente, 'Cliente Genérico de Evento') END AS Cliente, ob.CostoTotal AS MontoFacturado FROM CTE_OrdenesBase ob LEFT JOIN clientes c ON ob.IdCliente = c.IdCliente WHERE ob.SegmentoNegocio = 'EVENTO/CONTRATO' AND ob.EstadoOperativo = 'COMPLETADA' ORDER BY ob.CostoTotal DESC FOR JSON PATH)) AS Top10_Eventos,

            -- =========================================================
            -- BLOQUE 9: DESGLOSE SEMANAL PLANO
            -- =========================================================
            JSON_QUERY((SELECT TOP 100 PERCENT
                s.FechaInicioSemana,
                s.FechaFinSemana,
                CONCAT('Semana del ', FORMAT(s.FechaInicioSemana, 'dd/MM/yyyy'), ' al ', FORMAT(s.FechaFinSemana, 'dd/MM/yyyy')) AS Periodo,
                
                JSON_QUERY((
                    SELECT TOP 100 PERCENT
                        d.DiaNombre AS Dia,
                        d.FechaDia AS Fecha,
                        d.FlujoDeOrdenes,
                        d.DineroIngresado
                    FROM CTE_RendimientoDiario d
                    WHERE d.Anio = s.Anio AND d.SemanaDelAnio = s.SemanaDelAnio
                    ORDER BY d.FechaDia ASC
                    FOR JSON PATH
                )) AS RendimientoPorDiaSemana

             FROM CTE_LimitesSemana s
             ORDER BY s.Anio ASC, s.SemanaDelAnio ASC
             FOR JSON PATH)) AS DesgloseSemanal,

            -- =========================================================
            -- BLOQUE 10: RESUMEN ANALÍTICO DE FECHAS
            -- =========================================================
            JSON_QUERY((SELECT 
                
                JSON_QUERY((SELECT TOP 1 FechaDia AS Fecha, DiaNombre AS Dia, DineroIngresado AS TotalGenerado FROM CTE_RendimientoDiario ORDER BY DineroIngresado DESC FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)) AS MejorDiaFacturacionAbsoluta,
                JSON_QUERY((SELECT TOP 1 FechaDia AS Fecha, DiaNombre AS Dia, PromedioPorOrden AS TicketPromedio, FlujoDeOrdenes AS CantidadOrdenes FROM CTE_RendimientoDiario ORDER BY PromedioPorOrden DESC FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)) AS DiaConMejorPromedioDeVenta,
                JSON_QUERY((SELECT TOP 1 DiaNombre AS Dia, SUM(DineroIngresado) AS AcumuladoHistorico, SUM(FlujoDeOrdenes) AS VolumenTotalOrdenes FROM CTE_RendimientoDiario GROUP BY DiaNombre ORDER BY AcumuladoHistorico DESC FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)) AS MejorDiaDeLaSemanaGeneral

             FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)) AS ResumenEstadisticoFechas

        FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
    );

    SELECT ISNULL(@ResultadoJSON, '{}') AS AnaliticaVentasMaestra;
END;


