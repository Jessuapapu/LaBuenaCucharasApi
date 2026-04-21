CREATE PROC ActualizarCliente
	@IdCliente INT = null,
	@NombreCliente NVARCHAR(100) = null,
	@NombreClienteCambio NVARCHAR(100) = null,
	@Correo NVARCHAR(100) = null,
	@Telefono NVARCHAR(20) = null,
	@Dirreccion NVARCHAR(100) = NULL,

	@CorreoCambio NVARCHAR(100) = null,
	@TelefonoCambio NVARCHAR(20) = null,
	@DirreccionCambio NVARCHAR(100) = NULL
AS
BEGIN
	IF @IdCliente IS NULL AND @NombreCliente IS NULL
		BEGIN
			PRINT 'DEBE COLOCAR AL MENOS UN IDENTIDICADOR DEL CLIENTE'
			RETURN 1;
		END

	IF @IdCliente IS NULL
		BEGIN

			SET @IdCliente = (SELECT C.IdCliente FROM clientes C WHERE @NombreCliente = C.NombreCliente)

			IF @IdCliente IS NULL
				BEGIN
					PRINT 'USUARIO NO ENCONTRADO'
					RETURN 1;
				END
		END

	-- Validar datos a cambiar
	IF @Correo IS NULL AND @CorreoCambio IS NOT NULL
		BEGIN
			PRINT 'DEBE INGRESAR EL CORREO QUE QUIERE CAMBIAR DEL CLIENTE'
		END

	IF @Telefono IS NULL AND @TelefonoCambio IS NOT NULL
		BEGIN
			PRINT 'DEBE INGRESAR EL NUMERO TELEFONICO QUE QUIERE CAMBIAR DEL CLIENTE'
		END

	IF @Dirreccion IS NULL AND @DirreccionCambio IS NOT NULL
		BEGIN
			PRINT 'DEBE INGRESAR LA DIRRECCION QUE QUIERE CAMBIAR DEL CLIENTE'
		END


	-- UPDATES VALIDADAS
	IF @NombreCliente IS NOT NULL
		BEGIN
			UPDATE clientes
			SET NombreCliente = @NombreClienteCambio
			WHERE IdCliente = @IdCliente
		END

	IF @TelefonoCambio IS NOT NULL
		BEGIN
			UPDATE clientetelefono
			SET Telefono = @TelefonoCambio
			WHERE IdCliente = @IdCliente
		END

	IF @DirreccionCambio IS NOT NULL
		BEGIN
			UPDATE clientedireccion 
			SET Dirreccion = @DirreccionCambio
			WHERE IdCliente = @IdCliente
		END

	IF @CorreoCambio IS NOT NULL
		BEGIN
			UPDATE clientecorreo
			SET CorreoElectronico = @CorreoCambio
			WHERE IdCliente = @IdCliente
		END

END