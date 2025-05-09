USE placas_db; 

-- Tablas en orden correcto
CREATE TABLE vehiculos (
    id int  NOT NULL AUTO_INCREMENT,
    marca varchar(100)  NULL,
    color varchar(50)  NULL,
    tipo varchar(50)  NULL,
    tipo_vehiculo varchar(50)  NOT NULL,
    CONSTRAINT vehiculos_pk PRIMARY KEY (id)
);

CREATE TABLE camaras (
    id int  NOT NULL AUTO_INCREMENT,
    ubicacion varchar(255)  NOT NULL,
    descripcion text  NULL,
    ip_camara varchar(20)  NOT NULL,
    created_at timestamp  NULL DEFAULT current_timestamp,
    CONSTRAINT camaras_pk PRIMARY KEY (id)
);

CREATE TABLE placas (
    id int  NOT NULL AUTO_INCREMENT,
    texto varchar(20)  NOT NULL,
    vehiculo_id int  NULL,
    fecha_hora datetime  NOT NULL DEFAULT current_timestamp,
    imagen_base64 longtext  NOT NULL,
    UNIQUE INDEX AK_0 (texto),
    CONSTRAINT placas_pk PRIMARY KEY (id)
);

CREATE TABLE detecciones (
    id int  NOT NULL AUTO_INCREMENT,
    placa_id int  NULL,
    camara_id int  NULL,
    fecha_hora datetime  NOT NULL DEFAULT current_timestamp,
    imagen_url text  NULL,
    confianza float  NULL,
    CONSTRAINT detecciones_pk PRIMARY KEY (id)
);

CREATE TABLE alertas (
    id int  NOT NULL AUTO_INCREMENT,
    deteccion_id int  NULL,
    tipo_alerta varchar(100)  NULL,
    mensaje text  NULL,
    fecha_alerta datetime  NULL DEFAULT current_timestamp,
    CONSTRAINT alertas_pk PRIMARY KEY (id)
);

-- Claves foráneas al final
ALTER TABLE placas ADD CONSTRAINT FK_0 
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos (id)
    ON DELETE SET NULL;

ALTER TABLE detecciones ADD CONSTRAINT FK_1 
    FOREIGN KEY (placa_id) REFERENCES placas (id)
    ON DELETE CASCADE;

ALTER TABLE detecciones ADD CONSTRAINT FK_2 
    FOREIGN KEY (camara_id) REFERENCES camaras (id)
    ON DELETE SET NULL;

ALTER TABLE alertas ADD CONSTRAINT FK_3 
    FOREIGN KEY (deteccion_id) REFERENCES detecciones (id)
    ON DELETE CASCADE;