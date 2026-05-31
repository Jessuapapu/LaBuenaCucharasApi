CREATE PROC DetallesAbastIngredientes
	@IdRegistro INT
AS
BEGIN
    SELECT 
        (SELECT * FROM detallesregistroinsumos WHERE IdRegistroAbastecimiento = @IdRegistro FOR JSON PATH) AS Insumos,
        (SELECT * FROM detallesregistroingredientes WHERE IdRegistroAbastecimiento = @IdRegistro FOR JSON PATH) AS Ingredientes
    FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
END