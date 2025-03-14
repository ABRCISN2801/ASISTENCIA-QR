document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Evita que el formulario se envíe de forma tradicional

    // Obtén los valores del formulario
    const user = document.getElementById('user').value;
    const psw = document.getElementById('psw').value;

    // Envía los datos al endpoint de Flask
    fetch('/api/valida_login', { // Ajusta esta URL según tu backend
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user: user, password: psw })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.success) {
            // Redirige si todo es correcto
            window.location.href = data.redirect_url;
        } else {
            // Muestra una alerta de error con SweetAlert2
            Swal.fire({
                icon: 'error',
                title: 'Login failed',
                text: data.message || 'Invalid username or password'
            });
        }
    })
    .catch(error => {
        // Muestra una alerta en caso de error en la petición
        Swal.fire({
            icon: 'error',
            title: 'An error occurred',
            text: 'Please try again later'
        });
        console.error('Error:', error);
    });
});