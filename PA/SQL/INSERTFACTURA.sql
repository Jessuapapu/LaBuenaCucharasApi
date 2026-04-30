CREATE PROC GenerarFactura
    @PayloadJson NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON; 

    BEGIN TRY
        BEGIN TRANSACTION;

        DECLARE @Fecha DATETIME2 = JSON_VALUE(@PayloadJson, '$.fecha');
        DECLARE @Estado NVARCHAR(50) = JSON_VALUE(@PayloadJson, '$.Estado');
        DECLARE @NuevoIdFactura INT;
        DECLARE @MontoCalculado DECIMAL(18,2);
        DECLARE @CantidadTotal INT;

        -- Al crear la tabla temporal, la columna se llama IdOrdenes
        SELECT IdOrdenes
        INTO #OrdenesTemporales
        FROM OPENJSON(@PayloadJson, '$.detalles')
        WITH (
            IdOrdenes INT '$.IdOrden'
        );

        SELECT @MontoCalculado = SUM(CostoTotal) 
        FROM ordenes 
        WHERE IdOrdenes IN (SELECT IdOrdenes FROM #OrdenesTemporales);
        
        SELECT @CantidadTotal = SUM(CantidadPlatillo)
        FROM detallesordenes
        WHERE IdOrdenes IN (SELECT IdOrdenes FROM #OrdenesTemporales)

        INSERT INTO facturas (Fecha, Estado, MontoTotal,CantidadTotal)
        VALUES (@Fecha, @Estado, ISNULL(@MontoCalculado, 0), @CantidadTotal);

        SET @NuevoIdFactura = SCOPE_IDENTITY();

        INSERT INTO facturasordenes (IdFactura, IdOrdenes)
        -- CORRECCIÓN: Aquí debes llamar a IdOrdenes, que es el nombre en la tabla temporal
        SELECT @NuevoIdFactura, IdOrdenes
        FROM #OrdenesTemporales;

        COMMIT TRANSACTION;

        SELECT @NuevoIdFactura AS IdFacturaGenerada;

    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
