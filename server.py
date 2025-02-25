from flask import Flask, request, render_template_string, jsonify
import json
import logging
import hmac
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Secreto compartido con Mercado Pago (deberías obtenerlo de variables de entorno)
MP_SECRET = os.environ.get("MP_WEBHOOK_SECRET", "tu_clave_secreta")

# Lista para almacenar las últimas notificaciones recibidas (en memoria)
# En producción deberías usar una base de datos
notifications_history = []
MAX_HISTORY = 10

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
        
        # Guardar la notificación en el historial
        notification_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data,
            "headers": dict(request.headers)
        }
        notifications_history.insert(0, notification_entry)
        
        # Mantener solo las últimas MAX_HISTORY notificaciones
        if len(notifications_history) > MAX_HISTORY:
            notifications_history.pop()
        
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
        
        # Devolver respuesta de éxito
        return jsonify({"status": "success", "message": "Notificación procesada correctamente"})
        
    except Exception as e:
        logging.error(f"Error procesando webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/webhook/view", methods=["GET"])
def webhook_view():
    """Página para visualizar las notificaciones recibidas"""
    return render_template_string("""
        <html>
            <head>
                <title>Monitor de Webhook Mercado Pago</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                    h1 { color: #2d3748; }
                    .notification { 
                        background: #f8f9fa; 
                        border: 1px solid #dee2e6; 
                        border-radius: 5px; 
                        padding: 15px; 
                        margin-bottom: 20px; 
                    }
                    .timestamp { 
                        font-size: 0.8em; 
                        color: #6c757d; 
                        margin-bottom: 10px; 
                    }
                    pre { 
                        background: #f1f3f5; 
                        padding: 10px; 
                        border-radius: 3px; 
                        overflow-x: auto; 
                    }
                    .empty-state {
                        text-align: center;
                        padding: 40px;
                        color: #6c757d;
                    }
                    .header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .refresh-btn {
                        padding: 8px 15px;
                        background: #4361ee;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                    .refresh-btn:hover {
                        background: #3a56d4;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Monitor de Webhook de Mercado Pago</h1>
                    <button class="refresh-btn" onclick="location.reload()">Actualizar</button>
                </div>
                <p>Esta página muestra las últimas notificaciones recibidas en el webhook.</p>
                
                {% if notifications %}
                    <h2>Últimas {{ notifications|length }} notificaciones:</h2>
                    {% for notification in notifications %}
                        <div class="notification">
                            <div class="timestamp">Recibido: {{ notification.timestamp }}</div>
                            <h3>Datos de la notificación:</h3>
                            <pre>{{ notification.data|tojson(indent=4) }}</pre>
                            <h3>Encabezados:</h3>
                            <pre>{{ notification.headers|tojson(indent=4) }}</pre>
                        </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-state">
                        <h2>No se han recibido notificaciones</h2>
                        <p>Las notificaciones aparecerán aquí cuando Mercado Pago envíe datos a tu webhook.</p>
                    </div>
                {% endif %}
            </body>
        </html>
    """, notifications=notifications_history)

@app.route("/", methods=["GET"])
def home():
    """Página de inicio con información sobre el servicio"""
    return render_template_string("""
        <html>
            <head>
                <title>Webhook para Mercado Pago</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
                    h1 { color: #2d3748; }
                    .card { 
                        background: #fff; 
                        border-radius: 8px; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
                        padding: 20px; 
                        margin-bottom: 20px; 
                    }
                    .btn {
                        display: inline-block;
                        padding: 10px 15px;
                        background: #4361ee;
                        color: white;
                        text-decoration: none;
                        border-radius: 4px;
                        margin-right: 10px;
                    }
                    .btn:hover {
                        background: #3a56d4;
                    }
                    code {
                        background: #f1f3f5;
                        padding: 2px 5px;
                        border-radius: 3px;
                    }
                </style>
            </head>
            <body>
                <h1>Servicio de Webhook para Mercado Pago</h1>
                
                <div class="card">
                    <h2>Estado</h2>
                    <p>✅ El servicio está activo y funcionando correctamente.</p>
                    <a href="/webhook/view" class="btn">Ver notificaciones recibidas</a>
                </div>
                
                <div class="card">
                    <h2>Información del servicio</h2>
                    <p>Este servicio está configurado para recibir notificaciones de Mercado Pago a través de webhooks.</p>
                    <ul>
                        <li><strong>URL del webhook:</strong> <code>{{ request.host_url }}webhook</code></li>
                        <li><strong>Monitor de notificaciones:</strong> <code>{{ request.host_url }}webhook/view</code></li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2>Cómo probar</h2>
                    <p>Para enviar una notificación de prueba al webhook, puedes usar cURL:</p>
                    <pre>curl -X POST {{ request.host_url }}webhook \
-H "Content-Type: application/json" \
-d '{"type":"transfer","data":{"id":"12345","amount":1000}}'</pre>
                </div>
            </body>
        </html>
    """)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)