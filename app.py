from flask import Flask, request, jsonify
import os
import requests
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuración
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def get_ai_response(user_message):
    """Obtiene respuesta de OpenAI para preguntas sobre juegos"""
    if not OPENAI_API_KEY:
        return get_fallback_response(user_message)
    
    system_prompt = """Eres GameBuddy, un amigo robot divertido para niños de 10 años que aman Roblox y Minecraft.

🎮 ROBLOX:
- Adopt Me, Brookhaven, Pet Simulator X
- Tips para monedas y objetos raros
- Seguridad online y no compartir datos

⛏️ MINECRAFT:
- Construcciones paso a paso
- Trucos de supervivencia  
- Proyectos creativos para niños

🎯 ESTILO:
- Lenguaje simple y divertido
- Usa emojis 🎮⛏️✨🏠
- Sé entusiasta y positivo
- Explica como a un amigo
- Responde en español

¡Sé creativo y seguro! ¡Diviértete!"""
    
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ],
        'temperature': 0.8,
        'max_tokens': 500
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return get_fallback_response(user_message)
            
    except Exception as e:
        return get_fallback_response(user_message)

def get_fallback_response(user_message):
    """Respuestas cuando OpenAI no está disponible"""
    user_lower = user_message.lower()
    
    # Respuestas predefinidas
    if any(word in user_lower for word in ['hola', 'hi', 'hello']):
        return """¡Hola! 👋 Soy GameBuddy, tu amigo robot de juegos! 🎮

Pregúntame sobre:
• 🏠 Construcciones en Minecraft
• 🎯 Trucos en Roblox  
• 💡 Ideas creativas
• ⛏️ Supervivencia en Minecraft

¿En qué puedo ayudarte? ✨"""
    
    elif 'minecraft' in user_lower:
        return """¡Minecraft! ⛏️ Te ayudo con:

🏠 **CONSTRUCCIONES:**
• Casas modernas paso a paso
• Castillos medievales
• Granjas automáticas
• Bases subterráneas

🌳 **SUPERVIVENCIA:**
• Cómo encontrar diamantes rápido
• Consejos para la primera noche
• Combate contra mobs
• Encantamientos útiles

🔴 **REDSTONE BÁSICA:**
• Puertas automáticas
• Sistemas simples
• Trampas divertidas

¿Qué quieres construir o aprender? 🎨"""
    
    elif 'roblox' in user_lower:
        return """¡Roblox! 🎮 Hablemos de:

🎪 **JUEGOS POPULARES:**
• Adopt Me - Cuidar mascotas
• Brookhaven - Vida virtual
• Pet Simulator X - Mascotas gigantes
• Tower of Hell - Parkour difícil

💰 **CONSEGUIR MONEDAS:**
• Misiones diarias
• Minijuegos dentro de los juegos
• Trucos legales para avanzar

👥 **JUGAR CON AMIGOS:**
• Juegos cooperativos divertidos
• Cómo unirse a partidas
• Crear grupos privados

¿De qué juego quieres hablar? 🎯"""
    
    elif any(word in user_lower for word in ['constru', 'casa', 'edificio', 'build']):
        return """¡Construcciones! 🏠 Te doy ideas:

🎯 **PARA PRINCIPIANTES:**
1. Casa básica de madera (5x5)
2. Granja de animales simple
3. Torre de observación

🏰 **PARA AVANZADOS:**
• Castillo con murallas
• Casa moderna con vidrio
• Base secreta subterránea
• Puente colgante

💡 **IDEAS CREATIVAS:**
• Casa en un árbol gigante
• Templo en la jungla
• Barco pirata
• Estación espacial

¿Qué tipo de construcción te gustaría? 🎨"""
    
    else:
        return """¡Interesante! 🤔 Soy GameBuddy, especialista en:

🎮 **ROBLOX** - Adopt Me, Brookhaven, Pet Simulator X
⛏️ **MINECRAFT** - Construcciones, supervivencia, redstone
💡 **IDEAS CREATIVAS** - Proyectos divertidos

Pregúntame específicamente sobre:
• "¿Cómo construyo una casa moderna en Minecraft?"
• "¿Qué es Adopt Me en Roblox?"
• "Dame un desafío de construcción"
• "¿Cómo encuentro diamantes rápido?"

¡Estoy aquí para ayudarte! ✨"""

@app.route('/')
def home():
    return "🤖 Game Buddy Bot - ACTIVO 24/7 🎮"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibe mensajes de Telegram"""
    try:
        data = request.get_json()
        logging.info(f"📨 Mensaje recibido: {data}")
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text:
                logging.info(f"👤 Chat {chat_id}: {text}")
                
                # Obtener respuesta
                response = get_ai_response(text)
                
                # Enviar respuesta a Telegram
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                telegram_data = {
                    'chat_id': chat_id,
                    'text': response,
                    'parse_mode': 'HTML'
                }
                
                requests.post(url, json=telegram_data, timeout=10)
                logging.info("✅ Respuesta enviada")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logging.error(f"❌ Error en webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/set-webhook', methods=['GET'])
def set_webhook():
    """Configurar webhook en Telegram - EJECUTAR UNA VEZ"""
    try:
        # Obtener URL base de Render
        render_url = os.getenv('RENDER_EXTERNAL_URL')
        if not render_url:
            return "❌ RENDER_EXTERNAL_URL no configurada"
        
        webhook_url = f"{render_url}/webhook"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
        response = requests.post(url, json={'url': webhook_url})
        result = response.json()
        
        logging.info(f"Webhook response: {result}")
        
        if result.get('ok'):
            return f"✅ Webhook configurado correctamente!<br>URL: {webhook_url}"
        else:
            return f"❌ Error configurando webhook: {result}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route('/test', methods=['GET'])
def test():
    """Página de prueba"""
    return """
    <h1>🤖 Game Buddy Bot</h1>
    <p>El bot está funcionando correctamente! 🎮</p>
    <p><a href="/set-webhook">Configurar Webhook</a></p>
    <p>Para probar el bot, envía un mensaje a tu bot en Telegram.</p>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
