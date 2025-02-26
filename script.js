// Función para cargar y mostrar la asistencia desde localStorage
function cargarAsistencia() {
    let asistencia = JSON.parse(localStorage.getItem("asistencia")) || [];
    let tbody = document.getElementById("tabla-asistencia");
    tbody.innerHTML = "";  // Limpiar la tabla antes de agregar los nuevos datos

    // Recorrer los registros de asistencia y agregar cada uno a la tabla
    asistencia.forEach(a => {
        let row = `<tr><td>${a.matricula}</td><td>${a.nombre}</td><td>${a.fecha}</td></tr>`;
        tbody.innerHTML += row;  // Agregar la fila a la tabla
    });

    // Mostrar u ocultar el botón de borrar asistencia dependiendo de si hay registros
    let boton = document.getElementById("borrar-asistencia");
    if (asistencia.length > 0) {
        boton.style.display = "block";  // Mostrar el botón si hay registros
    } else {
        boton.style.display = "none";  // Ocultar el botón si no hay registros
    }
}

// Función para registrar asistencia en localStorage
function registrarAsistencia(decodedText) {
    try {
        let data = JSON.parse(decodedText);  // Suponiendo que el código QR contiene un JSON
        let asistencia = JSON.parse(localStorage.getItem("asistencia")) || [];

        // Verificar si ya existe la matrícula en la lista de asistencia
        let existe = asistencia.some(a => a.matricula === data.matricula);
        if (existe) {
            alert("⚠️ Código ya escaneado. Este código ya ha sido escaneado previamente.");
            return;
        }

        // Asegurarse de que los datos no sean "undefined"
        let matricula = data.matricula || "Matrícula no especificada";
        let nombre = data.nombre || "Nombre no especificado";
        let fecha = new Date().toLocaleString();

        // Agregar los datos escaneados a la asistencia
        asistencia.push({
            matricula: matricula,
            nombre: nombre,
            fecha: fecha  // Obtener la fecha y hora actual
        });

        // Guardar la nueva lista de asistencia en localStorage
        localStorage.setItem("asistencia", JSON.stringify(asistencia));

        // Registrar el código escaneado
        registrarCodigoEscaneado(matricula);

        // Llamar a cargarAsistencia para actualizar la tabla
        cargarAsistencia();
    } catch (error) {
        console.error("Error al procesar el código QR: ", error);
    }
}

// Función para registrar el código escaneado y evitar duplicados
function registrarCodigoEscaneado(matricula) {
    let codigosEscaneados = JSON.parse(localStorage.getItem("codigosEscaneados")) || [];
    codigosEscaneados.push(matricula);
    localStorage.setItem("codigosEscaneados", JSON.stringify(codigosEscaneados));
}

// Función para verificar si el código QR es único
function verificarCodigoUnico(decodedText) {
    let data = JSON.parse(decodedText);  // Suponiendo que el código QR contiene un JSON
    let codigosEscaneados = JSON.parse(localStorage.getItem("codigosEscaneados")) || [];
    return !codigosEscaneados.includes(data.matricula);
}

// Función para borrar toda la asistencia registrada
function borrarAsistencia() {
    localStorage.removeItem("asistencia");  // Eliminar los registros de asistencia en localStorage
    cargarAsistencia();  // Actualizar la tabla después de borrar los datos
}

// Llamar a cargarAsistencia inicialmente para cargar los datos al abrir la página
cargarAsistencia();

// Actualizar el registro de asistencia cada 5 segundos
setInterval(cargarAsistencia, 5000);  // Actualización cada 5 segundos
