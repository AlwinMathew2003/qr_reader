from flask import Flask, request, jsonify,render_template


app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index1.html')

@app.route('/process_qr', methods=['POST'])
def process_qr():
    qr_data = request.json.get('qrData')
    if not qr_data:
        return jsonify({'error': 'No QR data received'}), 400

    print(f"QR Data Received: {qr_data}")

    # Example response simulating processing of QR code
    return jsonify({'status': 'success', 'message': 'QR data processed successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
