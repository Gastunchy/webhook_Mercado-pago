from flask import Flask, request, render_template_string, jsonify
import json
import logging
import hmac
import hashlib
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Secreto compartido con Mercado Pago (deberías obtenerlo de variables de entorno)
MP_SECRET = os.environ.get("MP_WEBHOOK_SECRET", "tu_clave_secreta")

def verify_webhook_signature(request_data, signature, secret):
    """Verifica la firma del webhook de Mercado Pago"""
    if not signature:
        return False
    
    calculated_signature = hmac.new(
        secret.encode('utf-8'),
        request_data,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(calculated_signature, signature)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Obtener los datos crudos y la firma
        request_data = request.get_data()
        signature = request.headers.get('X-Signature')
        
        # Verificar la firma (esto dependerá de cómo Mercado Pago implementa la verificación)
        # Nota: Ajusta esto según la documentación específica de Mercado Pago
        # if not verify_webhook_signature(request_data, signature, MP_SECRET):
        #     logging.warning("Firma de webhook inválida")
        #     return jsonify({"error": "Firma inválida"}), 403
        
        # Obtener los datos JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos JSON no encontrados"}), 400
            
        # Registrar la notificación recibida
        logging.info(f"Webhook recibido: {json.dumps(data)[:100]}...")
        
        # Procesar según el tipo de notificación
        notification_type = data.get('type')
        if notification_type == 'payment':
            # Procesar un pago
            payment_data = data.get('data', {})
            # Aquí implementarías tu lógica de negocio para procesar el pago
            logging.info(f"Pago procesado: ID {payment_data.get('id')}")
        elif notification_type == 'transfer':
            # Procesar una transferencia
            transfer_data = data.get('data', {})
            # Aquí implementarías tu lógica para procesar la transferencia
            logging.info(f"Transferencia procesada: ID {transfer_data.get('id')}")
        
        # Si es una solicitud para ver los datos en el navegador, mostrar la interfaz
        if request.headers.get('Accept', '').startswith('text/html'):
            query_params = request.args.to_dict()
            return render_template_string("""
                <html>
                    <head>
                        <title>Webhook Mercado Pago</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 20px; }
                            pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
                        </style>
                    </head>
                    <body>
                        <h1>Datos recibidos del Webhook de Mercado Pago</h1>
                        <h2>Datos en el cuerpo de la solicitud:</h2>
                        <pre>{{ data }}</pre>
                        <h2>Parámetros de la URL:</h2>
                        <pre>{{ query_params }}</pre>
                    </body>
                </html>
            """, data=json.dumps(data, indent=4), query_params=query_params)
        
        # Si es una solicitud API, devolver JSON
        return jsonify({"status": "success", "message": "Notificación procesada correctamente"})
        
    except Exception as e:
        logging.error(f"Error procesando webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    """Página simple para verificar que el servicio está funcionando"""
    return "Servicio de webhook para Mercado Pago activo"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
