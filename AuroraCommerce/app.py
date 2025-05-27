import os
import logging
from flask import Flask, render_template, request, jsonify
from chatbot import AuroraChatbot

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "aurora-secret-key-2024")

# Initialize the Aurora chatbot
aurora_bot = AuroraChatbot()

@app.route('/')
def index():
    """Main chatbot interface"""
    categories = aurora_bot.get_categories()
    return render_template('index.html', categories=categories)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message'].strip()
        use_rag = data.get('use_rag', False)
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get response from Aurora chatbot
        response_data = aurora_bot.get_response(user_message, use_rag=use_rag)
        
        return jsonify(response_data)
    
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'I apologize, but I\'m experiencing technical difficulties. Please try again.',
            'response': 'Sorry, I encountered an error while processing your request.',
            'source': 'error'
        }), 500

@app.route('/api/categories')
def get_categories():
    """Get available question categories"""
    try:
        categories = aurora_bot.get_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        logging.error(f"Error getting categories: {str(e)}")
        return jsonify({'categories': []}), 500

@app.route('/api/category_questions')
def get_category_questions():
    """Get questions for a specific category"""
    try:
        category = request.args.get('category', '').strip()
        if not category:
            return jsonify({'error': 'No category provided'}), 400
        
        questions = aurora_bot.get_category_questions(category)
        return jsonify({'questions': questions})
    
    except Exception as e:
        logging.error(f"Error getting category questions: {str(e)}")
        return jsonify({'questions': []}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html', categories=aurora_bot.get_categories()), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html', categories=aurora_bot.get_categories()), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
