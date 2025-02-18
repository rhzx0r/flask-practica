from flask import Flask, jsonify, request, abort, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def to_dict(self):
        """Convierte el objeto Usuario a un diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email
        }

# Crear la base de datos y las tablas
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Renderiza la interfaz de usuario."""
    return render_template('index.html')

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    """Obtiene todos los usuarios."""
    usuarios = Usuario.query.all()
    return jsonify([usuario.to_dict() for usuario in usuarios])

@app.route('/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    """Obtiene un usuario por su ID."""
    usuario = Usuario.query.get_or_404(id, description="Usuario no encontrado")
    return jsonify(usuario.to_dict())

@app.route('/usuarios', methods=['POST'])
def create_usuario():
    """Crea un nuevo usuario."""
    data = request.get_json()
    if not data or not 'nombre' in data or not 'email' in data:
        abort(400, description="Faltan datos obligatorios: nombre y email")

    nombre = data['nombre']
    email = data['email']

    # Verificar si el email ya existe
    if Usuario.query.filter_by(email=email).first():
        abort(400, description="El email ya está registrado")

    nuevo_usuario = Usuario(nombre=nombre, email=email)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario creado exitosamente"}), 201

@app.route('/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    """Actualiza un usuario existente."""
    data = request.get_json()
    if not data or not 'nombre' in data or not 'email' in data:
        abort(400, description="Faltan datos obligatorios: nombre y email")

    nombre = data['nombre']
    email = data['email']

    usuario = Usuario.query.get_or_404(id, description="Usuario no encontrado")

    # Verificar si el nuevo email ya está registrado por otro usuario
    if Usuario.query.filter(Usuario.email == email, Usuario.id != id).first():
        abort(400, description="El email ya está registrado")

    usuario.nombre = nombre
    usuario.email = email
    db.session.commit()

    return jsonify({"mensaje": "Usuario actualizado exitosamente"})

@app.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    """Elimina un usuario por su ID."""
    usuario = Usuario.query.get_or_404(id, description="Usuario no encontrado")
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario eliminado exitosamente"})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
