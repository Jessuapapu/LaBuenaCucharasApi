CREATE PROC ListarClientes
	@NombreCliente NVARCHAR(100) = NULL
	
AS 
BEGIN
	SET NOCOUNT ON;
	DECLARE @IdCliente INT

	-- Encontrar el Id del cliente por el nombre
	IF @NombreCliente IS NOT NULL
		BEGIN
			SET @IdCliente = (SELECT C.IdCliente FROM clientes C WHERE @NombreCliente = C.NombreCliente)
			
			IF @IdCliente IS NULL
				BEGIN
					PRINT 'USUARIO NO ENCONTRADO'
					RETURN 1;
				END
		END

	SELECT c.IdCliente, C.NombreCliente, CD.Dirreccion,CC.CorreoElectronico,CT.Telefono FROM Clientes C
	INNER JOIN clientetelefono CT ON C.IdCliente = CT.IdCliente
	INNER JOIN clientedireccion CD ON C.IdCliente = CD.IdCliente
	INNER JOIN clientecorreo CC ON C.IdCliente = CC.IdCliente
	WHERE C.IdCliente = IIF(@IdCliente IS NOT NULL, @IdCliente, C.IdCliente)
END

