
$(document).ready(function() {
    $('#updateForm').submit(function(event) {
        event.preventDefault();
        let oldEmployee = $('#oldEmployee').val();
        let newEmployee = $('#newEmployee').val();
            
        $.post('/actualizar_empleado', { oldEmployee, newEmployee }, function(response) {
            $('#message').html(`<div class="alert alert-success">${response.message}</div>`);
        }).fail(function() {
            $('#message').html('<div class="alert alert-danger">Error al actualizar el empleado.</div>');
        });
    });
});
