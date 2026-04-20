CREATE PROC InsertaCliente 
	@Nombre NVARCHAR(100),
	@Dirreccion NVARCHAR(100),
	@Telefono NVARCHAR(20),
	@Correo NVARCHAR(100)

	
AS 
BEGIN
	
	IF @Nombre IS NULL
		BEGIN
			PRINT 'ERROR INGRESE UN NOMBRE AL CLIENTE'
			RETURN 1;
		END


	INSERT INTO clientes (NombreCliente) VALUES (@Nombre);
	
	DECLARE @IdCliente INT;
	
	-- Obtener id del cliente que se acaba de agregar
	SET @IdCliente = (SELECT MAX(IdCliente) FROM clientes)

	-- VALIDAR SI CORREO FUE INGRESADO
	IF @Correo IS NOT NULL
		BEGIN
			INSERT INTO clientecorreo (IdCliente, CorreoElectronico) VALUES (@IdCliente, @Correo)
		END
	
	ELSE
		BEGIN
			PRINT 'NO SE PUDO AGREGAR EL CORREO AL CLIENTE'
		END

	-- VALIDAR SI EL TELEFONO FUE INGRESADO
	IF @Telefono IS NOT NULL
		BEGIN
			INSERT INTO clientetelefono (IdCliente, Telefono) VALUES (@IdCliente, @Telefono)
		END
	
	ELSE
		BEGIN
			PRINT 'NO SE PUDO AGREGAR EL CORREO AL CLIENTE'
		END


	-- VALIDAR SI LA DIRRECCION FUE INGRESADO
	IF @Dirreccion IS NOT NULL
		BEGIN
			INSERT INTO clientedireccion (IdCliente, Dirreccion) VALUES (@IdCliente, @Dirreccion)
		END
	
	ELSE
		BEGIN
			PRINT 'NO SE PUDO AGREGAR EL CORREO AL CLIENTE'
		END
	
	
	
	PRINT 'SE HA INGRESADO CORRECTAMENTE LOS VALORES DEL CLIENTE'
	RETURN 0;

END

