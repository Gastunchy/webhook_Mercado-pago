from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Ruta para recibir el webhook
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        # Obtener los datos de la solicitud JSON
        data = request.get_json()

        # Mostrar los datos en la web
        return render_template_string("""
            <html>
                <body>
                    <h1>Datos recibidos del Webhook</h1>
                    <pre>{{ data }}</pre>
                </body>
            </html>
        """, data=data)  # Renderiza los datos como JSON en la página

    return "Método no permitido", 405

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
