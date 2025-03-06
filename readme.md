# Text to Image Generator

![Project Screenshot](assets/project-preview.png)


This project is a web application that generates images from text prompts using the Stable Diffusion 3.5 Large model via the Hugging Face API. It stores generated images in an Oracle database, limits the storage to the 10 most recent images, and provides a frontend interface to generate and download images.

## Features
- Generate images from text prompts using Stable Diffusion 3.5 Large.
- Store up to 10 most recent images in an Oracle database (older images are automatically deleted).
- Display the latest generated image and previous images with hover-activated download buttons.
- Responsive frontend with a clean user interface.

## Tech Stack
- **Backend**: Flask (Python), cx_Oracle for database interaction
- **Frontend**: HTML, CSS, JavaScript
- **External API**: Hugging Face Inference API (Stable Diffusion 3.5 Large)
- **Database**: Oracle Database
- **Environment Management**: `python-dotenv` for secure configuration

## Prerequisites
- Python 3.8+
- Oracle Database instance (configured with a `generated_images` table)
- Hugging Face API key
- Git (optional, for cloning the repository)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd text-to-image-generator
```

### 2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies 
```bash
pip install flask requests cx_Oracle python-dotenv
```

### 4. Configure Environment Variables
Create a .env file in the project root with the following content:
```bash
username=`<your-oracle-username>`
password=`<your-oracle-password>`
DSN=`<your-oracle-dsn>`
api_key=`<your-hugging-face-api-key>`
```

Replace the placeholders with your actual credentials and API key.

* Oracle DSN Example: (description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-ashburn-1.oraclecloud.com))(connect_data=(service_name=<your-service-name>))(security=(ssl_server_dn_match=yes)))

* Hugging Face API Key: Obtain from Hugging Face.

### 5. Set Up the Database
Create a table named generated_images in your Oracle database:
```bash
CREATE TABLE generated_images (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    prompt VARCHAR2(255) NOT NULL,
    image_data BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
### 6. Directory Structure
Ensure your project directory looks like this:
```bash
text-to-image-generator/
├── static/
│   └── styles.css    # CSS for frontend styling
├── templates/
│   └── index.html   # Frontend HTML
├── .env             # Environment variables
├── app.py           # Flask application
└── README.md        # This file
```

### Running the Application
1. Activate the virtual environment:
```bash
source venv/bin/activate 
```

2. Start the Flask server:
```bash
python app.py
```

3.  Open a web browser and navigate to:
```bash
127.0.0.1:5002
```
## Usage
1. Generate an Image:
* Enter a text prompt in the input field (e.g., "A futuristic city at night").
* Click "Generate Image" to create and display the image.
2. Download Images:
* Hover over the generated image or any previous image to reveal a "Download" button.
* Click the button to download the image as a PNG file.
3. View Previous Images:
* The "Previous Creations" section displays the 10 most recent images stored in the database.

## API Endpoints
* GET /: Renders the main page (index.html).
* POST /generate: Generates an image from a text prompt and stores it in the database.
    * Request: multipart/form-data with prompt field.
    * Response: PNG image file or JSON error.
* GET /previous_images: Retrieves the 10 most recent images from the database.
    * Response: JSON array of image objects (id, prompt, image_url).

## Frontend Details
* HTML: Located in templates/index.html.
* CSS: Located in static/styles.css (includes hover effect for download buttons).
* JavaScript: Handles form submission, image fetching, and dynamic display.

## Troubleshooting
* Database Connection Failed: Verify .env credentials and DSN.
* API Error: Check the Hugging Face API key and ensure the model endpoint is active.
* Images Not Displaying: Ensure the database table exists and has the correct schema.
## Limitations
* Limited to 10 images in the database due to automatic deletion of older entries.
* Dependent on Hugging Face API availability and rate limits.
## Contributing
Feel free to fork this repository, submit issues, or create pull requests with improvements.

## License
This project is licensed under the MIT License.