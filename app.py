import pyodbc # Conecta Py con DB de SQLServer
import logging # Registra eventos o errores en archivo log
from flask import Flask, jsonify, request, render_template, url_for # Flask(Crea app web), jsonify(Convierte respuestas en JSON), Request(Obtiene datos enviados al serv, como param URL), Render_template(Renderiza paginas HTML)
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import socket # Obtiene direcc IP del serv
import requests

app = Flask(__name__) # Inicializa app Flask, permite rutas y ejec el serv
app.secret_key = 'S@telite2801' # Clave secreta para proteger datos sensibles
CORS(app, origins=["http://localhost:5000"])

logging.basicConfig(
    filename="LOG_IMPRESION.log",  # Nombre del archivo de LOG
    level=logging.INFO, # Nivel de detalle del LOG
    format="%(asctime)s - %(levelname)s - %(message)s", # Formato de LOG
    datefmt="%Y-%m-%d %H:%M:%S", # Formato de fecha
)
logger = logging.getLogger(__name__) # Crea event logger para regis event


login_manager = LoginManager() # Crea objeto para manejar sesiones de usuario
login_manager.init_app(app) # Inicializa objeto con app Flask
login_manager.login_view = 'login' # Define ruta de login

# Función para conectar a SQL Server
CONNECTION_STR_FTDM07 = (
            r"Driver={SQL Server};" # Especif que usa driver odbc para conect a SQLServer
            r"Server=172.20.106.32;" # IP del equipo
            r"Database=RHProjects;" # DB con que consultar
            r"UID=itadmin;" # ID del user
            r"PWD=4dmin1T;" # PSW del user
        )

API_LDAP_URL = "http://172.20.96.4:9877/api/ActiveDirectory/AuthenticateUser" # URL de API LDAP para autenticar usuario

class User(UserMixin): # Clase para manejar usuarios
    def __init__(self, username, noemp, fullname, rol, email, usertype, area): # Constructor de la clase
        self.id = username # ID del usuario
        self.username = username # Nombre de usuario
        self.noemp = noemp # Número de empleado
        self.fullname = fullname # Nombre completo
        self.rol = rol # Rol del usuario
        self.email = email # Correo electrónico
        self.usertype = usertype # Tipo de usuario
        self.area = area # Área del usuario

# Carga usuario
@login_manager.user_loader 
def load_user(username):
    user_info = get_user_info(username) # Valida credenciales en BD
    if user_info['success']:
        return User(
            username=user_info['username'],
            noemp=user_info['noemp'],
            fullname=user_info['fullname'],
            rol=user_info['rol'],
            email=user_info['email'],
            usertype=user_info['usertype'],
            area=user_info['area']
        )
    return None

# !!!IMPORTANTE!!! --- Funcion para llamar a la DB de SQLServer

# Query: consult SQL o SP  # Params: param opc para consult # is_select: indica el tipo de consulta #is_stored_procedure: indica si es SP # srv: Nombre serv por defec
def run_query(query, params=None, is_select=True, is_stored_proc=False,srv ='FTDM07'):
    try: # Maneja errores y asig cadena conexion
        connection_string = CONNECTION_STR_FTDM07
        if not connection_string: # Si la cadena no esta def, arroja un mensaje
            raise ValueError(f"No se encontró la cadena de conexión para el servidor {srv}")
        
        # Establece conexi y crea cursor
        with pyodbc.connect(connection_string) as conn: # Conect SQLServer usando cadena def
            with conn.cursor() as cursor: # with: usa admin de contex para cerrar conex   # Cursor: crea cursor para ejec consulta SQL
                if is_stored_proc:
                    placeholders = ','.join(['?'] * len(params)) # ?: genera cant de marcad segun cantid de paramt
                    cursor.execute(f"{{CALL {query} ({placeholders})}}", params or ()) # CALL: eject proced con CALL y pasa paramt
                else:
                    cursor.execute(query, params or ()) # Si no es SP, ejec consulta SQL direc con param
                    
                if is_select or is_stored_proc: # Obtiene nombre de column(si hay result)
                    if cursor.description is not None:
                        columns = [column[0] for column in cursor.description] # columns: lista con nombre de las column
                        results = [dict(zip(columns, row)) for row in cursor.fetchall()] # cursor: obtiene todas filas de column  # dict: convierte cada fila en diccio
                        return {"success": True, "data": results}
                    else:
                        return {"success": True, "data": []}  # Devuelve una lista vacía si no hay resultados
                
                conn.commit()
                return {"success": True} # si no hay consult de selecc, confirma cambios con commit()
            
    # Manejo de errores y devuelve mensaje en LOG        
    except pyodbc.DatabaseError as db_err:
        logger.error(f"Database error in run_query: {query} | {params} | {db_err}")
        return {"success": False, "error": f"Database error: {str(db_err)}"}
    except pyodbc.Error as conn_err:
        logger.error(f"Connection error in run_query: {query} | {params} | {conn_err}")
        return {"success": False, "error": f"Connection error: {str(conn_err)}"}
    except Exception as e:
        logger.error(f"Unexpected error in run_query: {query} | {params} | {e}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


# Funciones de validación (ajusta según tu base de datos)
# def validate_user_credentials_DB(user, password, usertype):
#     # Placeholder: consulta a la base de datos para usuarios externos
#     query = "SELECT * FROM users WHERE username = ? AND password = ? AND usertype = ?"
#     result = run_query(query, (user, password, usertype))
#     if result['success'] and result['data']:
#         data = result['data'][0]
#         return{
#             "success": True,
#             "username": data['username'],
#             "noemp": data['noemp'],
#             "fullname": data['fullname'],
#             "rol": data['rol'],
#             "email": data['email'],
#             "usertype": data['usertype'],
#             "area": data['area']
#         }
#     return {"success": False}

def get_user_info(username):
    # Placeholder: consulta a la base de datos para obtener info del usuario
    query = "SELECT * FROM RH_USUARIOS WHERE Usuarios = ? AND Password = ?"
    result = run_query(query,(username,))
    if result['success'] and result['data']:
        data = result['data'][0]
        return{
            'success': True,
            "username": data['username'],
            "noemp": data['noemp'],
            "fullname": data['fullname'],
            "rol": data['rol'],
            "email": data['email'],
            "usertype": data['usertype'],
            "area": data['area']
        }
    return {"success": False}

@app.route('/api/valida_login', methods=['POST'])
def valida_login():
    data = request.get_json()
    try:
        user = data.get('user')
        password = data.get('password')
        auth_data = {"username": str(user).strip().lower(), "password": str(password)}

        # user_info = validate_user_credentials_DB(user, password, 'Externo')
        # if user_info['success']:
        #     user = User(**user_info)
        #     login_user(user)
        #     return jsonify(success=True, redirect_url=url_for('index'))
        
        response = requests.post(API_LDAP_URL, json=auth_data)
        if response.status_code == 200:
            user_info = response.json()
            if user_info['active']:
                # user_info = validate_user_credentials_DB(str(user).strip().lower())
                # if user_info['success']:
                #     user = User(**user_info)
                #     login_user(user)
                 return jsonify(success=True, redirect_url=url_for('index'))
            else:
                return jsonify(success=False, message="Usuario inactivo."), 403
        else:
            return jsonify(success=False, message=response.text.strip()), 401
    except Exception as e:
        logger.error(f"valida_login error: {e}")
        return jsonify(success=False, message=str(e))









#---------------------------------   API PARA OBTENER FOLIO  ---------------------------------#
# Ruta para obtener el número de empleado a partir del folio que aepta solic GET
@app.route('/api/obtenerEmpleadoPorFolio', methods=['GET'])
def obtener_empleado_por_folio():
    print('ENTRO AL METODO') # Mensaje para saber que se llamo al metodo
    folio = request.args.get('folio') # Obtiene el param folio de la URL
    if not folio or len(folio) != 9 or not folio.startswith("RHL25"):
        return jsonify({'error': 'Folio invalido, debe contener 9 caracteres y comenzar con RHL25'}), 400

    
    # Selecciona datos de 2 tablas unidas
    query = """--INFORMACION DE LAS PERSONAS A LAS QUE SE LES ENTREGO ETIQUETAS      
        SELECT A.Noemp,B.Nombre,B.Area,B.Sexo,B.Turno,A.Folio,A.FueEntregado, A.Activo AS Activo_folio, B.Activo AS Activo_empleado
        FROM RH_LOCKERS_RELACION_NOEMP_FOLIOS A
        JOIN TNMX_AsociadosActivos B ON A.Noemp = B.NoEmp
        WHERE A.Activo = 1 AND B.Activo = 'S' AND A.Folio = ?
        """
    # Usa join para combin datos de empleados activ

    empleado = run_query(query,(folio,)) # Ejec consult pasando folio como paramet
 
    if empleado['success']: # Si la consult fue exitosa
        empleado_data= empleado['data'] # Obtiene datos devueltos por la consult
    
    if empleado_data: # Si hay datos(si se encontro el folio)
        # devuelve datos en formato JSON
        return  jsonify({
            'numeroEmpleado': empleado_data[0]['Noemp'],
            'nombre': empleado_data[0]['Nombre'],
            'area': empleado_data[0]['Area'],
            'sexo': empleado_data[0]['Sexo'],
            'turno': empleado_data[0]['Turno'],
            'folio': empleado_data[0]['Folio'],
            'fueEntregado': empleado_data[0]['FueEntregado'],
            'activoEmpleado': empleado_data[0]['Activo_empleado'] == 'S'
        })
    else:
        return jsonify({'error': 'Folio no encontrado'}), 404 # Si no se encontro, devuelve un error



#---------------------------------   API PARA LLENAR TABLA  ---------------------------------#
@app.route('/api/informacionParaTabla', methods=['GET'])
def informacion_Para_Tabla():
    print('OBTENIENDO INFORMACION PARA LA TABLA')

    # Consulta SQL para obtener información de empleados con ese folio
    query = """
        SELECT A.Noemp, B.Nombre, B.Area, B.Sexo, B.Turno, A.Folio, A.FueEntregado, B.Activo 
        FROM RH_LOCKERS_RELACION_NOEMP_FOLIOS A
        JOIN TNMX_AsociadosActivos B ON A.Noemp = B.NoEmp
        WHERE A.Activo = 1 AND B.Activo = 'S' 
    """

    resultado = run_query(query)  # Ejecutar la consulta SQL
    # empleados = [{'numeroEmpleado':12345,'nombre':'fffff','folio':'RHLDDFFDDF','status':'Entregado'}]
    # return jsonify(empleados)
    if resultado['success']:  # Si la consulta fue exitosa
        datos = resultado['data']  # Obtener los datos

        if datos:  # Si hay datos en la respuesta
            # Convertimos la lista de resultados en formato JSON
            empleados = []
            for row in datos:

                status = 'Activo' if row ['Activo'] == 'S' else 'Inactivo'
                empleados.append({
                    'numeroEmpleado': row['Noemp'],
                    'nombre': row['Nombre'],
                    'folio': row['Folio'],
                    'status': status
                })
            return jsonify(empleados)
        else:
            return jsonify([])
    else:
        return jsonify({'error': 'Error en la consulta SQL'}), 500




# @app.route('api/actualizarEmpleado', methods=['GET'])
# def actualizar_empleados():
# print("EMPLEADO ACTUALIZADO")




















# Define la ruta principal del sitio web
@app.route('/templates/login.html/')
def login():
    return render_template('login.html')


@app.route('/templates/index.html/')
def index(): 
    return render_template('index.html') # Renderiza y muetra la plantilla HTML 'index.html'

@app.route('/templates/empleados.html/')
def pagina_empleados():
    return render_template('empleados.html')

@app.route('/templates/actualizar.html/')
def pagina_actualizaciones():
    return render_template('actualizar.html')


# Bloque para ejec Flask si el script se corre correctamente
if __name__ == '__main__':
    host_ip = socket.gethostbyname(socket.gethostname()) # Obtencion de IP del equipo
    print(f"Servidor funcionando en: http://{host_ip}:5000") # Imprime URL donde corre el serv
    app.run(debug=True, host='0.0.0.0') # Inicia el serv Flask en modo debug

