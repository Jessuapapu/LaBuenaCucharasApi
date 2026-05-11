CREATE PROC MostrarCantidadDeImagenes
	@IdPlatillo INT = NULL
AS 
BEGIN
	 
	SELECT P.IdPlatillo, P.NombrePlatillo, COUNT(IPS.IdImagen) AS CANTIDAD_IMAGENES FROM platillos P
	LEFT JOIN imagenesplatillos IPS ON P.IdPlatillo = IPS.IdPlatillo
	WHERE (@IdPlatillo IS NULL OR P.IdPlatillo = @IdPlatillo)
	GROUP BY P.IdPlatillo, P.NombrePlatillo
END