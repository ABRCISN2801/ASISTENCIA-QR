// dataTables.js

$(document).ready(function() {
    var table = $("#table").DataTable({
        "ajax": {
            "url": "http://10.121.98.72:5000/api/informacionParaTabla",
            "type": "GET",
            "dataSrc": ""
        },
        "columns": [
            { "data": "numeroEmpleado" },
            { "data": "folio" },
            { "data": "nombre" },
            { "data": "status" }
        ],
        "responsive": true,
        
            
    });
});
