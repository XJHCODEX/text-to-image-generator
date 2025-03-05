from flask import Flask, jsonify, render_template, request, send_file
import requests
import io
import cx_Oracle
import base64
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_USER = os.getenv('username')
DB_PASS = os.getenv('password')
DB_DSN = os.getenv('DSN')

def get_db_connection():
    """Establish and return a database connection."""
    try:
        connection = cx_Oracle.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        print("Database connection successful")
        return connection
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Database connection failed: {error.message}")
        return None

api_key = os.getenv('api_key')
api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large"

headers = {'Authorization': f'Bearer {api_key}'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    prompt = request.form.get('prompt', '').strip()
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        # Generate image
        data = {"inputs": prompt}
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        print(f"API response status: {response.status_code}")

        if response.status_code != 200:
            return jsonify({"error": f"API error: {response.text}"}), response.status_code

        image_data = response.content
        print("Image data received from API")

        # Store in database
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            cursor = connection.cursor()
            image_id_var = cursor.var(cx_Oracle.NUMBER)
            cursor.execute("""
                INSERT INTO generated_images (prompt, image_data)
                VALUES (:prompt, :image_data)
                RETURNING id INTO :id
            """, {
                'prompt': prompt,
                'image_data': image_data,
                'id': image_id_var
            })
            image_id_value = image_id_var.getvalue()
            print(f"image_id_value: {image_id_value}")

        # Delete older images if more than 10 exist
            cursor.execute("""
                DELETE FROM generated_images
                WHERE id NOT IN (
                    SELECT id FROM generated_images
                    ORDER BY created_at DESC
                    FETCH FIRST 10 ROWS ONLY
                )
            """)
            connection.commit()
            print("Limited database to last 10 images")

            if image_id_value is None:
                raise Exception("Database did not return an ID")
            image_id = image_id_value[0]  # This is where NoneType error could occur
            print(f"Inserted image ID: {image_id}")
            connection.commit()
        except Exception as e:
            print(f"Database operation failed: {str(e)}")
            raise  # Re-raise to catch in outer try-except
        finally:
            cursor.close()
            connection.close()

        return send_file(
            io.BytesIO(image_data),
            mimetype='image/png',
            as_attachment=False
        )

    except Exception as e:
        print(f"Server error in generate_image: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/previous_images", methods=["GET"])
def get_previous_images():
    """Fetch the last 5 generated images from the database."""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, prompt, image_data FROM generated_images
            ORDER BY created_at DESC FETCH FIRST 10 ROWS ONLY
        """)
        rows = cursor.fetchall()
        print(f"Rows fetched: {len(rows)}")
        
        images = []
        for row in rows:
            # Convert cx_Oracle.LOB to bytes
            lob_data = row[2]  # image_data is a LOB object
            if lob_data is None:
                print(f"Skipping row {row[0]}: No image data")
                continue
            image_bytes = lob_data.read()  # Read LOB into bytes
            # Convert bytes to base64 string
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            images.append({
                "id": row[0],
                "prompt": row[1],
                "image_url": f"data:image/png;base64,{image_base64}"
            })
        
        return jsonify({"images": images})
    
    except Exception as e:
        print(f"Error in get_previous_images: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)