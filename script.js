
function confirmarRegreso() {
    var confirmación = confirm("¿Estás seguro que desea cerrar sesión?");
    if (confirmación) {
        window.location.href = "/templates/login.html";
    }
}

function iniciarEscaneo() {

    document.getElementById("qr-scan").classList.add("move-down");


    html5QrCode = new Html5Qrcode("reader");
    html5QrCode.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: 300 },
        onScanSuccess
    );
}

function onScanSuccess(decodedText) {
    console.log("Código Escaneado: " + decodedText);
    obtenerNumeroEmpleado(decodedText);

    if (validarCodigoQR(decodedText)) {
        mostrarConfirmacion("✅ Escaneado con éxito", "El folio ha sido procesado correctamente.");
        setTimeout(() => {
            iniciarEscaneo();
        }, 5000);
    } else {
        mostrarConfirmacion("⚠️ Código inválido", "El código QR no tiene 9 caracteres o no comienza con 'RHL'.");
        setTimeout(() => {
            iniciarEscaneo();
        }, 5000);
    }
}

function validarCodigoQR(decodedText) {
    return decodedText.length === 9 && decodedText.startsWith("RHL");
}

function obtenerNumeroEmpleado(folio) {
    fetch(`/api/obtenerEmpleadoPorFolio?folio=${folio}`)
        .then(response => response.json())
        .then(data => {
            console.table(data);
            if (data.error) {
                console.log(data.error);
            } else {
                let numeroEmpleado = data.numeroEmpleado;
                document.getElementById("form-container").style.display = 'block';
                document.getElementById("txtStatus").value = data.activoEmpleado ? "Activo" : "Inactivo";
                document.getElementById("txtNoEmp").value = data.numeroEmpleado;
                document.getElementById("txtNombre").value = data.nombre;
            }
        })
        .catch(error => {
            console.error("Error al obtener el número de empleado:", error);
        });
}

document.getElementById("startScanButton").addEventListener("click", function() {
    iniciarEscaneo();
});