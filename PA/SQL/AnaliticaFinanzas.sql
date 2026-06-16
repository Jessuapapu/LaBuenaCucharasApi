CREATE PROC pa_Analitica_Finanzas
    @FechaInicio DATETIME = NULL,
    @FechaFin DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        -- Dinero total que pasó por el sistema (incluyendo errores y pendientes)
        ISNULL(SUM(CostoTotal), 0) AS IngresoBrutoTotal,
        
        -- Dinero real del que ya se entregó el producto
        ISNULL(SUM(CASE WHEN Estado IN ('ENTREGADO', 'PREPARADO') THEN CostoTotal ELSE 0 END), 0) AS IngresoNetoReal,
        
        -- Fuga financiera total por platos cancelados o mal digitados
        ISNULL(SUM(CASE WHEN Estado IN ('ANULADO', 'ANULADA', 'CANCELADO', 'CANCELADA') THEN CostoTotal ELSE 0 END), 0) AS DineroPerdidoAnulaciones,
        
        -- Dinero bloqueado en mesas que siguen consumiendo o pedidos sin cerrar
        ISNULL(SUM(CASE WHEN Estado = 'PENDIENTE' THEN CostoTotal ELSE 0 END), 0) AS CapitalFlotantePendiente,
        
        -- Cantidad bruta de transacciones caídas
        SUM(CASE WHEN Estado IN ('ANULADO', 'ANULADA', 'CANCELADO', 'CANCELADA') THEN 1 ELSE 0 END) AS TotalOrdenesAnuladas
    FROM ordenes
    WHERE (@FechaInicio IS NULL OR Fecha >= @FechaInicio) 
      AND (@FechaFin IS NULL OR Fecha <= @FechaFin);
END;
