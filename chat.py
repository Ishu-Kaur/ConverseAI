import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Input
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import os
import random
import re

# --- FINAL, CORRECTED MODEL LOADING AND REBUILDING (ROBUST METHOD) ---

print("Loading FINAL trained model and tokenizer...")
model_path = os.path.join('saved_models', 'seq2seq_model_final.keras')
tokenizer_path = os.path.join('saved_models', 'tokenizer_final.pickle')

# Load assets
training_model = load_model(model_path)
with open(tokenizer_path, 'rb') as handle:
    tokenizer = pickle.load(handle)
print("Assets loaded successfully.")

# --- Get parameters from the loaded model ---
max_input_length = training_model.input_shape[0][1]
max_response_length = training_model.input_shape[1][1]
# Get the LSTM units from the Decoder LSTM (layer 4)
lstm_units = training_model.layers[4].units 

# --- Reconstruct the Encoder Model by reusing trained layers ---
encoder_inputs = training_model.input[0]
# The Encoder LSTM is layer [3]. We need its outputs (the states).
_, state_h_enc, state_c_enc = training_model.layers[3].output 
encoder_states = [state_h_enc, state_c_enc]
encoder_model = Model(encoder_inputs, encoder_states)

# --- Reconstruct the Decoder Model using the CORRECT indices ---
decoder_inputs = Input(shape=(1,))
decoder_state_input_h = Input(shape=(lstm_units,), name="decoder_state_h")
decoder_state_input_c = Input(shape=(lstm_units,), name="decoder_state_c")
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]

# Get the trained layers using the indices from YOUR model summary
decoder_embedding_layer = training_model.layers[2]
decoder_lstm_layer = training_model.layers[4]      # Correct index is 4
decoder_dense_layer = training_model.layers[5]     # Correct index is 5

# Connect the layers to build the inference graph
decoder_embedding = decoder_embedding_layer(decoder_inputs)
decoder_outputs_and_states = decoder_lstm_layer(
    decoder_embedding, initial_state=decoder_states_inputs
)
decoder_outputs = decoder_outputs_and_states[0]
decoder_states = decoder_outputs_and_states[1:]
decoder_outputs = decoder_dense_layer(decoder_outputs)

# THE FIX IS HERE: We convert the tuple 'decoder_states' to a list
decoder_model = Model(
    [decoder_inputs] + decoder_states_inputs,
    [decoder_outputs] + list(decoder_states)
)
print("Inference models built successfully.")

# Reverse-lookup token index to decode sequences back to text
reverse_word_index = {v: k for k, v in tokenizer.word_index.items()}


# --- Advanced Decoding with Beam Search ---
def decode_sequence_beam(input_seq, beam_width=3):
    states_value = encoder_model.predict(input_seq, verbose=0)
    start_token_index = tokenizer.word_index['<start>']
    
    beams = [([start_token_index], 0.0, states_value)]
    
    for _ in range(max_response_length):
        all_candidates = []
        for seq, score, states in beams:
            if seq[-1] == tokenizer.word_index.get('<end>'):
                all_candidates.append((seq, score, states))
                continue

            target_seq = np.array([[seq[-1]]])
            
            output_tokens, h, c = decoder_model.predict([target_seq] + states, verbose=0)
            
            word_probabilities = output_tokens[0, -1, :]
            top_next_indices = np.argsort(word_probabilities)[-beam_width:]
            
            for word_index in top_next_indices:
                new_seq = seq + [word_index]
                new_score = score - np.log(word_probabilities[word_index] + 1e-9)
                all_candidates.append((new_seq, new_score, [h, c]))
                
        beams = sorted(all_candidates, key=lambda x: x[1])[:beam_width]
        
        if all(b[0][-1] == tokenizer.word_index.get('<end>') for b in beams):
            break
            
    best_seq = beams[0][0]
    decoded_sentence = ''
    for token_index in best_seq:
        word = reverse_word_index.get(token_index)
        if word and word not in ['<start>', '<end>', '<unk>']:
            decoded_sentence += ' ' + word
            
    return decoded_sentence.strip()


# --- THE DEFINITIVE CONVERSATION MANAGER (with Greeting Logic) ---
def get_final_response(user_input, conversation_state):
    user_input_lower = user_input.lower()
    
    # Rule 1: Handle Greetings
    greetings = [r'\bhello\b', r'\bhi\b', r'\bhey\b', r'good morning', r'good afternoon']
    if any(re.search(pattern, user_input_lower) for pattern in greetings):
        responses = ["Hello! How can I help you today?", "Hi there! What can I do for you?", "Hello, thanks for reaching out. How may I assist?"]
        return random.choice(responses), "general"

    # Rule 2: Handle Farewells
    if any(word in user_input_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
        return "Thank you for chatting with me. Goodbye!", "general"

    # Rule 3: Handle awaiting_email state
    elif conversation_state == "awaiting_email":
        if re.search(r'\S+@\S+', user_input):
            return "Thank you. I have your contact information now. How can I assist you further?", "has_email"
        else:
            return "I'll need a valid email address to proceed. Could you please provide it?", "awaiting_email"
    
    # Rule 4: Handle awaiting_order_number state
    elif conversation_state == "awaiting_order_number":
        match = re.search(r'\d{5,}', user_input)
        if match:
            order_number = match.group(0)
            return f"Thank you. I've looked up order number {order_number} and it is currently out for delivery.", "has_email"
        else:
            return "I'm sorry, that doesn't look like a valid order number. It should be at least 5 digits long.", "awaiting_order_number"

    # Rule 5: Handle awaiting_flight_info state
    elif conversation_state == "awaiting_flight_info":
        if "yes" in user_input_lower:
            confirmation_number = random.randint(10000, 99999) 
            return f"Your flight has been successfully cancelled. Your confirmation number is {confirmation_number}.", "has_email"
        else:
            return "Cancellation has been aborted. Is there anything else I can help with?", "has_email"

    # Rule 6: If we have an email, check for our keywords
    elif conversation_state == "has_email":
        if "order" in user_input_lower:
            return "I can help with that. Could you please provide your order number?", "awaiting_order_number"
        elif "flight" in user_input_lower or "cancel" in user_input_lower:
            return "I can certainly help with that. Are you sure you want to cancel your flight? Please respond with 'yes' to confirm.", "awaiting_flight_info"
        
    # Rule 7: If no specific rules apply, THEN use the AI model
    input_seq = pad_sequences(tokenizer.texts_to_sequences([user_input]), maxlen=max_input_length, padding='post')
    model_response = decode_sequence_beam(input_seq)
    
    # This is the line with the fixed typo
    new_state = conversation_state
    if conversation_state == "general" and ('email' in model_response or 'dm' in model_response or 'direct message' in model_response):
        new_state = "awaiting_email"
        
    return model_response, new_state


# --- The Terminal Chat Loop ---
if __name__ == '__main__':
    current_conversation_state = "general" 
    
    print("\n--- Chatbot is Ready (Terminal Mode) ---")
    print("Type your message and press Enter. Type 'quit' to exit.")
    
    while True:
        try: # Add a try-except block to catch any unexpected errors during chat
            user_input = input("You: ")
            
            if user_input.lower() == 'quit':
                print("Bot: Goodbye!")
                break
                
            response, new_state = get_final_response(user_input, current_conversation_state)
            
            current_conversation_state = new_state
            
            print(f"Bot: {response}")
        except Exception as e:
            print(f"An error occurred: {e}")
            break