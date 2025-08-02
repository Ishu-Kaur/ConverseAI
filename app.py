from flask import Flask, request, jsonify, render_template, session
import os
from chat import get_final_response

app = Flask(__name__)
app.secret_key = 'a_super_secret_key_for_your_chatbot' 

@app.route("/")
def home():
    session['conversation_state'] = 'general'
    return render_template("index.html")

@app.route("/get")
def chatbot_response():
    user_text = request.args.get('msg')
    current_state = session.get('conversation_state', 'general')
    response, new_state = get_final_response(user_text, current_state)
    session['conversation_state'] = new_state
    return jsonify(response)

def create_template_if_needed():
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    html_path = 'templates/index.html'
    print("Creating/Updating 'templates/index.html' with new design...")
    
    # --- THIS IS THE NEW HTML/CSS/JS WITH ALL THE DESIGN UPGRADES ---
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Chatbot</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <!-- 1. Import a nicer font from Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600&display=swap" rel="stylesheet">
    <style>
        /* --- Base Dark Theme --- */
        body { 
            background-color: #121212;
            color: #e0e0e0; 
            /* 2. Apply the new font */
            font-family: 'Nunito', sans-serif; 
            font-size: 16px;
        }
        .chat-container { 
            max-width: 700px; 
            margin: 30px auto; 
            border: 1px solid #333;
            box-shadow: 0 0 20px rgba(0,0,0,0.7);
            border-radius: 15px;
            overflow: hidden; /* Important for border-radius on children */
        }
        .card-header { 
            background-color: #1f1f1f;
            color: #00aaff;
            font-weight: 600;
            font-size: 1.2rem;
            border-bottom: 1px solid #333;
        }
        .chatbox { 
            height: 500px; /* Increased height */
            overflow-y: auto; 
            padding: 20px; 
            background-color: #1e1e1e;
            /* 3. Add smooth scrolling behavior */
            scroll-behavior: smooth;
        }
        .card-footer { 
            background-color: #1f1f1f;
            border-top: 1px solid #333;
            padding: 15px;
        }
        .form-control {
            background-color: #2c2c2c;
            color: white;
            border: 1px solid #444;
            border-radius: 20px;
        }
        .form-control:focus {
            background-color: #333;
            color: white;
            border-color: #007bff;
            box-shadow: 0 0 5px rgba(0,123,255,0.5);
        }
        .btn-primary {
            border-radius: 20px;
            /* 4. Add transition for hover effects */
            transition: all 0.2s ease-in-out;
        }
        .btn-primary:hover {
            transform: scale(1.05);
            box-shadow: 0 0 10px rgba(0,123,255,0.7);
        }

        /* --- Chat Bubble & Avatar Styling --- */
        .msg-container {
            margin-bottom: 20px;
            /* 5. Add a fade-in animation for new messages */
            animation: fadeIn 0.5s ease-in-out;
        }
        .user-msg, .bot-msg { 
            display: flex; 
            align-items: flex-end; 
        }
        .user-msg { justify-content: flex-end; }
        .bot-msg { justify-content: flex-start; }
        .msg-bubble { 
            padding: 12px 18px; 
            border-radius: 20px; 
            max-width: 80%; 
        }
        .user-bubble { 
            background-color: #007bff;
            color: white; 
            border-bottom-right-radius: 5px; 
        }
        .bot-bubble { 
            background-color: #3a3a3a;
            color: #f1f1f1;
            border-bottom-left-radius: 5px; 
        }
        /* 6. Avatar Styles */
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-size: cover;
            background-position: center;
            flex-shrink: 0; /* Prevents avatar from shrinking */
        }
        .user-avatar {
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="white" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>');
            margin-left: 10px;
        }
        .bot-avatar {
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="lightblue" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-12h2v4h-2v-4zm0 6h2v2h-2v-2z"/></svg>');
            margin-right: 10px;
        }

        /* --- Animation Keyframes --- */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* 7. Animated Typing Indicator */
        #typing-indicator .bot-bubble span {
            display: inline-block;
            animation: pulse 1.4s infinite;
        }
        #typing-indicator .bot-bubble span:nth-child(2) { animation-delay: 0.2s; }
        #typing-indicator .bot-bubble span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes pulse {
            0%, 60%, 100% { transform: scale(1); }
            30% { transform: scale(1.3); }
        }

        /* 8. Custom Scrollbar for Webkit Browsers (Chrome, Edge, Safari) */
        .chatbox::-webkit-scrollbar { width: 8px; }
        .chatbox::-webkit-scrollbar-track { background: #1e1e1e; }
        .chatbox::-webkit-scrollbar-thumb { background-color: #555; border-radius: 4px; border: 2px solid #1e1e1e; }
        .chatbox::-webkit-scrollbar-thumb:hover { background-color: #007bff; }
    </style>
</head>
<body>
    <div class="container chat-container card">
        <div class="card-header text-center">
            Customer Support Chatbot
        </div>
        <div class="card-body chatbox" id="chatbox">
            <div class="msg-container bot-msg">
                <div class="avatar bot-avatar"></div>
                <div class="msg-bubble bot-bubble">Hello! How can I help you today?</div>
            </div>
        </div>
        <div class="card-footer">
            <div class="input-group">
                <input type="text" class="form-control" id="userInput" placeholder="Type your message here..." autocomplete="off">
                <div class="input-group-append">
                    <button class="btn btn-primary" id="sendBtn">Send</button>
                </div>
            </div>
        </div>
    </div>

    <!-- The JavaScript has been updated to use the new HTML structure with avatars -->
    <script>
        function sendMessage() {
            var userInput = $("#userInput").val();
            if (userInput.trim() === "") { return; }

            // 9. Updated HTML for user message with avatar
            var userHtml = '<div class="msg-container user-msg"><div class="msg-bubble user-bubble">' + userInput + '</div><div class="avatar user-avatar"></div></div>';
            $("#chatbox").append(userHtml);
            $("#userInput").val("");
            $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight);

            // 10. Updated HTML for animated typing indicator
            var typingHtml = '<div class="msg-container bot-msg" id="typing-indicator">' +
                             '<div class="avatar bot-avatar"></div>' +
                             '<div class="msg-bubble bot-bubble">' +
                             '<span>.</span><span>.</span><span>.</span>' +
                             '</div></div>';
            $("#chatbox").append(typingHtml);
            $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight);

            $.get("/get", { msg: userInput }).done(function(data) {
                $("#typing-indicator").remove();
                
                // 11. Updated HTML for bot response with avatar
                var botHtml = '<div class="msg-container bot-msg"><div class="avatar bot-avatar"></div><div class="msg-bubble bot-bubble">' + data + '</div></div>';
                $("#chatbox").append(botHtml);
                $("#chatbox").scrollTop($("#chatbox")[0].scrollHeight);
            });
        }

        $("#userInput").keypress(function(e) { if(e.which == 13) sendMessage(); });
        $("#sendBtn").click(function() { sendMessage(); });
    </script>
</body>
</html>
    """
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    create_template_if_needed()
    
    # Get the port number from the environment variable Render provides.
    # Default to 5000 for local development.
    port = int(os.environ.get("PORT", 5000))
    
    print("\n--- Starting Flask Web Server ---")
    print(f"Server will run on host 0.0.0.0 and port {port}")
    # Tell the app to listen on all network interfaces and on the specified port.
    app.run(host="0.0.0.0", port=port)