
tabla_centros_hospitalarios  = """
                                CREATE TABLE CentrosHospitalarios (
                                id SERIAL PRIMARY KEY,
                                ncodi FLOAT
                                );
                                """

tabla_anios = """CREATE TABLE Años (
                id SERIAL PRIMARY KEY,
                año INT NOT NULL UNIQUE
                );
               """


tabla_tipo_hospi = """
                   CREATE TABLE TipoHospitalizacion (
                   id SERIAL PRIMARY KEY,
                   tipo_hospitalizacion VARCHAR(20) NULL UNIQUE
                   );
                   """

tabla_gastos = """
                CREATE TABLE Gastos (
                    id SERIAL PRIMARY KEY,
                    año_id INT REFERENCES Años(id),
                    centro_id INT REFERENCES CentrosHospitalarios(id),
                    totalcompra FLOAT,
                    producfarma FLOAT,
                    materialsani FLOAT,
                    implantes FLOAT,
                    restomateriasani FLOAT,
                    servcontratado FLOAT,
                    trabajocontratado FLOAT,
                    xrestocompras FLOAT,
                    variaexistencias FLOAT,
                    servexteriores FLOAT,
                    sumistro FLOAT,
                    xrestoserviexter FLOAT,
                    gastopersonal FLOAT,
                    sueldos FLOAT,
                    indemnizacion FLOAT,
                    segsocempresa FLOAT,
                    otrgassocial FLOAT,
                    dotaamortizacion FLOAT,
                    perdidadeterioro FLOAT,
                    xrestogasto FLOAT,
                    totcompragasto FLOAT
                );
                """


tabla_ingresos = """
                CREATE TABLE Ingresos (
                    id SERIAL PRIMARY KEY,
                    particulares FLOAT,
                    aseguradoras FLOAT,
                    aseguradoras_enfermedad FLOAT,
                    aseguradoreas_trafico FLOAT,
                    mutuas FLOAT, 
                    año_id INT REFERENCES Años(id),
                    centro_id INT REFERENCES CentrosHospitalarios(id),
                    tipo_id INT REFERENCES TipoHospitalizacion(id)
                );
                """