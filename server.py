from flask import Flask, request, render_template_string
import json

app = Flask(__name__)

# Ruta para recibir el webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        # Obtener los datos de la solicitud JSON
        data = request.get_json()

        # Mostrar los datos en la web de manera legible
        return render_template_string("""
            <html>
                <body>
                    <h1>Datos recibidos del Webhook</h1>
                    <pre>{{ data }}</pre>
                    <h2>Datos formateados:</h2>
                    <pre>{{ formatted_data }}</pre>
                </body>
            </html>
        """, data=json.dumps(data, indent=4), formatted_data=data)

    return "Método no permitido", 405

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
